"""Errors that app can run into"""


class DomainError(Exception):
    """The base class for all errors"""

    status_code: int = 400
    detail: str = "Domain error"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


# 400. The user sent wrong data

class ValidationError(DomainError):
    status_code = 400


class EmailExistsError(ValidationError):
    """Raised when registering with an email that was used before"""
    detail = "Email already in use"


class IncorrectAnswerError(ValidationError):
    """Raised when the security answer doesn't match"""
    detail = "Incorrect security answer"


class InvalidEmailOrAnswerError(ValidationError):
    """Raised by reset-password. Error for wrong email or wrong answer"""

    detail = "Invalid email or answer"

class OverpaymentError(ValidationError):
    """Raised when a payment exceed the loan's outstanding balance"""
    detail = "Payment exceeds loan balance"


# 401. The user used wrong credentials

class AuthError(DomainError):
    status_code = 401


class InvalidCredentialsError(AuthError):
    """Raised when login details are incorrect"""
    detail = "Invalid email or password"


# 404. If account not registered or service does not exist

class NotFoundError(DomainError):
    status_code = 404


class UserNotFoundError(NotFoundError):
    """Raised when no account exists with the given email"""
    detail = "No account found with this email"

class TransactionNotFoundError(NotFoundError):
    """Raised when a transaction does not exist"""
    detail = "Transaction not found"

class BudgetNotFoundError(NotFoundError):
    """Raised when a budget does not exist"""
    detail = "Budget not found"

class LoanNotFoundError(NotFoundError):
    """Raised when a loan doesn't exist"""
    detail = "Loan not found"