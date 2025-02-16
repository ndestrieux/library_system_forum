from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

BaseModel = declarative_base()


class Post(BaseModel):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    author: Mapped[str] = mapped_column(String(20))
    posted_on: Mapped[datetime] = mapped_column(insert_default=datetime.today)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))

    topic = relationship("Topic", back_populates="posts")


class Topic(BaseModel):
    __tablename__ = "topic"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    category: Mapped[str] = mapped_column(String(20))
    created_by: Mapped[str] = mapped_column(String(20))
    created_on: Mapped[datetime] = mapped_column(insert_default=datetime.today)

    posts: Mapped[List["Post"]] = relationship(
        "Post", back_populates="topic", cascade="all, delete-orphan"
    )
