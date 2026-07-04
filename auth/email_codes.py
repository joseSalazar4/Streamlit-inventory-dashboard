from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

CODE_TTL_MINUTES = 15
MAX_EMAIL_CODE_ATTEMPTS = 5


def generate_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_code(code: str) -> str:
    return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()


def create_email_challenge() -> Tuple[str, Dict[str, Any]]:
    code = generate_verification_code()
    challenge = {
        "code_hash": hash_code(code),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MINUTES),
        "attempts_remaining": MAX_EMAIL_CODE_ATTEMPTS,
    }
    return code, challenge


def get_attempts_remaining(challenge: Dict[str, Any] | None) -> int:
    if not challenge:
        return 0
    return max(0, int(challenge.get("attempts_remaining", MAX_EMAIL_CODE_ATTEMPTS)))


def validate_email_code(code: str, challenge: Dict[str, Any] | None) -> Tuple[bool, str]:
    if not challenge:
        return False, "Request a new verification code."

    if not code.strip():
        return False, "Enter the verification code."

    expires_at = challenge.get("expires_at")
    if not expires_at or datetime.now(timezone.utc) > expires_at:
        return False, "The verification code expired. Request a new one."

    attempts_remaining = get_attempts_remaining(challenge)
    if attempts_remaining <= 0:
        return False, "Too many incorrect attempts. Request a new code."

    if hmac.compare_digest(hash_code(code), challenge.get("code_hash", "")):
        return True, "Email verified."

    attempts_remaining -= 1
    challenge["attempts_remaining"] = attempts_remaining
    if attempts_remaining <= 0:
        return False, "Invalid verification code. No attempts remaining. Request a new code."
    return False, f"Invalid verification code. {attempts_remaining} attempts remaining."
