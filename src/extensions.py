from strawberry.extensions import SchemaExtension

from database.db_conf import SessionLocal


class SQLAlchemySession(SchemaExtension):
    def on_operation(self):
        self.execution_context.context["db"] = SessionLocal()
        yield
        self.execution_context.context["db"].close()
