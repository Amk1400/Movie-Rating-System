from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class MovieRating(Base):
    """Movie rating model.

    Attributes:
        id (int): primary key.
        score (int): rating score 1-10.
    """

    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    score = Column(Integer, nullable=False)
    rated_at = Column(DateTime(timezone=True), nullable=False)

    movie = relationship("Movie", back_populates="ratings")
