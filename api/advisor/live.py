"""LIVE advisor: asks Grok (xAI Responses API, POST /v1/responses) for suggestions over plain HTTPS.

Needs XAI_API_KEY in the environment. Model: XAI_MODEL (default below) or the request.
Base URL: XAI_BASE_URL (default https://api.x.ai). The key is never logged or returned.
Grok output is untrusted: it goes through the same safety layer as MOCK suggestions.

Not tested against the real xAI API in CI (no key on the maintainer box); tests use a faked
transport. Override the default model with XAI_MODEL or the request field.
"""
import json
import os
import re
from urllib.request import Request, urlopen

DEFAULT_MODEL = 'grok-4.7'  # xAI flagship as of Nov 2026; override with XAI_MODEL or the request
TIMEOUT_S = 45


class LiveUnavailable(Exception):
    pass


def model_name(requested=None):
    return requested or os.environ.get('XAI_MODEL') or DEFAULT_MODEL


def _prompt(state, lim, actions):
    return (
        'You advise a small family aquaponics garage pilot (goldfish, worms in a side stream, DWC plants). '
        'You only SUGGEST; a human decides and nothing is actuated. Be caution-first. '
        'Inputs are SIM or ASSUME unless labeled MEASURED; unknown values are not healthy. '
        f'Allowed actions: {", ".join(actions)}. '
        'feed_rate value = g/day number; water_temp_setpoint value = °C number; aeration value = keep_on|backup_on; '
        'circulation value = keep_on; manual_test/manual_review value = short text. Never suggest dose amounts. '
        'Reply with ONLY JSON: {"suggestions":[{"action":...,"value":...,"reason":"<one sentence>"}]} (max 6).\n'
        f'STATE: {json.dumps(state)}\nLIMITS: {json.dumps(lim)}'
    )


def _post(url, body, key):
    req = Request(url, data=json.dumps(body).encode(), method='POST',
                  headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'})
    with urlopen(req, timeout=TIMEOUT_S) as r:  # noqa: S310 (fixed https base URL)
        return json.loads(r.read())


def _text(data):
    """Pull the model's text out of a Responses API reply (chat-completions shape also accepted)."""
    if isinstance(data.get('output_text'), str):
        return data['output_text']
    parts = [c.get('text', '') for item in data.get('output', []) if isinstance(item, dict)
             for c in item.get('content') or [] if isinstance(c, dict) and c.get('type') == 'output_text']
    if parts:
        return ''.join(parts)
    return data['choices'][0]['message']['content']


def suggest(state, lim, actions, model=None, post=_post):
    key = os.environ.get('XAI_API_KEY')
    if not key:
        raise LiveUnavailable('XAI_API_KEY is not set')
    base = os.environ.get('XAI_BASE_URL', 'https://api.x.ai').rstrip('/')
    if not base.startswith('https://'):
        raise LiveUnavailable('XAI_BASE_URL must use https')
    body = {'model': model_name(model),
            'input': [{'role': 'system', 'content': 'Return strict JSON only.'},
                      {'role': 'user', 'content': _prompt(state, lim, actions)}]}
    try:
        content = _text(post(base + '/v1/responses', body, key))
    except Exception as exc:  # network, HTTP, shape: fall back to mock upstream
        raise LiveUnavailable(f'xAI request failed ({type(exc).__name__})') from None
    match = re.search(r'\{.*\}', content or '', re.S)
    try:
        items = json.loads(match.group(0))['suggestions'] if match else None
    except (ValueError, KeyError, TypeError):
        items = None
    if not isinstance(items, list):
        raise LiveUnavailable('Grok reply was not the expected JSON')
    out = []
    for it in items[:6]:
        if isinstance(it, dict):
            out.append({'action': it.get('action'), 'value': it.get('value'),
                        'reason': str(it.get('reason', ''))[:300],
                        'source': f'LIVE Grok ({model_name(model)}) via xAI API; untrusted until safety-checked'})
    return out
