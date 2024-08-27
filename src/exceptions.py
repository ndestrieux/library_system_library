from strawberry.exceptions import StrawberryGraphQLError

from database.models import BaseModel


class RelatedObjectMissingError(StrawberryGraphQLError):
    def __init__(self, model: BaseModel, related_model: BaseModel, **kwargs):
        super().__init__(
            f"{model.__name__} object should be related to at least 1 object of type {related_model.__name__}."
        )
