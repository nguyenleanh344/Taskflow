from app.exceptions.base import ForbiddenError, UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    code = "invalid_credentials"
    default_detail = "Invalid credentials"


class InactiveUserError(ForbiddenError):
    code = "inactive_user"
    default_detail = "User is inactive"


class InvalidRefreshTokenError(UnauthorizedError):
    code = "invalid_refresh_token"
    default_detail = "Invalid refresh token"
