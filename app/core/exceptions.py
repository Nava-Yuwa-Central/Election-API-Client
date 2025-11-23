"""Custom exception classes for the Nepal Entity Service."""

from fastapi import HTTPException, status


class EntityNotFoundError(HTTPException):
    """Raised when an entity is not found."""

    def __init__(self, entity_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID '{entity_id}' not found",
        )


class RelationshipNotFoundError(HTTPException):
    """Raised when a relationship is not found."""

    def __init__(self, relationship_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID '{relationship_id}' not found",
        )


class EntityValidationError(HTTPException):
    """Raised when entity validation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class RelationshipValidationError(HTTPException):
    """Raised when relationship validation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class DatabaseError(HTTPException):
    """Raised when a database operation fails."""

    def __init__(self, detail: str = "Database operation failed") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
