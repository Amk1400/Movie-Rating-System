from typing import Any, Dict, List

from app.exceptions.exceptions import ValidationError
from app.services.base import BaseService


class MovieService(BaseService):
    """Movie business logic holder.

    Attributes:
        _repo (Any): MovieRepository instance.
    """

    MAX_PAGE_SIZE = 100

    def __init__(self, repo: Any) -> None:
        """Construct MovieService.

        Args:
            repo (Any): repository instance.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(repo)

    def _validate_pagination(self, page: int, page_size: int) -> None:
        """Validate pagination parameters.

        Args:
            page (int): page number.
            page_size (int): items per page.

        Returns:
            None: nothing.

        Raises:
            ValidationError: when pagination values are invalid.
        """
        if page < 1:
            raise ValidationError("page must be >= 1")
        if page_size < 1 or page_size > self.MAX_PAGE_SIZE:
            raise ValidationError(f"page_size must be between 1 and {self.MAX_PAGE_SIZE}")

    def _format_item(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw repository movie into API output shape.

        Args:
            raw (Dict[str, Any]): raw movie dict.

        Returns:
            Dict[str, Any]: formatted movie output.
        """
        avg = raw.get("average_rating")
        average_rating = None if avg is None else round(float(avg), 1)

        return {
            "id": raw["id"],
            "title": raw["title"],
            "release_year": raw.get("release_year"),
            "director": {
                "id": raw["director"]["id"],
                "name": raw["director"]["name"],
            },
            "genres": list(raw.get("genres", [])),
            "average_rating": average_rating,
        }

    def get_movies_paginated(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Return paginated movies payload.

        Args:
            page (int): page number.
            page_size (int): items per page.

        Returns:
            Dict[str, Any]: pagination-compatible movie payload.

        Raises:
            ValidationError: when pagination args are invalid.
            Exception: when repository access fails.
        """
        self._validate_pagination(page, page_size)

        items_raw, total_items = self._repo.list_paginated(page, page_size)
        items: List[Dict[str, Any]] = [self._format_item(i) for i in items_raw]

        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "items": items,
        }
