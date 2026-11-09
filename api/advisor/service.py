"""Advisor orchestration: pick mode, gather suggestions, run every one through the safety layer."""
from . import live, mock
from .safety import ACTIONS, check, limits

CONTROL_MODE = 'ADVISORY ONLY: suggestions are never executed; a human decides and acts'


def safety_limits():
    return limits()


def advise(state, mode='mock', model=None, include_safety_demo=False, post=None):
    lim = limits()
    notice, mode_used, raw = None, 'mock', None
    if mode == 'live':
        try:
            kwargs = {'post': post} if post else {}
            raw = live.suggest(state, lim, ACTIONS, model=model, **kwargs)
            mode_used = 'live'
        except live.LiveUnavailable as exc:
            notice = f'LIVE mode unavailable ({exc}); fell back to MOCK rules'
    if raw is None:
        raw = mock.suggest(state, lim)
    if include_safety_demo:
        raw = raw + [dict(s, source='MOCK canned safety-layer demo') for s in mock.SAFETY_DEMO]
    checked = [check(s, state, lim) for s in raw]
    counts = {k: sum(s['safety_status'] == k for s in checked) for k in ('ALLOWED', 'CLAMPED', 'BLOCKED')}
    return {
        'label': 'MOCK' if mode_used == 'mock' else 'LIVE',
        'label_note': ('MOCK: deterministic rules, not Grok output' if mode_used == 'mock'
                       else 'LIVE: Grok suggestions, safety-checked; inputs keep their own labels'),
        'mode_requested': mode, 'mode_used': mode_used,
        'model': live.model_name(model) if mode_used == 'live' else None,
        'notice': notice, 'control_mode': CONTROL_MODE, 'executed': False,
        'state_used': state, 'safety_counts': counts, 'suggestions': checked,
        'limits_source': 'configs/pilot-v2.json (labels and sources in GET /advisor/limits)',
    }
