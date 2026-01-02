from app.services.base import BaseService


class GenreService(BaseService):
    """Genre business logic holder.

    Attributes:
        _repo (Any): GenreRepository instance.
    """

    def __init__(self, repo) -> None:
        """Construct GenreService.

        Args:
            repo: repository instance.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(repo)
