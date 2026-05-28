from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
import bcrypt

from app.core.config import get_settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ရိုက်ထည့်လိုက်သော Password နှင့် Database ထဲက Hash ကို တိုက်စစ်ရန်"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    """စာသား Password ကို လုံခြုံစိတ်ချရသော Hash အဖြစ် ပြောင်းရန်"""
    pwbytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwbytes, salt)
    return hashed_password.decode("utf-8")


def create_access_token(subject: str | UUID, expires_delta: timedelta = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        subject: str | None = payload.get("sub")
        return subject
    except JWTError:
        return None