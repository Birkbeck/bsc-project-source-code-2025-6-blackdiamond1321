"""Business logic for user"""

from app.interfaces import IAuthToken, IPasswordHasher
from app.models import User
from app.repositories import UserRepository
from app.schemas import TokenResponse, UserCreate, UserResponse, UserLogin


class EmailExistsError(Exception):
    """Raised when registering with an email that was used before"""

class InvalidCredentialsError(Exception):
    """Raised when login details are incorrect"""

class UserNotFoundError(Exception):
    """Raised when no account exists with the given email"""

class IncorrectAnswerError(Exception):
    """Raised when the security answer doesn't match"""

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
        """Check credentials and return a token"""
        user = self._users.find_by_email(data.email)
        if not user or not self._hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        return TokenResponse(
            access_token=self._tokens.create_token(user.id),
            user=UserResponse.model_validate(user),
        )

    def get_security_question(self, email: str) -> str:
        """Give the security question for the given email"""
        user = self._users.find_by_email(email)
        if not user:
            raise UserNotFoundError("No account found with this email.")
        return user.security_question

    def reset_password(self, email: str, answer: str, new_password: str) -> None:
        """Check if the security answer is the same and reset the password"""
        user = self._users.find_by_email(email)
        if not user:
            raise UserNotFoundError("No account found with this email.")

        # # make the typed answer lowercase and remove any whitespaces
        if user.security_answer != answer.strip().lower():
            raise IncorrectAnswerError("Incorrect security answer.")

        user.password_hash = self._hasher.hash(new_password)
        self._users.update(user)