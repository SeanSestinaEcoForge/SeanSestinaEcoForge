"""Grok advisor demo: suggests adjustments, never actuates.

Pipeline: state -> suggestions (``mock`` rules or ``live`` Grok) -> caution-first safety layer
(``safety.py``) -> response. Every suggestion is returned with ``executed: false``.
"""
from .service import advise, safety_limits  # noqa: F401
