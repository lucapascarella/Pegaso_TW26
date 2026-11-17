import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from utils.settings import settings

ALGORITHM = "HS256"

# Argon2: slow on purpose, with a random salt stored inside the hash
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(user_id: uuid.UUID, role: str) -> tuple[str, int]:
    """Return a signed JWT and its validity in seconds."""
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MIN * 60
    payload = {
        "sub": str(user_id),                                                # subject: who the token belongs to
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),  # expiration time
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM), expires_in


def decode_access_token(token: str) -> dict:
    """Verify signature and expiration. Raises jwt.InvalidTokenError if the token is not valid."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
