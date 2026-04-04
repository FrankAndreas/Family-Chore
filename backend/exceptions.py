class DomainError(Exception):
    """Base exception for all business domain errors."""

    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code


class UserNotFoundError(DomainError):
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail, status_code=404)


class TaskNotFoundError(DomainError):
    def __init__(self, detail: str = "Task not found"):
        super().__init__(detail=detail, status_code=404)


class RewardNotFoundError(DomainError):
    def __init__(self, detail: str = "Reward not found"):
        super().__init__(detail=detail, status_code=404)


class InsufficientPointsError(DomainError):
    def __init__(self, detail: str = "Insufficient points balance"):
        super().__init__(detail=detail, status_code=400)


class InvalidStateTransitionError(DomainError):
    def __init__(self, detail: str = "Invalid state transition for resource"):
        super().__init__(detail=detail, status_code=400)


class DuplicateResourceError(DomainError):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(detail=detail, status_code=409)


class AuthorizationError(DomainError):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=403)
