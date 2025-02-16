from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    A model representing a paginated response.
    """

    total: int
    page: int
    size: int
    data: List[T]


class TopicSchema(BaseModel):
    """
    A model representing the response schema for a topic.
    """

    id: int
    title: str
    description: Optional[str]
    category: str
    created_by: str
    created_on: datetime


class PostSchema(BaseModel):
    """
    A model representing the response schema for a post.
    """

    id: int
    content: str
    author: str
    posted_on: datetime
