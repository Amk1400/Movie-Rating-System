from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Genre(Base):
    """Genre model.

    Attributes:
        id (int): primary key.
        name (str): genre name.
    """

    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(512), nullable=True)

    movie_genres = relationship("MovieGenre", back_populates="genre")
