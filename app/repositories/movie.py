from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

from app.repositories.base import BaseRepository
from app.models import Genre, Movie, MovieGenre, MovieRating, Director


class MovieRepository(BaseRepository):
    """Repository for movie-related DB access.

    Attributes:
        _session_factory (Any): session factory.
    """

    def __init__(self, session_factory: Any) -> None:
        """Construct MovieRepository.

        Args:
            session_factory (Any): session maker or factory.

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

    def _format_movie(self, movie: Movie, ratings: dict = None) -> Dict[str, Any]:
        """Format movie with genres, director, and optional average rating.

        Args:
            movie (Movie): SQLAlchemy Movie instance.
            ratings (dict): optional movie_id to average_rating map.

        Returns:
            Dict[str, Any]: formatted movie data.

        Raises:
            None: pure formatter.
        """
        genre_names = [mg.genre.name for mg in movie.genres if mg.genre and mg.genre.name]
        director_dict = {
            "id": movie.director.id if movie.director else None,
            "name": movie.director.name if movie.director else None,
            "birth_year": getattr(movie.director, "birth_year", None),
            "description": getattr(movie.director, "description", None),
        } if getattr(movie, "director", None) else {}

        avg = ratings.get(movie.id) if ratings else None

        return {
            "id": movie.id,
            "title": movie.title,
            "release_year": movie.release_year,
            "cast": getattr(movie, "cast", None),
            "director": director_dict,
            "genres": genre_names,
            "average_rating": float(avg) if avg is not None else None,
            "ratings_count": getattr(movie, "ratings_count", 0),
        }

    def _fetch_movies_with_ratings(self, session, movies: List[Movie]) -> List[Dict[str, Any]]:
        """Fetch related ratings and format movies for given list.

        Args:
            session: SQLAlchemy session.
            movies (List[Movie]): list of Movie instances.

        Returns:
            List[Dict[str, Any]]: formatted movie dicts.

        Raises:
            None: pure fetch/format.
        """
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

        for m in movies:
            if not hasattr(m, "ratings_count"):
                row_count = session.query(func.count(MovieRating.id)).filter(MovieRating.movie_id == m.id).scalar()
                m.ratings_count = int(row_count or 0)

        return [self._format_movie(m, ratings) for m in movies]

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
            Tuple[List[Dict[str, Any]], int]: list of formatted movies and total count.

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

            movies = filtered_q.order_by(Movie.id).distinct(Movie.id).offset(offset).limit(page_size).all()

            items = self._fetch_movies_with_ratings(session, movies)
            return items, total_items

    def get_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Fetch single movie by id with related metadata.

        Args:
            movie_id (int): movie primary key.

        Returns:
            Optional[Dict[str, Any]]: formatted movie dict or None.

        Raises:
            None: returns None if not found.
        """
        with self._session_factory() as session:
            movie = (
                session.query(Movie)
                .options(
                    joinedload(Movie.director),
                    selectinload(Movie.genres).joinedload(MovieGenre.genre),
                )
                .filter(Movie.id == movie_id)
                .one_or_none()
            )
            if not movie:
                return None

            row = session.query(
                func.avg(MovieRating.score).label("avg"),
                func.count(MovieRating.id).label("count"),
            ).filter(MovieRating.movie_id == movie_id).one()

            movie.ratings_count = int(row.count or 0)

            items = self._fetch_movies_with_ratings(session, [movie])
            return items[0] if items else None

    def create_movie(
        self,
        title: str,
        director_id: int,
        release_year: Optional[int],
        cast: Optional[str],
        genre_ids: List[int],
    ) -> Dict[str, Any]:
        """Create movie record and association rows.

        Args:
            title (str): movie title.
            director_id (int): director id.
            release_year (Optional[int]): release year.
            cast (Optional[str]): cast string.
            genre_ids (List[int]): list of genre ids.

        Returns:
            Dict[str, Any]: formatted created movie dict.

        Raises:
            None: caller validates inputs.
        """
        with self._session_factory() as session:
            movie = Movie(title=title, director_id=director_id, release_year=release_year, cast=cast)
            session.add(movie)
            session.flush()

            if genre_ids:
                for gid in genre_ids:
                    mg = MovieGenre(movie_id=movie.id, genre_id=gid)
                    session.add(mg)

            session.commit()
            return self.get_by_id(movie.id)

    def exists_director(self, director_id: int) -> bool:
        """Return True if director with id exists.

        Args:
            director_id (int): director id.

        Returns:
            bool: existence flag.

        Raises:
            None: simple check.
        """
        with self._session_factory() as session:
            return session.query(Director).filter(Director.id == director_id).first() is not None

    def count_genres_by_ids(self, genre_ids: List[int]) -> int:
        """Return number of genres that match provided ids.

        Args:
            genre_ids (List[int]): list of genre ids.

        Returns:
            int: matched genres count.

        Raises:
            None: simple count.
        """
        if not genre_ids:
            return 0
        with self._session_factory() as session:
            return session.query(func.count(Genre.id)).filter(Genre.id.in_(genre_ids)).scalar() or 0
