from strawberry.exceptions import StrawberryGraphQLError

from database.models import BaseModel


class ObjectNotFound(StrawberryGraphQLError):
    def __init__(self, model: BaseModel, id_: int, **kwargs):
        super().__init__(f"{model.__name__} object with id '{id_}' could not be found.")


class JWTTokenInvalidError(StrawberryGraphQLError):
    """
    Exception raised when a JWT token is invalid or missing required data.

    This exception is used to indicate issues with JWT token validation.

    Args:
        error (Exception | str): The underlying error that caused the token validation to fail.
    """

    def __init__(self, error: Exception | str):
        super().__init__(f"Token not valid: {error}")
