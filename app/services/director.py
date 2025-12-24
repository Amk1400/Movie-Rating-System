from app.services.base import BaseService


class DirectorService(BaseService):
    """Director business logic holder.

    Attributes:
        _repo (Any): DirectorRepository instance.
    """

    def __init__(self, repo) -> None:
        """Construct DirectorService.

        Args:
            repo: repository instance.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(repo)
