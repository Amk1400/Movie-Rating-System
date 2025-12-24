from typing import Any
from app.repositories.base import BaseRepository


class DirectorRepository(BaseRepository):
    """Repository for director-related DB access.

    Attributes:
        _session_factory (Any): session factory.
    """

    def __init__(self, session_factory: Any) -> None:
        """Construct DirectorRepository.

        Args:
            session_factory (Any): sessionmaker or factory.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(session_factory)
