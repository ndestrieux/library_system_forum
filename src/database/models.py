from datetime import date
from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

BaseModel = declarative_base()


class Post(BaseModel):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    author: Mapped[str] = mapped_column(String(20))
    posted_on: Mapped[date] = mapped_column(insert_default=date.today)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topic.id"))


class Topic(BaseModel):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    created_by: Mapped[str] = mapped_column(String(20))
    created_on = mapped_column(insert_default=date.today)

    posts: Mapped[List["Post"]] = relationship("Post", back_populates="post")
