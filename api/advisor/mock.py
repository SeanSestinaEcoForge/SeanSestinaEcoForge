"""MOCK advisor: deterministic, rule-based suggestions from the pilot thresholds.

No network, no key, same input -> same output. Labeled MOCK everywhere it appears.
"""
from .safety import feed_increase_blockers

SOURCE = 'MOCK rule set (api/advisor/mock.py) over configs/pilot-v2.json thresholds; not Grok output'

# Canned, intentionally unsafe suggestions used only to demonstrate the safety layer.
SAFETY_DEMO = [
    {'action': 'feed_rate', 'value': 25, 'reason': 'MOCK canned unsafe suggestion (safety-layer demo): triple the feed'},
    {'action': 'aeration', 'value': 'off', 'reason': 'MOCK canned unsafe suggestion (safety-layer demo): save power by stopping air'},
    {'action': 'dose', 'value': 'sodium bicarbonate 50 g', 'reason': 'MOCK canned unsafe suggestion (safety-layer demo): dose buffer'},
    {'action': 'water_temp_setpoint', 'value': 30, 'reason': 'MOCK canned unsafe suggestion (safety-layer demo): warm the water'},
    {'action': 'circulation', 'value': 'stop', 'reason': 'MOCK canned unsafe suggestion (safety-layer demo): pause the pump'},
]


def suggest(state, lim):
    v = {k: r['value'] for k, r in lim.items() if isinstance(r, dict) and 'value' in r}
    out = []

    def add(action, value, reason):
        out.append({'action': action, 'value': value, 'reason': reason, 'source': SOURCE})

    for key, label in [('DO_mg_L', 'dissolved oxygen'), ('TAN_mg_L', 'TAN'), ('nitrite_mg_L', 'nitrite'),
                       ('pH', 'pH'), ('temp_C', 'water temperature')]:
        if state.get(key) is None:
            add('manual_test', f'Measure {label}', f'{label} is unknown; unknown is never treated as healthy')

    do, tan, no2 = state.get('DO_mg_L'), state.get('TAN_mg_L'), state.get('nitrite_mg_L')
    ph, kh, temp = state.get('pH'), state.get('KH_mg_L'), state.get('temp_C')
    feed = state.get('feed_g_day')
    pause = None
    if do is not None and do <= v['DO_critical_mg_L']:
        add('aeration', 'backup_on', f'DO {do} mg/L at or below critical {v["DO_critical_mg_L"]}: force backup aeration')
        pause = f'DO critical ({do} mg/L)'
    elif do is not None and do <= v['DO_warning_mg_L']:
        add('aeration', 'backup_on', f'DO {do} mg/L at or below warning {v["DO_warning_mg_L"]}: backup aeration on')
    if tan is not None and tan >= v['TAN_alarm_mg_L']:
        pause = pause or f'TAN {tan} at or above alarm {v["TAN_alarm_mg_L"]}'
        add('manual_test', 'Spot-test TAN, DO, pH and KH', 'TAN alarm: confirm with a manual test before acting')
    if no2 is not None and no2 >= v['nitrite_alarm_mg_L']:
        pause = pause or f'nitrite {no2} at or above alarm {v["nitrite_alarm_mg_L"]}'
        add('manual_test', 'Spot-test nitrite and confirm the kit reporting basis (as N or as ion)',
            'Nitrite alarm; protocol basis is unconfirmed')
    if pause:
        add('feed_rate', 0, f'Pause feeding pending manual confirmation: {pause}')
    if ph is not None and not v['pH_alarm_low'] <= ph <= v['pH_alarm_high']:
        add('manual_test', 'Test KH first', f'pH {ph} outside {v["pH_alarm_low"]}–{v["pH_alarm_high"]}')
        add('manual_review', 'Correct pH manually after the KH result; log it', 'Protocol: no automatic dosing')
    if kh is not None and kh < v['KH_alarm_mg_L']:
        add('manual_review', 'Review bicarbonate addition manually (no dose amount suggested)',
            f'KH {kh} mg/L CaCO3 below {v["KH_alarm_mg_L"]}')
    lo, hi = lim['temp_range_C']['value']
    if temp is not None and not lo <= temp <= hi:
        add('water_temp_setpoint', min(hi, max(lo, temp)), f'Water {temp} °C outside pilot range {lo}–{hi} °C')
    for vessel, level in sorted((state.get('water_levels_pct') or {}).items()):
        if level <= v['level_critical_pct']:
            add('circulation', 'keep_on', f'{vessel} level {level}% critical: keep core circulation and aeration on backup power')
            add('manual_review', f'Attended top-up / leak check on {vessel}', 'Critical level; no automatic makeup water')
        elif level <= v['level_low_pct']:
            add('manual_review', f'Attended top-up on {vessel}', f'{vessel} level {level}% at or below {v["level_low_pct"]}%')
    if state.get('heartbeat_stale'):
        add('manual_review', 'Check stale sensor(s): power, Wi-Fi, probe', 'More than 2 heartbeat intervals missing')
    if not pause:
        blockers = feed_increase_blockers(state, lim)
        if feed is not None:
            why = ('Hold feed: ' + '; '.join(blockers)) if blockers else \
                'No threshold breach; hold feed (no auto-ramp; a ramp step needs clean spot tests and manual review)'
            add('feed_rate', feed, why)
    if not out:
        add('manual_review', 'Keep logging; no threshold breach in the supplied state', 'All supplied values inside thresholds')
    return out
