from strawberry.exceptions import StrawberryGraphQLError

from database.models import BaseModel


class ObjectNotFound(StrawberryGraphQLError):
    def __init__(self, model: BaseModel, id_: int, **kwargs):
        super().__init__(f"{model.__name__} object with id '{id_}' could not be found.")
