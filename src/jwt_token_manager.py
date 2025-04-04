from typing import List

import jwt
from jwt.exceptions import DecodeError
from pydantic import BaseModel, ValidationError

from conf import get_settings
from exceptions import JWTTokenInvalidError


class Token(BaseModel):
    """
    A model representing a token.

    Attributes:
        bearer (str): The bearer token string.
    """

    bearer: str


class RequesterData(BaseModel):
    """
    A model representing requester data.

    Attributes:
        name (str): The name of the requester.
        groups (List[str]): A list of groups the requester belongs to.
    """

    name: str
    groups: List[str]


class JWTToken:
    """
    A class for handling JWT token operations.

    Attributes:
        _SECRET (str): (class) The secret key used for encoding and decoding JWT tokens.
        _ALGORITHM (str): (class) The algorithm used for encoding and decoding JWT tokens.
    """

    _SECRET = get_settings().JWT_SECRET
    _ALGORITHM = get_settings().JWT_ALG

    @classmethod
    def decode(cls, token: str) -> RequesterData:
        """
        Decodes a JWT token to extract requester data.

        Args:
            token (Annotated[Token, Header()]): The token to decode.

        Returns:
            RequesterData: The data extracted from the token.

        Raises:
            JWTTokenInvalidException: If the token is invalid or cannot be decoded.
        """
        try:
            return RequesterData(**jwt.decode(token, cls._SECRET, [cls._ALGORITHM]))
        except ValidationError as ve:
            fields = ", ".join(e["loc"][0] for e in ve.errors())
            error = f"Missing data or incorrect format: {fields}"
            raise JWTTokenInvalidError(error)
        except DecodeError as e:
            raise JWTTokenInvalidError(e)
