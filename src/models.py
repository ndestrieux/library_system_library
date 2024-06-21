import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table

from database import Base


class LanguageChoices(enum.Enum):
    EN = "English"
    FR = "French"
    PL = "Polish"


book2author_table = Table(
    "book2author",
    Base.metadata,
    Column("book_id", ForeignKey("books.id")),
    Column("authors_id", ForeignKey("authors.id")),
)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=False)
    language = Column(Enum(LanguageChoices), nullable=True)
    category = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
    last_updated_by = Column(String, nullable=False)
    last_updated_on = Column(DateTime, nullable=False)


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False)
    last_updated_by = Column(String, nullable=False)
    last_updated_on = Column(DateTime, nullable=False)
