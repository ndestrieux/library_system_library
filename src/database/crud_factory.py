from abc import ABC
from typing import List, Optional

from sqlalchemy import delete
from sqlalchemy.orm import Session
from strawberry.types.nodes import SelectedField

from database.models import Author as AuthorModel
from database.models import BaseModel
from database.models import Book as BookModel
from database.query_builders import AuthorSQLQuery, BookSQLQuery
from database.validators.author import Validator
from filters.author import Filter


class BaseSQLCrud(ABC):
    MODEL = None
    QUERY_BUILDER = None

    @classmethod
    def create(
        cls,
        db: Session,
        data: Validator,
    ) -> BaseModel:
        obj = cls.MODEL(**data.model_dump())
        db.add(obj)
        db.commit()
        return obj

    @classmethod
    def get_one_by_id(
        cls,
        session: Session,
        id_: int,
        fields: List[SelectedField],
        *,
        with_for_update: bool = False,
    ) -> BaseModel:
        query_builder = cls.QUERY_BUILDER(cls.MODEL, fields, obj_id=id_)
        query = query_builder.build()
        if with_for_update:
            query = query.with_for_update()
        return session.execute(query).unique().scalar_one()

    @classmethod
    def get_many_by_values(
        cls,
        session: Session,
        fields: List[SelectedField],
        q_filter: Optional[Filter] = None,
    ):
        query_builder = cls.QUERY_BUILDER(cls.MODEL, fields, q_filter=q_filter)
        query = query_builder.build()
        return session.execute(query).unique().scalars()

    @classmethod
    def update_by_id(
        cls,
        session: Session,
        data: Validator,
        id_: int,
        fields: List[SelectedField],
    ) -> BaseModel:
        obj = cls.get_one_by_id(session, id_, fields, with_for_update=True)
        values = data.model_dump(exclude_unset=True)
        for k, v in values.items():
            setattr(obj, k, v)
        session.commit()
        return obj

    @classmethod
    def remove_by_id(cls, session: Session, id_: int) -> int:
        query = delete(cls.MODEL).filter_by(id=id_)
        rows = session.execute(query)
        session.commit()
        return rows.rowcount


class AuthorSQLCrud(BaseSQLCrud):
    MODEL = AuthorModel
    QUERY_BUILDER = AuthorSQLQuery


class BookSQLCrud(BaseSQLCrud):
    MODEL = BookModel
    QUERY_BUILDER = BookSQLQuery
