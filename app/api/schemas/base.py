from typing import Literal

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Structure for error detail.

    Attributes:
        code (int): HTTP or application error code.
        message (str): human readable message.
    """
    code: int
    message: str


class ErrorResponse(BaseModel):
    """Top-level error response.

    Attributes:
        status (Literal[\"failure\"]): response status.
        error (ErrorDetail): error detail object.
    """
    status: Literal["failure"]
    error: ErrorDetail