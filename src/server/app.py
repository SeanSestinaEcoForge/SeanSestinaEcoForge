"""Compatibility launch path; same pilot API, not a second stale set of limits.
Run: uvicorn src.server.app:app --host 127.0.0.1
Legacy /viability is retired: cell density is not a garage-pilot health test.
"""
from api.main import app
