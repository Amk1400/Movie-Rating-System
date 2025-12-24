from typing import Any


class BaseService:
    """Base service placeholder.

    Attributes:
        _repo (Any): repository instance.
    """

    def __init__(self, repo: Any) -> None:
        """Construct BaseService.

        Args:
            repo (Any): repository instance.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        self._repo = repo
