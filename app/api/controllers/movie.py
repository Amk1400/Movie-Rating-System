from typing import Any, Optional

from fastapi import APIRouter, Query, HTTPException, FastAPI, Path

from app.api.schemas.base import ErrorResponse, ErrorDetail
from app.api.schemas.movie import MoviesListResponse, MovieDetailResponse
from app.exceptions.exceptions import ValidationError, NotFoundError


class MovieAPI:
    """Movie API router holder."""

    def __init__(self, service: Any) -> None:
        """Construct MovieAPI.

        Args:
            service (Any): MovieService instance.

        Returns:
            None: nothing.
        """
        self._service = service
        self.router = APIRouter(prefix="/api/v1/movies", tags=["movies"])
        self._register_routes()

    def _register_routes(self) -> None:
        """Register router endpoints.

        Returns:
            None: nothing.
        """

        @self.router.get(
            "/",
            response_model=MoviesListResponse,
            responses={
                422: {"model": ErrorResponse},
                500: {"description": "Internal server error"},
            },
        )
        async def list_movies(
            page: int = Query(1, ge=1),
            page_size: int = Query(10, ge=1, le=100),
            title: Optional[str] = Query(None),
            release_year: Optional[int] = Query(None),
            genre: Optional[str] = Query(None),
        ) -> MoviesListResponse:
            """List movies with pagination and optional filters.

            Args:
                page (int): page number.
                page_size (int): items per page.
                title (Optional[str]): partial title to search.
                release_year (Optional[int]): filter by release year.
                genre (Optional[str]): filter by genre name.

            Returns:
                MoviesListResponse: paginated movies response.

            Raises:
                HTTPException: on validation or internal errors.
            """
            try:
                data = self._service.get_movies_paginated(
                    page=page, page_size=page_size, title=title, release_year=release_year, genre=genre
                )
                return MoviesListResponse(status="success", data=data)
            except ValidationError as ve:
                error_detail = ErrorDetail(code=422, message=str(ve))
                error_response = ErrorResponse(status="failure", error=error_detail)
                raise HTTPException(status_code=422, detail=error_response.model_dump())
            except Exception as ex:
                raise HTTPException(status_code=500, detail=str(ex))

        @self.router.get(
            "/{movie_id}",
            response_model=MovieDetailResponse,
            responses={
                404: {"model": ErrorResponse},
                422: {"model": ErrorResponse},
                500: {"description": "Internal server error"},
            },
        )
        async def get_movie(movie_id: int = Path(..., gt=0)) -> MovieDetailResponse:
            """Get detailed movie by id.

            Args:
                movie_id (int): movie id path parameter.

            Returns:
                MovieDetailResponse: detailed movie response.

            Raises:
                HTTPException: on not found or other errors.
            """
            try:
                data = self._service.get_movie_detail(movie_id)
                return MovieDetailResponse(status="success", data=data)
            except NotFoundError as nf:
                error_detail = ErrorDetail(code=404, message=str(nf))
                error_response = ErrorResponse(status="failure", error=error_detail)
                raise HTTPException(status_code=404, detail=error_response.model_dump())
            except ValidationError as ve:
                error_detail = ErrorDetail(code=422, message=str(ve))
                error_response = ErrorResponse(status="failure", error=error_detail)
                raise HTTPException(status_code=422, detail=error_response.model_dump())
            except Exception as ex:
                raise HTTPException(status_code=500, detail=str(ex))

    def register(self, app: FastAPI) -> None:
        """Include the API router into FastAPI app.

        Args:
            app (FastAPI): FastAPI application.

        Returns:
            None: nothing.
        """
        app.include_router(self.router)
