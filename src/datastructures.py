from typing import List, Optional

from pydantic import BaseModel, conint


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


class PageParams(BaseModel):
    """
    A model representing pagination parameters.

    Attributes:
        page (conint): The page number, must be greater than or equal to 1. Defaults to 1.
        size (conint): The number of items per page, must be between 1 and 100. Defaults to 10.
    """

    page: conint(ge=1) = 1
    size: conint(ge=1, le=100) = 10


class TopicCreateData(BaseModel):
    """
    A model representing data for creating a topic.

    Attributes:
        title (str): The title of the topic.
        description (Optional[str]): An optional description of the topic. Defaults to None.
        category (str): The category of the topic.
    """

    title: str
    description: Optional[str] = None
    category: str


class TopicUpdateData(BaseModel):
    """
    A model representing data for updating a topic.

    Attributes:
        title (Optional[str]): An optional title for the topic. Defaults to None.
        description (Optional[str]): An optional description for the topic. Defaults to None.
        category (Optional[str]): An optional category for the topic. Defaults to None.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class PostData(BaseModel):
    """
    A model representing data for a post.

    Attributes:
        content (str): The content of the post.
    """

    content: str
