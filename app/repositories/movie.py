from typing import Any, Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

from app.repositories.base import BaseRepository
from app.models import Movie, MovieGenre, MovieRating


class MovieRepository(BaseRepository):
    """Repository for movie-related DB access."""

    def __init__(self, session_factory: Any) -> None:
        super().__init__(session_factory)

    def count_all(self) -> int:
        with self._session_factory() as session:
            total = session.query(func.count(Movie.id)).scalar()
            return int(total)

    def list_paginated(self, page: int, page_size: int) -> Tuple[List[Dict[str, Any]], int]:
        if page <= 0 or page_size <= 0:
            raise ValueError("page and page_size must be positive integers")

        offset = (page - 1) * page_size

        with self._session_factory() as session:
            movies = (
                session.query(Movie)
                .options(
                    joinedload(Movie.director),  # scalar relationship ok with joinedload
                    selectinload(Movie.genres).joinedload(MovieGenre.genre),  # collection -> selectinload then join inner assoc->genre
                )
                .order_by(Movie.id)
                .offset(offset)
                .limit(page_size)
                .all()
            )

            movie_ids = [m.id for m in movies]
            ratings = {}
            if movie_ids:
                rows = (
                    session.query(MovieRating.movie_id, func.avg(MovieRating.score).label("avg"))
                    .filter(MovieRating.movie_id.in_(movie_ids))
                    .group_by(MovieRating.movie_id)
                    .all()
                )
                ratings = {r.movie_id: float(r.avg) for r in rows}

            items: List[Dict[str, Any]] = []
            for m in movies:
                genre_names: List[str] = []
                # m.genres is a list of MovieGenre instances (association-object)
                for mg in m.genres:
                    if mg is not None and getattr(mg, "genre", None) is not None:
                        g = mg.genre
                        if getattr(g, "name", None) is not None:
                            genre_names.append(g.name)
                director_dict = {"id": getattr(m.director, "id", None), "name": getattr(m.director, "name", None)}
                avg = ratings.get(m.id)
                items.append(
                    {
                        "id": m.id,
                        "title": m.title,
                        "release_year": m.release_year,
                        "director": director_dict,
                        "genres": genre_names,
                        "average_rating": avg,
                    }
                )

            total_items = self.count_all()
            return items, int(total_items)
