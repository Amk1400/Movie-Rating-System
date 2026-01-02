from pydantic import BaseModel


class DirectorOut(BaseModel):
    """Director output schema.

    Attributes:
        id (int): director id.
        name (str): director name.
    """

    id: int
    name: str
