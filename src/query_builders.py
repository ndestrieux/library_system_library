from abc import ABC
from typing import Any, Dict, List, Optional

import strawberry
from sqlalchemy import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import joinedload, load_only, strategy_options
from strawberry.types.nodes import SelectedField
from strawberry.utils.str_converters import to_snake_case

from database import Base as BaseModel
from filters.author import AuthorFilter
from models import Author as AuthorModel
from models import Book as BookModel


class Query(ABC):
    FILTER_CRITERION_DICT = {}
    RELATED_FIELDS = []
    JOIN_DICT = {}

    def __init__(
        self,
        model: BaseModel,
        fields: List[SelectedField],
        q_filter: Optional[AuthorFilter] = None,
    ):
        self.model = model
        self.fields = fields
        self.q_filter = q_filter
        self.joins = []

    def _get_model_field_objs(
        self, model: BaseModel, fields: List[SelectedField]
    ) -> Dict[str, List[Any]]:
        result = {"fields": [], "related": []}
        relationship_model_dict = {
            str(r).split(".")[-1]: r.mapper.class_ for r in inspect(model).relationships
        }
        for field in fields:
            if field.selections:
                result["related"].append(
                    {"name": to_snake_case(field.name)}
                    | self._get_model_field_objs(
                        relationship_model_dict[field.name], field.selections
                    )
                )
            else:
                result["fields"].append(getattr(model, to_snake_case(field.name)))
        return result

    def _build_options(self) -> List[strategy_options]:
        load_attrs = self._get_model_field_objs(self.model, self.fields)
        options = [load_only(*load_attrs["fields"])]
        if load_attrs.get("related"):
            relationship_attr = getattr(
                self.model, load_attrs.get("related")[0].get("name")
            )
            relationship_fields = load_attrs.get("related")[0].get("fields")
            options += [joinedload(relationship_attr).load_only(*relationship_fields)]
        return options

    def _build_filter_criteria(self):
        if not self.q_filter:
            return []
        criterion = []
        for k, v in self.q_filter.__dict__.items():
            if k in self.RELATED_FIELDS:
                self.joins.append(self.JOIN_DICT[k.split("_")[0]])
            if v is not strawberry.UNSET:
                value = f"%{v}%" if type(v) is str else v
                criterion.append(self.FILTER_CRITERION_DICT[k](value))
        return criterion

    def build(self):
        query = select(AuthorModel)
        options = self._build_options()
        subquery = self._build_filter_criteria()
        for j in self.joins:
            query = query.join(j)
        return query.options(*options).filter(*subquery)


class AuthorQuery(Query):
    FILTER_CRITERION_DICT = {
        "id": AuthorModel.id.like,
        "first_name": AuthorModel.first_name.ilike,
        "middle_name": AuthorModel.middle_name.ilike,
        "last_name": AuthorModel.last_name.ilike,
        "book_title": BookModel.title.ilike,
    }

    RELATED_FIELDS = [
        "book_title",
    ]

    JOIN_DICT = {
        "book": AuthorModel.books,
    }
