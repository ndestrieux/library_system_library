from typing import Any, Dict, List, Optional

from sqlalchemy import Select, select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import joinedload, load_only, strategy_options
from sqlalchemy.sql.elements import SQLCoreOperations
from strawberry.types.nodes import SelectedField
from strawberry.utils.str_converters import to_snake_case

from database.db_conf import Base as BaseModel
from database.models import Author as AuthorModel
from database.models import Book as BookModel
from filters.author import Filter

MODEL_QUERY_PARAMS = {
    AuthorModel: {
        "filter_criterion": {
            "first_name": AuthorModel.first_name.ilike,
            "middle_name": AuthorModel.middle_name.ilike,
            "last_name": AuthorModel.last_name.ilike,
            "book_title": BookModel.title.ilike,
        },
        "related_fields": [
            "book_title",
        ],
        "joins": {
            "book": AuthorModel.books,
        },
    }
}


class SQLQuery:
    def __new__(cls, *args, **kwargs):
        kwargs_arr = kwargs.keys()
        if "q_filter" in kwargs_arr and "obj_id" in kwargs_arr:
            raise AttributeError(
                "Query filter and object ID cannot be both passed when building query."
            )
        return super().__new__(cls)

    def __init__(
        self,
        model: BaseModel,
        fields: List[SelectedField],
        *,
        obj_id: Optional[int] = None,
        q_filter: Optional[Filter] = None,
    ):
        self.model = model
        self.fields = fields
        self.obj_id = obj_id
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

    def _build_filter_criteria(self) -> List[SQLCoreOperations]:
        if self.obj_id:
            return [self.model.id.like(self.obj_id)]
        if not self.q_filter:
            return []
        criterion = []
        for k, v in self.q_filter.asdict().items():
            if k in MODEL_QUERY_PARAMS[self.model]["related_fields"]:
                self.joins.append(
                    MODEL_QUERY_PARAMS[self.model]["joins"][k.split("_")[0]]
                )
            value = f"%{v}%" if type(v) is str else v
            criterion.append(
                MODEL_QUERY_PARAMS[self.model]["filter_criterion"][k](value)
            )
        return criterion

    def build(self) -> Select:
        query = select(self.model)
        options = self._build_options()
        subquery = self._build_filter_criteria()
        for j in self.joins:
            query = query.join(j)
        return query.options(*options).filter(*subquery)
