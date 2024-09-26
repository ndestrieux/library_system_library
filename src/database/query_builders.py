from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import Select, select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import joinedload, load_only, strategy_options
from sqlalchemy.sql.elements import SQLCoreOperations
from strawberry.types.nodes import SelectedField
from strawberry.utils.str_converters import to_snake_case

from database.models import Author as AuthorModel
from database.models import BaseModel
from database.models import Book as BookModel
from filters.author import Filter


class SQLQuery(ABC):
    MODEL = None
    POSSIBLE_FILTER_ARGS = ["obj_id", "q_filter"]

    def __new__(cls, *args, **kwargs):
        kwargs_arr = tuple(kwargs.keys())
        if len(list(set(cls.POSSIBLE_FILTER_ARGS) & set(kwargs_arr))) > 1:
            raise AttributeError(
                f"Only one arg of '{kwargs_arr}' can be passed when building query."
            )
        return super().__new__(cls)

    def __init__(
        self,
        fields: Optional[List[SelectedField]] = None,
        *,
        obj_id: Optional[int] = None,
        q_filter: Optional[Filter] = None,
    ):
        self.fields = fields
        self.obj_id = obj_id
        self.q_filter = q_filter
        self.joins = []

    @property
    @abstractmethod
    def _get_filter_criteria(self) -> Dict:
        pass

    @property
    @abstractmethod
    def _get_related_fields(self) -> List:
        pass

    @property
    @abstractmethod
    def _get_join(self) -> Dict:
        pass

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
        load_attrs = self._get_model_field_objs(self.MODEL, self.fields)
        options = [load_only(*load_attrs["fields"])]
        if load_attrs.get("related"):
            relationship_attr = getattr(
                self.MODEL, load_attrs.get("related")[0].get("name")
            )
            relationship_fields = load_attrs.get("related")[0].get("fields")
            options += [joinedload(relationship_attr).load_only(*relationship_fields)]
        return options

    @staticmethod
    def _format_query_value(value: Any) -> Tuple:
        match value:
            case str():
                return (f"%{value}%",)
            case dict():
                return value.get("from_"), value.get("to_")
            case _:
                return (value,)

    def _build_filter_criteria(self) -> List[SQLCoreOperations]:
        if self.obj_id:
            return [self.MODEL.id.like(self.obj_id)]
        if not self.q_filter:
            return []
        criterion = []
        for k, v in self.q_filter.asdict().items():
            if k in self._get_related_fields:
                self.joins.append(self._get_join[k.split("_")[0]])
            criterion.append(self._get_filter_criteria[k](*self._format_query_value(v)))
        return criterion

    def build(self) -> Select:
        query = select(self.MODEL)
        subquery = self._build_filter_criteria()
        for j in self.joins:
            query = query.join(j)
        if self.fields:
            options = self._build_options()
            query = query.options(*options)
        return query.filter(*subquery)


class AuthorSQLQuery(SQLQuery):
    MODEL = AuthorModel

    @property
    def _get_filter_criteria(self):
        return {
            "first_name": AuthorModel.first_name.ilike,
            "middle_name": AuthorModel.middle_name.ilike,
            "last_name": AuthorModel.last_name.ilike,
            "book_title": BookModel.title.ilike,
            "book_publication_year": BookModel.publication_year.like,
            "created_by": AuthorModel.created_by.ilike,
            "created_between": AuthorModel.created_on.between,
            "last_updated_by": AuthorModel.last_updated_by.ilike,
            "last_updated_between": AuthorModel.last_updated_on.between,
        }

    @property
    def _get_related_fields(self):
        return [
            "book_title",
            "book_publication_year",
        ]

    @property
    def _get_join(self):
        return {
            "book": AuthorModel.books,
        }


class BookSQLQuery(SQLQuery):
    MODEL = BookModel

    @property
    def _get_filter_criteria(self):
        return {
            "title": BookModel.title.ilike,
            "publication_year": BookModel.publication_year.like,
            "language": BookModel.language.like,
            "category": BookModel.category.ilike,
            "created_by": BookModel.created_by.ilike,
            "created_between": BookModel.created_on.between,
            "last_updated_by": BookModel.last_updated_by.ilike,
            "last_updated_between": BookModel.last_updated_on.between,
            "author_first_name": AuthorModel.first_name.ilike,
            "author_middle_name": AuthorModel.middle_name.ilike,
            "author_last_name": AuthorModel.last_name.ilike,
        }

    @property
    def _get_related_fields(self):
        return [
            "author_first_name",
            "author_middle_name",
            "author_last_name",
        ]

    @property
    def _get_join(self):
        return {
            "author": BookModel.authors,
        }
