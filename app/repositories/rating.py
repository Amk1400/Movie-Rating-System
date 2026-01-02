from typing import Any, Optional
from datetime import datetime, timezone

from app.repositories.base import BaseRepository
from app.models import Movie, MovieRating

class RatingRepository(BaseRepository):
    def __init__(self, session_factory: Any) -> None:
        super().__init__(session_factory)

    def add_rating(self, movie_id: int, score: int) -> Optional[MovieRating]:
        with self._session_factory() as session:
            movie = session.query(Movie).filter(Movie.id == movie_id).one_or_none()
            if movie is None:
                return None

            rating = MovieRating(
                movie_id=movie_id,
                score=score,
                rated_at=datetime.now(timezone.utc)
            )

            session.add(rating)
            session.commit()
            session.refresh(rating)
            return rating
