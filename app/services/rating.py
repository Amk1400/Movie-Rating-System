from typing import Any, Dict
from app.exceptions.exceptions import NotFoundError, ValidationError

class RatingService:
    """Business logic for route 7 (post rating)."""

    def __init__(self, repo: Any) -> None:
        self._repo = repo

    def add_rating(self, movie_id: int, score: int) -> Dict[str, Any]:
        if not isinstance(score, int) or score < 1 or score > 10:
            raise ValidationError("Score must be an integer between 1 and 10")

        rating = self._repo.add_rating(movie_id, score)
        if rating is None:
            raise NotFoundError("Movie not found")

        created_at = rating.rated_at.isoformat() if rating.rated_at is not None else None
        return {
            "rating_id": rating.id,
            "movie_id": rating.movie_id,
            "score": rating.score,
            "created_at": created_at,
        }
