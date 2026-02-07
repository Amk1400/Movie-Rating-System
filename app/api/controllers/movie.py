from typing import Any, Optional
import logging
import time

from fastapi import APIRouter, Query, HTTPException, FastAPI, Path
from starlette import status

from app.api.schemas.base import ErrorResponse, ErrorDetail
from app.api.schemas.movie import (
    MoviesListResponse,
    MovieDetailResponse,
    MovieCreateResponse,
    MovieCreateRequest,
    MovieUpdateRequest,
    MovieUpdateResponse,
)
from app.exceptions.exceptions import ValidationError, NotFoundError

logger = logging.getLogger("movie_rating")


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
        """Register router endpoints."""

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
            page_size: int = Query(10, ge=1),
            title: Optional[str] = Query(None),
            release_year: Optional[int] = Query(None),
            genre: Optional[str] = Query(None),
        ) -> MoviesListResponse:
            """List movies with pagination and optional filters."""
            route = "/api/v1/movies"
            start = time.perf_counter()

            logger.info(
                "List movies requested (route=%s, page=%s, page_size=%s, title=%s, release_year=%s, genre=%s)",
                route,
                page,
                page_size,
                title,
                release_year,
                genre,
            )

            try:
                data = self._service.get_movies_paginated(
                    page=page,
                    page_size=page_size,
                    title=title,
                    release_year=release_year,
                    genre=genre,
                )

                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.info(
                    "List movies success (route=%s, page=%s, page_size=%s, returned=%s, total_items=%s, duration_ms=%s)",
                    route,
                    page,
                    page_size,
                    len(data.get("items", [])),
                    data.get("total_items"),
                    duration_ms,
                )
                return MoviesListResponse(status="success", data=data)

            except ValidationError as ve:
                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.warning(
                    "List movies validation failed (route=%s, duration_ms=%s, error=%s)",
                    route,
                    duration_ms,
                    str(ve),
                )
                error_detail = ErrorDetail(code=422, message=str(ve))
                error_response = ErrorResponse(status="failure", error=error_detail)
                raise HTTPException(status_code=422, detail=error_response.model_dump())

            except Exception as ex:
                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.error(
                    "List movies failed (route=%s, duration_ms=%s)",
                    route,
                    duration_ms,
                    exc_info=True,
                )
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
            """Get detailed movie by id."""
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

        @self.router.post(
            "/",
            response_model=MovieCreateResponse,
            status_code=status.HTTP_201_CREATED,
            responses={
                201: {"description": "Created"},
                422: {"model": ErrorResponse},
                500: {"description": "Internal server error"},
            },
        )
        async def create_movie(body: MovieCreateRequest) -> MovieCreateResponse:
            """Create a new movie."""
            try:
                data = self._service.create_movie(
                    title=body.title,
                    director_id=body.director_id,
                    release_year=body.release_year,
                    cast=body.cast,
                    genre_ids=body.genres,
                )
                return MovieCreateResponse(status="success", data=data)
            except ValidationError as ve:
                error_detail = ErrorDetail(code=422, message=str(ve))
                error_response = ErrorResponse(status="failure", error=error_detail)
                raise HTTPException(status_code=422, detail=error_response.model_dump())
            except Exception as ex:
                raise HTTPException(status_code=500, detail=str(ex))

        @self.router.put(
            "/{movie_id}",
            response_model=MovieUpdateResponse,
            responses={
                404: {"model": ErrorResponse},
                422: {"model": ErrorResponse},
                500: {"description": "Internal server error"},
            },
        )
        async def update_movie(movie_id: int = Path(..., gt=0), body: MovieUpdateRequest = ...):
            try:
                data = self._service.update_movie(
                    movie_id=movie_id,
                    title=body.title,
                    release_year=body.release_year,
                    cast=body.cast,
                    genre_ids=body.genres,
                )
                return MovieUpdateResponse(status="success", data=data)
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

        @self.router.delete(
            "/{movie_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            responses={
                204: {"description": "No Content"},
                404: {"model": ErrorResponse},
                500: {"description": "Internal server error"},
            },
        )
        async def delete_movie(movie_id: int = Path(..., gt=0)):
            try:
                self._service.delete_movie(movie_id)
                return  # FastAPI returns empty body for 204
            except NotFoundError as nf:
                error_detail = ErrorDetail(code=404, message=str(nf))
                error_response = ErrorResponse(status="failure", error=error_detail)
                raise HTTPException(status_code=404, detail=error_response.model_dump())
            except Exception as ex:
                raise HTTPException(status_code=500, detail=str(ex))

    def register(self, app: FastAPI) -> None:
        """Include the API router into FastAPI app."""
        app.include_router(self.router)