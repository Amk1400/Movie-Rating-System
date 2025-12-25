from typing import Any

from fastapi import APIRouter, Query, HTTPException
from fastapi import FastAPI

from app.api.schemas.movie import MoviesListResponse
from app.exceptions.exceptions import ValidationError


class MovieAPI:
    """Movie API router holder.

    Attributes:
        router (APIRouter): router exposing movie endpoints.
    """

    def __init__(self, service: Any) -> None:
        """Construct MovieAPI.

        Args:
            service (Any): MovieService instance.

        Returns:
            None: nothing.

        Raises:
            None: simple initializer.
        """
        self._service = service
        self.router = APIRouter(prefix="/api/v1/movies", tags=["movies"])
        self._register_routes()

    def _register_routes(self) -> None:
        """Register router endpoints.

        Returns:
            None: nothing.

        Raises:
            None: internal registration.
        """

        @self.router.get(
            "/",
            response_model=MoviesListResponse,
            responses={
                400: {"description": "Validation error"},
                500: {"description": "Internal server error"},
            },
        )
        async def list_movies(
            page: int = Query(1, ge=1),
            page_size: int = Query(10, ge=1, le=100),
        ) -> MoviesListResponse:
            """List movies with pagination.

            Args:
                page (int): page number.
                page_size (int): items per page.

            Returns:
                MoviesListResponse: paginated movies response.

            Raises:
                HTTPException: on validation or internal errors.
            """
            try:
                data = self._service.get_movies_paginated(page=page, page_size=page_size)
                return MoviesListResponse(status="success", data=data)
            except ValidationError as ve:
                raise HTTPException(status_code=400, detail=str(ve))
            except Exception as ex:
                raise HTTPException(status_code=500, detail=f"internal server error: {str(ex)}")

    def register(self, app: FastAPI) -> None:
        """Include the API router into FastAPI app.

        Args:
            app (FastAPI): FastAPI application.

        Returns:
            None: nothing.

        Raises:
            None: simple include.
        """
        app.include_router(self.router)