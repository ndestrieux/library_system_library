from strawberry.extensions import SchemaExtension

from database import SessionLocal


class SQLAlchemySession(SchemaExtension):
    def on_operation(self):
        self.execution_context.context["db"] = SessionLocal()
        yield
        self.execution_context.context["db"].close()
