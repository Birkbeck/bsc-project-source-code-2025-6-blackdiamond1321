"""Business logic for user"""

from app.interfaces import IAuthToken, IPasswordHasher
from app.models import User
from app.repositories import UserRepository
from app.schemas import TokenResponse, UserCreate, UserResponse


class EmailExistsError(Exception):
    """Raised when registering with an email that was used before"""


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
                f"Account with email {data.email} already exists."
            )

        user = User(
            email=data.email,
            password_hash=self._hasher.hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            security_question=data.security_question,

            # make the answer lowercase  and remove any whitespace
            security_answer=data.security_answer.strip().lower(),
        )
        self._users.add(user)

        return TokenResponse(
            access_token=self._tokens.create_token(user.id),
            user=UserResponse.model_validate(user),
        )