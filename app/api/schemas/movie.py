from typing import List, Optional, Literal

from pydantic import BaseModel

from app.api.schemas.director import DirectorOut


class MovieOut(BaseModel):
    """Movie output schema.

    Attributes:
        id (int): movie id.
        title (str): movie title.
        release_year (Optional[int]): movie release year.
        director (DirectorOut): director info.
        genres (List[str]): list of genre names.
        average_rating (Optional[float]): average rating with one decimal.
    """

    id: int
    title: str
    release_year: Optional[int]
    director: DirectorOut
    genres: List[str]
    average_rating: Optional[float]


class MoviesPageData(BaseModel):
    """Pagination payload for movies.

    Attributes:
        page (int): current page number.
        page_size (int): items per page.
        total_items (int): total movies count.
        items (List[MovieOut]): page items.
    """

    page: int
    page_size: int
    total_items: int
    items: List[MovieOut]


class MoviesListResponse(BaseModel):
    """Top-level movies list response.

    Attributes:
        status (Literal[\"success\",\"error\"]): response status.
        data (MoviesPageData): response data object.
    """

    status: Literal["success", "error"]
    data: MoviesPageData


class MovieDetailResponse(BaseModel):
    """Top-level movie detail response.

    Attributes:
        status (Literal['success']): response status.
        data (MovieDetailOut): movie detail object.
    """
    status: Literal["success"]
    data: MovieOut