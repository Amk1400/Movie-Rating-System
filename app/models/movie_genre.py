from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class MovieGenre(Base):
    """Association between movie and genre.

    Attributes:
        movie_id (int): FK to movies.id.
        genre_id (int): FK to genres.id.
    """

    __tablename__ = "movie_genres"
    __table_args__ = (UniqueConstraint("movie_id", "genre_id", name="uix_movie_genre"),)

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)

    movie = relationship("Movie", back_populates="genres")
    genre = relationship("Genre", back_populates="movie_genres")
