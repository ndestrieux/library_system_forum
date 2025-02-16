from abc import ABC, abstractmethod

from fastapi import status


class ForumApiException(Exception, ABC):
    """
    Base custom exception class for the Forum API.

    This class serves as a base for all custom exceptions in the Forum API.
    It defines a common structure for handling exceptions with a status code
    and a message property.

    Attributes:
        STATUS_CODE (int): The HTTP status code associated with the exception.
    """

    STATUS_CODE = None

    @property
    @abstractmethod
    def message(self) -> str:
        """
        Abstract property for the exception message.

        Returns:
            str: The message describing the exception.
        """
        ...


class JWTTokenInvalidException(ForumApiException):
    """
    Exception raised when a JWT token is invalid or missing required data.

    This exception is used to indicate issues with JWT token validation.

    Attributes:
        STATUS_CODE (int): The HTTP status code for a bad request (400).
        error (Exception): The underlying error that caused the token validation to fail.
    """

    STATUS_CODE = status.HTTP_400_BAD_REQUEST

    def __init__(self, error: Exception):
        """
        Initializes the exception with the underlying error.

        Args:
            error (Exception): The error that caused the token validation to fail.
        """
        self.error = error

    @property
    def message(self) -> str:
        """
        The message describing the exception.

        Returns:
            str: A message indicating that the token is not valid, along with the underlying error.
        """
        return f"Token not valid: {self.error}"


class NoPermissionException(ForumApiException):
    """
    Exception raised when a user attempts an unauthorized action.

    This exception is used to indicate that a user does not have the necessary
    permissions to perform a certain action, such as creation, update, or deletion.

    Attributes:
        STATUS_CODE (int): The HTTP status code for forbidden access (403).
        username (str): The username of the user who attempted the unauthorized action.
    """

    STATUS_CODE = status.HTTP_403_FORBIDDEN

    def __init__(self, username: str):
        """
        Initializes the exception with the username of the user.

        Args:
            username (str): The username of the user who attempted the unauthorized action.
        """
        self.username = username

    @property
    def message(self) -> str:
        """
        The message describing the exception.

        Returns:
            str: A message indicating that the user does not have sufficient permissions.
        """
        return f"User {self.username} does not have enough permission to perform this action!"
