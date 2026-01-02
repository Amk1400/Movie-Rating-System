from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

from app.repositories.base import BaseRepository
from app.models import Genre, Movie, MovieGenre, MovieRating


class MovieRepository(BaseRepository):
    """Repository for movie-related DB access.

    Attributes:
        _session_factory (Any): session factory.
    """

    def __init__(self, session_factory: Any) -> None:
        """Construct MovieRepository.

        Args:
            session_factory (Any): sessionmaker or factory.

        Returns:
            None: nothing.

        Raises:
            None: initializer.
        """
        super().__init__(session_factory)

    def _apply_filters(
        self,
        query,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genre: Optional[str] = None,
    ):
        """Apply title/release_year/genre filters to a SQLAlchemy query.

        Args:
            query: SQLAlchemy query object.
            title (Optional[str]): partial title to match.
            release_year (Optional[int]): exact release year.
            genre (Optional[str]): exact genre name.

        Returns:
            Any: modified query.

        Raises:
            None: no runtime raise.
        """
        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        if release_year is not None:
            query = query.filter(Movie.release_year == release_year)
        if genre:
            query = query.join(Movie.genres).join(MovieGenre.genre).filter(Genre.name == genre)
        return query

    def list_paginated(
        self,
        page: int,
        page_size: int,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genre: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return paginated movies and total count with optional filters.

        Args:
            page (int): page number.
            page_size (int): items per page.
            title (Optional[str]): partial title to search.
            release_year (Optional[int]): filter by release year.
            genre (Optional[str]): filter by genre name.

        Returns:
            Tuple[List[Dict[str, Any]], int]: list of raw items and total count.

        Raises:
            ValueError: if page or page_size invalid.
        """
        offset = (page - 1) * page_size

        with self._session_factory() as session:
            base_q = session.query(Movie)
            base_q = base_q.options(
                joinedload(Movie.director),
                selectinload(Movie.genres).joinedload(MovieGenre.genre),
            )

            filtered_q = self._apply_filters(base_q, title=title, release_year=release_year, genre=genre)

            total_q = session.query(func.count(func.distinct(Movie.id)))
            total_q = self._apply_filters(total_q.select_from(Movie), title=title, release_year=release_year, genre=genre)
            total_items = int(total_q.scalar() or 0)

            movies_query = filtered_q.order_by(Movie.id).distinct(Movie.id).offset(offset).limit(page_size)
            movies = movies_query.all()

            movie_ids = [m.id for m in movies]
            ratings: Dict[int, float] = {}
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
                for mg in m.genres:
                    g = getattr(mg, "genre", None)
                    if g is not None and getattr(g, "name", None) is not None:
                        genre_names.append(g.name)
                director_dict = {
                    "id": getattr(m.director, "id", None),
                    "name": getattr(m.director, "name", None),
                }
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

            return items, total_items
