from strawberry.extensions import SchemaExtension

from database import SessionLocal


class SQLAlchemySession(SchemaExtension):
    def on_request_start(self):
        self.execution_context.context["db"] = SessionLocal()

    def on_request_end(self):
        self.execution_context.context["db"].close()
