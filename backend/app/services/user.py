"""Business logic for user"""

from app.interfaces import IAuthToken, IPasswordHasher
from app.models import User
from app.repositories import UserRepository
from app.schemas import TokenResponse, UserCreate, UserResponse, UserLogin, UserUpdate
from app.utils.exceptions import (
    IncorrectAnswerError,
    UserNotFoundError,
    InvalidCredentialsError,
    EmailExistsError,
    InvalidEmailOrAnswerError)

import base64
import io
import json
import secrets

import pyotp
import qrcode

class UserService:
    """Business logic for user account operations"""

    def __init__(
        self,
        users: UserRepository,
        hasher: IPasswordHasher,
        tokens: IAuthToken,
    ):
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def register(self, data: UserCreate) -> TokenResponse:
        """Create a new account and return a session token"""
        if self._users.find_by_email(data.email):
            raise EmailExistsError(
                f"Account with email {data.email} already exists"
            )

        user = User(
            email=data.email,
            password_hash=self._hasher.hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            security_question=data.security_question,

            # make the answer lowercase and remove any whitespaces
            security_answer=data.security_answer.strip().lower(),
        )
        self._users.add(user)

        return TokenResponse(
            access_token=self._tokens.create_token(user.id),
            user=UserResponse.model_validate(user),
        )

    def login(self, data: UserLogin) -> TokenResponse:
        """Check credentials and return a token. If 2FA is enabled, return a challenge token"""
        user = self._users.find_by_email(data.email)
        if not user or not self._hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError()

        if user.totp_enabled:
            from app.schemas import TFAChallengeResponse
            return TFAChallengeResponse(challenge_token=self._tokens.create_challenge_token(user.id))

        return TokenResponse(
            access_token=self._tokens.create_token(user.id),
            user=UserResponse.model_validate(user),
        )

    def login_2fa(self, challenge_token: str, code: str) -> TokenResponse:
        """Check t 2FA code connected with the challenge token"""
        user_id = self._tokens.decode_challenge_token(challenge_token)
        if user_id is None:
            raise InvalidCredentialsError()
        user = self._users.get(user_id)
        if not user or not self.verify_totp(user, code):
            raise InvalidCredentialsError()
        return TokenResponse(
            access_token=self._tokens.create_token(user.id),
            user=UserResponse.model_validate(user),
        )

    def get_security_question(self, email: str) -> str:
        """Give the security question for the given email"""
        user = self._users.find_by_email(email)
        if not user:
            raise UserNotFoundError()
        return user.security_question

    def reset_password(self, email: str, answer: str, new_password: str) -> None:
        """Check if the security answer is the same and reset the password"""
        user = self._users.find_by_email(email)
        if not user:
            raise InvalidEmailOrAnswerError()

        # # make the typed answer lowercase and remove any whitespaces
        if user.security_answer != answer.strip().lower():
            raise InvalidEmailOrAnswerError()

        user.password_hash = self._hasher.hash(new_password)
        self._users.update(user)

    def update_profile(self, user: User, data: UserUpdate) -> User:
        """Update name and email. Reject if the email is taken by someone else."""
        if data.email != user.email:
            existing = self._users.find_by_email(data.email)
            if existing and existing.id != user.id:
                raise EmailExistsError(
                    f"Account with email {data.email} already exists"
                )
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.email = data.email
        return self._users.update(user)

    def change_password(self, user: User, current: str, new: str) -> None:
        """Check the current password, then replace it with the new one"""
        if not self._hasher.verify(current, user.password_hash):
            raise InvalidCredentialsError()
        user.password_hash = self._hasher.hash(new)
        self._users.update(user)

    def delete_account(self, user: User, email: str, password: str) -> None:
        """Check email and password, then delete the account"""
        if email != user.email:
            raise InvalidCredentialsError()
        if not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError()
        self._users.delete(user)

    def start_2fa_setup(self, user: User) -> "TFASetupResponse":
        """Generate TOTP secret and a QR code for the auth app"""
        from app.schemas import TFASetupResponse

        if not user.totp_secret:
            user.totp_secret = pyotp.random_base32()
            self._users.update(user)

        uri = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(name=user.email, issuer_name="FinTrack")
        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

        return TFASetupResponse(secret=user.totp_secret, qr_data_url=qr_data_url)

    def enable_2fa(self, user: User, code: str) -> list[str]:
        """Check the code from setup, return recovery codes"""
        if not user.totp_secret or not pyotp.TOTP(user.totp_secret).verify(code, valid_window=1):
            raise InvalidCredentialsError()

        codes = [secrets.token_hex(4) for _ in range(8)]
        user.recovery_codes = json.dumps(codes)
        user.totp_enabled = True
        self._users.update(user)
        return codes

    def disable_2fa(self, user: User, password: str, code: str) -> None:
        """Check password and current code from auth app, then turn 2FA off"""
        if not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError("Wrong password")
        if not user.totp_secret or not pyotp.TOTP(user.totp_secret).verify(code, valid_window=1):
            raise InvalidCredentialsError("Wrong 2FA code")
        user.totp_enabled = False
        user.totp_secret = None
        user.recovery_codes = None
        self._users.update(user)

    def verify_totp(self, user: User, code: str) -> bool:
        """Check a 6-digit code or a recovery code"""
        if not user.totp_secret:
            return False
        if pyotp.TOTP(user.totp_secret).verify(code, valid_window=1):
            return True
        codes = json.loads(user.recovery_codes or "[]")
        if code in codes:
            codes.remove(code)
            user.recovery_codes = json.dumps(codes)
            self._users.update(user)
            return True
        return False