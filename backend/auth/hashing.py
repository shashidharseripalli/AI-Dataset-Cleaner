import hashlib

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _normalize_password(password: str) -> str:
    # bcrypt only supports up to 72 bytes; pre-hash long passwords safely.
    if len(password.encode("utf-8")) <= 72:
        return password
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return f"sha256${digest}"


def hash_password(password: str) -> str:
    return pwd_context.hash(_normalize_password(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    normalized = _normalize_password(plain_password)
    try:
        return pwd_context.verify(normalized, hashed_password)
    except ValueError:
        # Legacy fallback for previously stored bcrypt hashes.
        if len(plain_password.encode("utf-8")) <= 72:
            return pwd_context.verify(plain_password, hashed_password)
        return False
