from app.services.base import BaseService


class MovieService(BaseService):
    """Movie business logic holder.

    Attributes:
        _repo (Any): MovieRepository instance.
    """

    def __init__(self, repo) -> None:
        """Construct MovieService.

        Args:
            repo: repository instance.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(repo)
