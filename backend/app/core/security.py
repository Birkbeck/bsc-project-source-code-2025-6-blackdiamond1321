"""Implementations of IPasswordHasher and IAuthToken using Argon2id and JWT"""

from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.interfaces import IAuthToken, IPasswordHasher


class Argon2PasswordHasher(IPasswordHasher):
    """Argon2id implementation of IPasswordHasher"""

    # add secret words to all passwords before hashing. For extra security
    def __init__(self, pepper: str):
        self._argon2 = PasswordHasher()
        self.pepper = pepper

    def hash(self, plain: str) -> str:
        return self._argon2.hash(plain + self.pepper)

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return self._argon2.verify(hashed, plain + self.pepper)
        except (VerifyMismatchError, InvalidHashError):
            return False


class JWTAuthToken(IAuthToken):
    """JWT implementation of IAuthToken using HS256"""

    def __init__(self, secret_key: str, expire_hours: int = 24, algorithm: str = "HS256"):
        # for test purpose jwt session last 24 hours, later will change to 15 min. For best security
        self._key = secret_key
        self._hours = expire_hours
        self._alg = algorithm

    def create_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(hours=self._hours)
        return jwt.encode(
            {"sub": str(user_id), "exp": expire},
            self._key,
            algorithm=self._alg,
        )

    def decode_token(self, token: str) -> int | None:
        try:
            payload = jwt.decode(token, self._key, algorithms=[self._alg])
            return int(payload["sub"])
        except (jwt.PyJWTError, KeyError, ValueError):
            return None