from app.exceptions.base import ConflictError, ForbiddenError, NotFoundError


class EmailAlreadyExistsError(ConflictError):
    code = "email_already_exists"
    default_detail = "Email already exists"


class ProjectNotFoundError(NotFoundError):
    code = "project_not_found"
    default_detail = "Project not found"


class ProjectForbiddenError(ForbiddenError):
    code = "project_forbidden"
    default_detail = "You do not have permission to access this project"


class TaskNotFoundError(NotFoundError):
    code = "task_not_found"


class TaskForbiddenError(ForbiddenError):
    code = "task_forbidden"


class CommentNotFoundError(NotFoundError):
    code = "comment_not_found"


class CommentForbiddenError(ForbiddenError):
    code = "comment_forbidden"


class UserNotFoundError(NotFoundError):
    code = "user_not_found"


class MemberNotFoundError(NotFoundError):
    code = "member_not_found"


class MemberAlreadyExistsError(ConflictError):
    code = "member_already_exists"
    default_detail = "User is already a member of this project"


class ProjectMemberForbiddenError(ForbiddenError):
    code = "project_member_forbidden"
    default_detail = "You do not have permission to manage this project"
