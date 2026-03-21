"""
Custom exception hierarchy for the application.
All domain exceptions inherit from AppException so the global handler
can catch them uniformly and return structured JSON responses.
"""


class AppException(Exception):
    """Base exception for all application-level errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    status_code = 404
    error_code = "NOT_FOUND"
    detail = "The requested resource was not found."


class ConflictException(AppException):
    """Raised when a resource already exists or there is a state conflict."""

    status_code = 409
    error_code = "CONFLICT"
    detail = "A conflict occurred with an existing resource."


class ForbiddenException(AppException):
    """Raised when the authenticated user lacks permission for the action."""

    status_code = 403
    error_code = "FORBIDDEN"
    detail = "You do not have permission to perform this action."


class UnauthorizedException(AppException):
    """Raised when authentication is missing or invalid."""

    status_code = 401
    error_code = "UNAUTHORIZED"
    detail = "Authentication is required or the provided credentials are invalid."


class BadRequestException(AppException):
    """Raised when the request is malformed or contains invalid data."""

    status_code = 400
    error_code = "BAD_REQUEST"
    detail = "The request could not be processed due to invalid input."
