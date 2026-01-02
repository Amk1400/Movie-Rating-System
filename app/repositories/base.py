from typing import Any


class BaseRepository:
    """Abstract base repository placeholder.

    Attributes:
        _session_factory (Any): session factory.
    """

    def __init__(self, session_factory: Any) -> None:
        """Construct base repository with session factory.

        Args:
            session_factory (Any): sessionmaker or factory.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        self._session_factory = session_factory
