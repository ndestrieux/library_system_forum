from abc import ABC
from typing import Optional

from pydantic import BaseModel as ValidatedData
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import RowReturningQuery

from database.models import BaseModel, Post, Topic


class BaseCRUD(ABC):
    """
    Abstract base class for CRUD operations.

    This class provides generic methods for creating, reading, updating,
    and deleting records in a database. It is meant to be subclassed with
    a specific model class assigned to the `MODEL` attribute.
    """

    MODEL = None

    @classmethod
    def get_one(cls, db: Session, id_: int) -> BaseModel:
        """
        Retrieve a single record by its ID.

        Args:
            db (Session): The database session.
            id_ (int): The ID of the record to retrieve.

        Returns:
            BaseModel: The retrieved record.
        """
        return db.query(cls.MODEL).where(cls.MODEL.id == id_).first()

    @classmethod
    def get_many(
        cls, db: Session, id_: Optional[int | str] = None, column: Optional[str] = None
    ) -> RowReturningQuery[tuple[BaseModel]]:
        """
        Retrieve multiple records based on optional filter criteria.

        Args:
            db (Session): The database session.
            id_ (Optional[int | str]): The ID or string value to filter by.
            column (Optional[str]): The column name to apply the filter on.

        Returns:
            ScalarResult[BaseModel]: The result set of records.
        """
        q = db.query(cls.MODEL)
        if id_ and column:
            q.where(getattr(cls.MODEL, column) == id_)
        return q

    @classmethod
    def create(cls, db: Session, validated_data: ValidatedData) -> BaseModel:
        """
        Create a new record in the database.

        Args:
            db (Session): The database session.
            validated_data (ValidatedData): The data to create the record from.

        Returns:
            BaseModel: The created record.
        """
        obj = cls.MODEL(**validated_data.model_dump(exclude_none=True))
        db.add(obj)
        db.commit()
        return obj

    @classmethod
    def update(
        cls, db: Session, obj: BaseModel, validated_data: ValidatedData
    ) -> BaseModel:
        """
        Update an existing record in the database.

        Args:
            db (Session): The database session.
            obj (BaseModel): The record to update.
            validated_data (ValidatedData): The data to update the record with.

        Returns:
            BaseModel: The updated record.
        """
        for k, v in validated_data.model_dump(exclude_none=True).items():
            setattr(obj, k, v)
        db.commit()
        return obj

    @classmethod
    def delete(cls, db: Session, obj: BaseModel) -> bool:
        """
        Delete a record from the database.

        Args:
            db (Session): The database session.
            obj (BaseModel): The record to delete.

        Returns:
            bool: True if the deletion was successful.
        """
        db.delete(obj)
        db.commit()
        return True


class TopicCRUD(BaseCRUD):
    """
    CRUD operations for the Topic model.

    This class implements the CRUD operations for the Topic model by
    specifying the `MODEL` attribute.
    """

    MODEL = Topic


class PostCRUD(BaseCRUD):
    """
    CRUD operations for the Post model.

    This class implements the CRUD operations for the Post model by
    specifying the `MODEL` attribute.
    """

    MODEL = Post
