# src/auth/verification.py
import os, hmac, hashlib, secrets

VERIFY_CODE_SECRET = os.getenv("VERIFY_CODE_SECRET", "dev-secret-change-me")

def generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"  # 000000 - 999999

def hash_code(code: str) -> str:
    return hmac.new(
        VERIFY_CODE_SECRET.encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()
