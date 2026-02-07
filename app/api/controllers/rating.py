from typing import Any
import logging
import time

from fastapi import APIRouter, HTTPException, Path
from starlette import status

from app.api.schemas.base import ErrorResponse, ErrorDetail
from app.api.schemas.rating import RatingCreateRequest, RatingCreateResponse
from app.exceptions.exceptions import ValidationError, NotFoundError

logger = logging.getLogger("movie_rating")


class RatingAPI:
    def __init__(self, service: Any) -> None:
        self._service = service
        self.router = APIRouter(prefix="/api/v1/movies", tags=["ratings"])
        self._register_routes()

    def _register_routes(self) -> None:
        @self.router.post(
            "/{movie_id}/ratings/",
            response_model=RatingCreateResponse,
            status_code=status.HTTP_201_CREATED,
            responses={
                201: {"description": "Created"},
                404: {"model": ErrorResponse},
                422: {"model": ErrorResponse},
                500: {"description": "Internal server error"},
            },
        )
        async def add_rating(movie_id: int = Path(..., gt=0), body: RatingCreateRequest = ...):
            route = f"/api/v1/movies/{movie_id}/ratings/"
            start = time.perf_counter()

            logger.info(
                "Rating movie (movie_id=%s, rating=%s, route=%s)",
                movie_id,
                body.score,
                route,
            )

            try:
                data = self._service.add_rating(movie_id=movie_id, score=body.score)

                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.info(
                    "Rating saved successfully (movie_id=%s, rating=%s, duration_ms=%s)",
                    movie_id,
                    body.score,
                    duration_ms,
                )
                return RatingCreateResponse(status="success", data=data)

            except NotFoundError as nf:
                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.warning(
                    "Rating target movie not found (movie_id=%s, rating=%s, duration_ms=%s)",
                    movie_id,
                    body.score,
                    duration_ms,
                )
                error_detail = ErrorDetail(code=404, message=str(nf))
                error_response = ErrorResponse(status="failure", error=error_detail)
                raise HTTPException(status_code=404, detail=error_response.model_dump())

            except ValidationError as ve:
                duration_ms = int((time.perf_counter() - start) * 1000)
                logger.warning(
                    "Invalid rating value (movie_id=%s, rating=%s, route=%s, duration_ms=%s, error=%s)",
                    movie_id,
                    body.score,
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
                    "Failed to save rating (movie_id=%s, rating=%s, duration_ms=%s)",
                    movie_id,
                    body.score,
                    duration_ms,
                    exc_info=True,
                )
                raise HTTPException(status_code=500, detail=str(ex))