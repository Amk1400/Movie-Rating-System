from app.services.base import BaseService


class RatingService(BaseService):
    """Rating business logic holder.

    Attributes:
        _repo (Any): RatingRepository instance.
    """

    def __init__(self, repo) -> None:
        """Construct RatingService.

        Args:
            repo: repository instance.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(repo)
