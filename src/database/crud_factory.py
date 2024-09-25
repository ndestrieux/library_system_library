from abc import ABC
from typing import List, Optional

from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from strawberry.types.nodes import SelectedField

from database.models import Author as AuthorModel
from database.models import BaseModel
from database.models import Book as BookModel
from database.query_builders import AuthorSQLQuery, BookSQLQuery
from database.validators.author import Validator
from exceptions import ObjectNotFound
from filters.base import Filter


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
        return obj

    @classmethod
    def get_one_by_id(
        cls,
        session: Session,
        id_: int,
        fields: Optional[List[SelectedField]] = None,
        *,
        with_for_update: bool = False,
    ) -> BaseModel:
        try:
            query_builder = cls.QUERY_BUILDER(fields, obj_id=id_)
            query = query_builder.build()
            if with_for_update:
                query = query.with_for_update()
            return session.execute(query).unique().scalar_one()
        except NoResultFound as e:
            raise ObjectNotFound(cls.MODEL, id_) from e

    @classmethod
    def get_many_by_values(
        cls,
        session: Session,
        fields: Optional[List[SelectedField]] = None,
        q_filter: Optional[Filter] = None,
    ) -> BaseModel:
        query_builder = cls.QUERY_BUILDER(fields, q_filter=q_filter)
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
        return obj

    @classmethod
    def remove_by_id(cls, session: Session, id_: int) -> int:
        query = delete(cls.MODEL).filter_by(id=id_)
        rows = session.execute(query)
        return rows.rowcount

    @classmethod
    def create_relation(
        cls, session: Session, base_obj: BaseModel, related_ids: List[int]
    ):
        relation_name = cls.MODEL.__tablename__
        [
            getattr(base_obj, relation_name).append(
                cls.get_one_by_id(session, related_obj_id)
            )
            for related_obj_id in related_ids
        ]

    @classmethod
    def remove_relation(
        cls, session: Session, base_obj: BaseModel, related_ids: List[int]
    ):
        relation_name = cls.MODEL.__tablename__
        existing_relations = getattr(base_obj, relation_name)
        for id_ in related_ids:
            try:
                related_obj = cls.get_one_by_id(session, id_)
                if related_obj in existing_relations:
                    existing_relations.remove(related_obj)
            except ObjectNotFound:
                pass


class AuthorSQLCrud(BaseSQLCrud):
    MODEL = AuthorModel
    QUERY_BUILDER = AuthorSQLQuery


class BookSQLCrud(BaseSQLCrud):
    MODEL = BookModel
    QUERY_BUILDER = BookSQLQuery
