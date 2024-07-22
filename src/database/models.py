import enum
from datetime import datetime
from typing import List, Optional, TypeAlias

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db_conf import Base

Model: TypeAlias = Base


class LanguageChoices(enum.Enum):
    EN = "English"
    FR = "French"
    PL = "Polish"


book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", ForeignKey("books.id")),
    Column("authors_id", ForeignKey("authors.id")),
)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    authors: Mapped[List["Author"]] = relationship(
        "Author", secondary=book_authors, back_populates="books"
    )
    publication_year: Mapped[int]
    language: Mapped[LanguageChoices]
    category: Mapped[Optional[str]] = mapped_column(String(20), default=None)
    created_by: Mapped[str] = mapped_column(String(20))
    created_on: Mapped[datetime] = mapped_column(insert_default=datetime.now)
    last_updated_by: Mapped[Optional[str]] = mapped_column(String(20))
    last_updated_on: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.now)


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(120))
    middle_name: Mapped[Optional[str]] = mapped_column(String(120), default=None)
    last_name: Mapped[str] = mapped_column(String(120))
    books: Mapped[List["Book"]] = relationship(
        "Book", secondary=book_authors, back_populates="authors"
    )
    created_by: Mapped[str] = mapped_column(String(20))
    created_on: Mapped[datetime] = mapped_column(insert_default=datetime.now)
    last_updated_by: Mapped[Optional[str]] = mapped_column(String(20))
    last_updated_on: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.now)