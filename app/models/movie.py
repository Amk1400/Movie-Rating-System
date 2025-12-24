from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Movie(Base):
    """Movie model.

    Attributes:
        id (int): primary key.
        title (str): movie title.
    """

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False)
    director_id = Column(Integer, ForeignKey("directors.id"), nullable=False)
    release_year = Column(Integer, nullable=True)
    cast = Column(String(1024), nullable=True)

    director = relationship("Director", back_populates="movies")
    genres = relationship("MovieGenre", back_populates="movie")
    ratings = relationship("MovieRating", back_populates="movie")
