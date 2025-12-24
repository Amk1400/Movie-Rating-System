from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Director(Base):
    """Director model.

    Attributes:
        id (int): primary key.
        name (str): director name.
    """

    __tablename__ = "directors"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    birth_year = Column(Integer, nullable=True)
    description = Column(String(1024), nullable=True)

    movies = relationship("Movie", back_populates="director")
