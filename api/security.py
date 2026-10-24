"""Shared-password gate for the API.

Same intent as the old Streamlit gate: one password for a personal app. If
`DEVI_PASSWORD` is unset (local development) auth is disabled entirely.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time

COOKIE = "devi_session"
TTL_SECONDS = 60 * 60 * 24 * 30  # 30 days


def _password() -> str:
    return os.environ.get("DEVI_PASSWORD", "")


def auth_required() -> bool:
    return bool(_password())


def _secret() -> bytes:
    explicit = os.environ.get("DEVI_SECRET")
    if explicit:
        return explicit.encode()
    return hashlib.sha256(("devi:" + _password()).encode()).digest()


def check_password(candidate: str) -> bool:
    pw = _password()
    if not pw:
        return True
    return hmac.compare_digest(candidate or "", pw)


def issue_token() -> str:
    exp = str(int(time.time()) + TTL_SECONDS)
    sig = hmac.new(_secret(), exp.encode(), hashlib.sha256).hexdigest()
    return f"{exp}.{sig}"


def verify_token(token: str | None) -> bool:
    if not auth_required():
        return True
    if not token or "." not in token:
        return False
    exp, sig = token.split(".", 1)
    expected = hmac.new(_secret(), exp.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return False
    try:
        return int(exp) > time.time()
    except ValueError:
        return False


def cookie_secure() -> bool:
    return os.environ.get("DEVI_COOKIE_SECURE", "0") == "1"
