from typing import Any
from app.repositories.base import BaseRepository


class RatingRepository(BaseRepository):
    """Repository for rating-related DB access.

    Attributes:
        _session_factory (Any): session factory.
    """

    def __init__(self, session_factory: Any) -> None:
        """Construct RatingRepository.

        Args:
            session_factory (Any): sessionmaker or factory.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(session_factory)
