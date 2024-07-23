from typing import List, Optional

from sqlalchemy import delete
from sqlalchemy.orm import Session
from strawberry.types.nodes import SelectedField

from database.models import Model
from database.query_builders import SQLQuery
from database.validators.author import Validator
from filters.author import Filter


def crud_factory(model: Model):
    class SQLCrud:
        @classmethod
        def create(
            cls,
            db: Session,
            data: Validator,
        ) -> Model:
            db_model = model(**data.model_dump())
            db.add(db_model)
            db.commit()
            db.refresh(db_model)
            return db_model

        @classmethod
        def get_one_by_id(
            cls,
            session: Session,
            id_: int,
            fields: List[SelectedField],
            *,
            with_for_update: bool = False,
        ) -> Model:
            query_builder = SQLQuery(model, fields, obj_id=id_)
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
            query_builder = SQLQuery(model, fields, q_filter=q_filter)
            query = query_builder.build()
            return session.execute(query).unique().scalars()

        @classmethod
        def update_by_id(
            cls,
            session: Session,
            data: Validator,
            id_: int,
            fields: List[SelectedField],
        ) -> Model:
            db_model = cls.get_one_by_id(session, id_, fields, with_for_update=True)
            values = data.model_dump(exclude_unset=True)
            for k, v in values.items():
                setattr(db_model, k, v)
            session.commit()
            return db_model

        @classmethod
        def remove_by_id(cls, session: Session, id_: int) -> int:
            query = delete(model).filter_by(id=id_)
            rows = session.execute(query)
            session.commit()
            return rows.rowcount

    SQLCrud.model = model
    return SQLCrud
