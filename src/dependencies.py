from typing import Annotated

import jwt
from fastapi import Header
from jwt.exceptions import DecodeError

from conf import get_settings
from database.db_conf import SessionLocal
from datastructures import RequesterData, Token
from exceptions import JWTTokenInvalidException


def get_db():
    """
    Generator function to get a database session.

    Yields:
        Session: A database session.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class JWTToken:
    """
    A class for handling JWT token operations.

    Attributes:
        _secret (str): The secret key used for encoding and decoding JWT tokens.
        _algorithm (str): The algorithm used for encoding and decoding JWT tokens.
    """

    def __init__(self):
        self._secret = get_settings().jwt_secret
        self._algorithm = get_settings().jwt_alg

    def decode(self, token: Annotated[Token, Header()]) -> RequesterData:
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
            return RequesterData(
                **jwt.decode(token.bearer, self._secret, [self._algorithm])
            )
        except DecodeError as e:
            raise JWTTokenInvalidException(e)
