class DomainError(Exception):
    status_code = 500
    code = "domain_error"
    default_detail = "An application error occurred"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class NotFoundError(DomainError):
    status_code = 404
    code = "not_found"
    default_detail = "Resource not found"


class ForbiddenError(DomainError):
    status_code = 403
    code = "forbidden"
    default_detail = "You do not have permission to access this resource"


class UnauthorizedError(DomainError):
    status_code = 401
    code = "unauthorized"
    default_detail = "Authentication failed"


class ConflictError(DomainError):
    status_code = 409
    code = "conflict"
    default_detail = "The resource conflicts with existing data"
