"""Caution-first safety layer for advisor suggestions.

Hard-coded rules, limits read from configs/pilot-v2.json (QUOTED/ASSUME labels kept).
Every suggestion is ALLOWED, CLAMPED or BLOCKED, with reasons. The layer is the same for
mock and live mode: a suggestion from Grok gets no more trust than a canned one.
Nothing here actuates anything; results always carry ``executed: False``.
"""
import logging
import math

from ..configuration import load_config, values

log = logging.getLogger('ecoforge.advisor.safety')

ACTIONS = ('feed_rate', 'aeration', 'circulation', 'water_temp_setpoint', 'manual_test', 'manual_review', 'dose')
SAFE_AERATION = ('keep_on', 'backup_on')
SAFE_CIRCULATION = ('keep_on',)
MAX_TEXT = 300


def limits(c=None):
    """Return safety limits with their config labels and sources."""
    c = c or load_config()
    a, f = c['alarms'], c['fish']
    temp = c['request_policy']['temperature_range_C']

    def rec(r):
        return {k: r[k] for k in ('value', 'unit', 'label', 'source') if k in r}
    return {
        'feed_cap_g_day': rec(f['feed_cap_g_day']),
        'feed_ramp_g_week': rec(f['feed_ramp_g_week']),
        'temp_range_C': rec(temp),
        'DO_warning_mg_L': rec(a['DO_warning_mg_L']),
        'DO_critical_mg_L': rec(a['DO_critical_mg_L']),
        'TAN_alarm_mg_L': rec(a['TAN_alarm_mg_L']),
        'nitrite_alarm_mg_L': rec(a['nitrite_alarm_mg_L']),
        'pH_alarm_low': rec(a['pH_alarm_low']),
        'pH_alarm_high': rec(a['pH_alarm_high']),
        'KH_alarm_mg_L': rec(a['KH_alarm_mg_L']),
        'level_low_pct': rec(a['level_low_pct']),
        'level_critical_pct': rec(a['level_critical_pct']),
        'feed_ramp_policy': c['startup']['feed_ramp'],
        'hard_rules': [
            'Advisor only: nothing is actuated, dosed, fed, messaged or purchased.',
            'Aeration never stops; core circulation is never stopped by software.',
            'No chemical dose amounts: dosing suggestions are blocked; KH/pH correction stays manual.',
            'Feed never above the cap; increases only by one weekly ramp step, only with complete, '
            'non-alarming DO/TAN/nitrite data and fresh heartbeats, and only after manual review.',
            'Temperature setpoints are clamped to the pilot range.',
            'Unknown action types are blocked.',
        ],
    }


def _num(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return None
    return float(x) if math.isfinite(x) else None


def feed_increase_blockers(state, lim):
    """Reasons a feed increase is not allowed now (missing data counts as a blocker)."""
    v = {k: r['value'] for k, r in lim.items() if isinstance(r, dict) and 'value' in r}
    out = []
    do, tan, no2 = state.get('DO_mg_L'), state.get('TAN_mg_L'), state.get('nitrite_mg_L')
    if do is None:
        out.append('DO unknown')
    elif do <= v['DO_warning_mg_L']:
        out.append(f"DO {do} mg/L at or below warning {v['DO_warning_mg_L']}")
    if tan is None:
        out.append('TAN unknown')
    elif tan >= v['TAN_alarm_mg_L']:
        out.append(f"TAN {tan} at or above alarm {v['TAN_alarm_mg_L']}")
    if no2 is None:
        out.append('nitrite unknown')
    elif no2 >= v['nitrite_alarm_mg_L']:
        out.append(f"nitrite {no2} at or above alarm {v['nitrite_alarm_mg_L']} (basis unconfirmed)")
    if state.get('heartbeat_stale') is not False:
        out.append('heartbeat stale or unknown')
    return out


def check(suggestion, state, lim=None):
    """Validate one suggestion. Returns a new dict with status, final value and reasons."""
    lim = lim or limits()
    s = dict(suggestion)
    action = s.get('action')
    proposed = s.get('value')
    reasons, status, final = [], 'ALLOWED', proposed

    if action not in ACTIONS:
        status, final = 'BLOCKED', None
        reasons.append(f'Unknown action {action!r}; only {", ".join(ACTIONS)} are recognized')
    elif action == 'dose':
        status, final = 'BLOCKED', None
        reasons.append('No automatic or advised dose amounts. Spot-test KH/pH and decide manually (protocol: correct manually and log).')
    elif action == 'aeration':
        if proposed not in SAFE_AERATION:
            status, final = 'BLOCKED', 'keep_on'
            reasons.append('Aeration never stops (hard rule). Only keep_on/backup_on are accepted.')
    elif action == 'circulation':
        if proposed not in SAFE_CIRCULATION:
            status, final = 'BLOCKED', 'keep_on'
            reasons.append('Software never stops core circulation; dry-run risk needs a hard alarm and manual confirmation.')
    elif action == 'water_temp_setpoint':
        x = _num(proposed)
        lo, hi = lim['temp_range_C']['value']
        if x is None:
            status, final = 'BLOCKED', None
            reasons.append('Temperature setpoint must be a finite number in °C')
        elif not lo <= x <= hi:
            status, final = 'CLAMPED', min(hi, max(lo, x))
            reasons.append(f'Clamped {x} °C to pilot range {lo}–{hi} °C ({lim["temp_range_C"]["label"]})')
    elif action == 'feed_rate':
        x = _num(proposed)
        cap = lim['feed_cap_g_day']['value']
        step = lim['feed_ramp_g_week']['value']
        current = _num(state.get('feed_g_day'))
        if x is None:
            status, final = 'BLOCKED', current
            reasons.append('Feed rate must be a finite number in g/day')
        else:
            final = x
            if final < 0:
                final, status = 0.0, 'CLAMPED'
                reasons.append('Negative feed clamped to 0 g/day')
            if final > cap:
                final, status = float(cap), 'CLAMPED'
                reasons.append(f'Above feed cap; clamped to {cap} g/day ({lim["feed_cap_g_day"]["label"]})')
            if current is None and final > 0:
                status, final = 'BLOCKED', None
                reasons.append('Current feed rate unknown; cannot verify a safe change')
            elif current is not None and final > current:
                blockers = feed_increase_blockers(state, lim)
                if blockers:
                    status, final = 'BLOCKED', current
                    reasons.append('Feed increase blocked; hold current rate: ' + '; '.join(blockers))
                elif final > current + step:
                    final, status = current + step, 'CLAMPED'
                    reasons.append(f'Increase limited to one ramp step (+{step} g/day per week, {lim["feed_ramp_g_week"]["label"]})')
                if status != 'BLOCKED':
                    reasons.append('Any increase needs clean spot tests and manual review first (startup policy)')
    else:  # manual_test / manual_review: text only
        if not isinstance(proposed, str):
            status, final = 'BLOCKED', None
            reasons.append('Manual items must be text')
        elif len(proposed) > MAX_TEXT:
            final, status = proposed[:MAX_TEXT], 'CLAMPED'
            reasons.append(f'Text truncated to {MAX_TEXT} characters')

    if status == 'ALLOWED' and not reasons:
        reasons.append('Within hard limits')
    if status != 'ALLOWED':
        log.warning('advisor suggestion %s: action=%r proposed=%r final=%r reasons=%s',
                    status, action, proposed, final, ' | '.join(reasons))
    s.update(proposed_value=proposed, final_value=final, safety_status=status, safety_reasons=reasons,
             executed=False, requires_human_confirmation=True)
    s.pop('value', None)
    return s
