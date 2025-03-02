from typing import Optional, TypeAlias

from pydantic import BaseModel

ValidatedData: TypeAlias = BaseModel


class TopicCreateValidatedData(ValidatedData):
    """
    A model representing validated data for creating a topic.
    """

    title: str
    description: Optional[str] = None
    category: str
    created_by: str


class TopicUpdateValidatedData(ValidatedData):
    """
    A model representing validated data for updating a topic.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class PostCreateValidatedData(ValidatedData):
    """
    A model representing validated data for creating a post.
    """

    content: str
    author: str
    topic_id: int


class PostUpdateValidatedData(ValidatedData):
    """
    A model representing validated data for updating a post.
    """

    content: str
