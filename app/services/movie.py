from typing import Any, Dict, List, Optional
from datetime import datetime

from app.exceptions.exceptions import ValidationError, NotFoundError
from app.services.base import BaseService


class MovieService(BaseService):
    """Movie business logic holder.

    Attributes:
        _repo (Any): MovieRepository instance.
        _max_page_size (int): maximum allowed page size.
        _min_release_year (int): minimum allowed release year.
    """

    def __init__(self, repo: Any, max_page_size: int, min_release_year: int) -> None:
        """Construct MovieService.

        Args:
            repo (Any): repository instance.
            max_page_size (int): maximum allowed page size.
            min_release_year (int): minimum allowed release year.

        Returns:
            None: nothing.

        Raises:
            None: initializer.
        """
        super().__init__(repo)
        self._max_page_size = max_page_size
        self._min_release_year = min_release_year

    def _validate_pagination(self, page_size: int) -> None:
        """Validate pagination parameters.

        Args:
            page_size (int): items per page.

        Returns:
            None: nothing.

        Raises:
            ValidationError: when pagination values are invalid.
        """
        if page_size > self._max_page_size:
            raise ValidationError(f"page_size must be between 1 and {self._max_page_size}")

    def _validate_release_year(self, release_year: int) -> None:
        """Validate release_year is within allowed historical range.

        Args:
            release_year (int): year to validate.

        Returns:
            None: nothing.

        Raises:
            ValidationError: when year not in [MIN_RELEASE_YEAR, current_year].
        """
        current_year = datetime.now().year
        if release_year < self._min_release_year or release_year > current_year:
            raise ValidationError("Invalid release_year")

    def _format_output(self, raw: Dict[str, Any], detail: bool = False) -> Dict[str, Any]:
        """Common output formatter for movie dicts.

        Args:
            raw (Dict[str, Any]): raw movie dict.
            detail (bool): include full details if True.

        Returns:
            Dict[str, Any]: formatted movie output.

        Raises:
            None: pure formatter.
        """
        avg = raw.get("average_rating")
        average_rating = None if avg is None else round(float(avg), 1)

        director_info = raw.get("director", {})
        director_formatted = {"id": director_info.get("id"), "name": director_info.get("name")}
        if detail:
            director_formatted["birth_year"] = director_info.get("birth_year")
            director_formatted["description"] = director_info.get("description")

        output = {
            "id": raw["id"],
            "title": raw["title"],
            "release_year": raw.get("release_year"),
            "director": director_formatted,
            "genres": list(raw.get("genres", [])),
            "average_rating": average_rating,
        }
        if detail:
            output["cast"] = raw.get("cast")
            output["ratings_count"] = int(raw.get("ratings_count", 0))
        return output

    def get_movies_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genre: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return paginated movies payload with optional filters.

        Args:
            page (int): page number.
            page_size (int): items per page.
            title (Optional[str]): partial title to search.
            release_year (Optional[int]): filter by release year.
            genre (Optional[str]): filter by genre name.

        Returns:
            Dict[str, Any]: pagination-compatible movie payload.

        Raises:
            ValidationError: when pagination or release_year args are invalid.
            Exception: when repository access fails.
        """
        self._validate_pagination(page_size)
        if release_year is not None:
            self._validate_release_year(release_year)

        items_raw, total_items = self._repo.list_paginated(
            page, page_size, title=title, release_year=release_year, genre=genre
        )
        items: List[Dict[str, Any]] = [self._format_output(i) for i in items_raw]

        return {"page": page, "page_size": page_size, "total_items": total_items, "items": items}

    def get_movie_detail(self, movie_id: int) -> Dict[str, Any]:
        """Return detailed movie payload.

        Args:
            movie_id (int): movie id.

        Returns:
            Dict[str, Any]: movie detailed payload.

        Raises:
            NotFoundError: when movie not found.
        """
        raw = self._repo.get_by_id(movie_id)
        if raw is None:
            raise NotFoundError("Movie not found")
        return self._format_output(raw, detail=True)

    def create_movie(
        self,
        title: str,
        director_id: int,
        release_year: Optional[int],
        cast: Optional[str],
        genre_ids: List[int],
    ) -> Dict[str, Any]:
        """Create a new movie after validating inputs.

        Args:
            title (str): movie title.
            director_id (int): director id.
            release_year (Optional[int]): release year.
            cast (Optional[str]): cast string.
            genre_ids (List[int]): list of genre ids.

        Returns:
            Dict[str, Any]: created movie detail payload.

        Raises:
            ValidationError: when input validation fails.
        """
        #if not title or not title.strip():
            #raise ValidationError("title is required")
            #////no need because it is handled by pydantic/////

        self._validate_release_year(release_year)

        if not self._repo.exists_director(director_id):
            raise ValidationError("Invalid director_id or genres")

        #if genre_ids: #////no need because it is handled by pydantic/////
        matched = self._repo.count_genres_by_ids(genre_ids)
        if matched != len(genre_ids):
            raise ValidationError("Invalid director_id or genres")

        raw = self._repo.create_movie(
            title=title, director_id=director_id, release_year=release_year, cast=cast, genre_ids=genre_ids
        )
        return self._format_output(raw, detail=True)

    def update_movie(
        self,
        movie_id: int,
        title: str,
        release_year: int,
        cast: Optional[str],
        genre_ids: List[int],
    ) -> Dict[str, Any]:
        # validate year range
        self._validate_release_year(release_year)

        # validate genres ids exist
        matched = self._repo.count_genres_by_ids(genre_ids)
        if matched != len(genre_ids):
            raise ValidationError("Invalid director_id or genres")

        raw = self._repo.update_movie(
            movie_id=movie_id,
            title=title,
            release_year=release_year,
            cast=cast,
            genre_ids=genre_ids,
        )
        if raw is None:
            raise NotFoundError("Movie not found")

        # doc sample shows updated_at; your DB doesn't store it, so we can add it virtually
        out = self._format_output(raw, detail=True)
        out["updated_at"] = datetime.utcnow().isoformat() + "Z"
        return out

    def delete_movie(self, movie_id: int) -> None:
        ok = self._repo.delete_movie(movie_id)
        if not ok:
            raise NotFoundError("Movie not found")
        
    
