from typing import Optional


class NotFoundError(Exception):
    """Domain-level not found error.

    Attributes:
        message (str): human readable message.
    """

    def __init__(self, message: Optional[str] = "resource not found") -> None:
        """Construct NotFoundError.

        Args:
            message (Optional[str]): error message.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(message)
        self.message = message


class ValidationError(Exception):
    """Domain-level validation error.

    Attributes:
        message (str): human readable message.
    """

    def __init__(self, message: Optional[str] = "validation failed") -> None:
        """Construct ValidationError.

        Args:
            message (Optional[str]): error message.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        super().__init__(message)
        self.message = message
