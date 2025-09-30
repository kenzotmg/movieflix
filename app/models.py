from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, SmallInteger, ForeignKey, CheckConstraint
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    genre: Mapped[str] = mapped_column(String, nullable=False)

    ratings: Mapped[List["Rating"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 10", name="ck_rating_1_10"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    movie: Mapped[Movie] = relationship(back_populates="ratings")
