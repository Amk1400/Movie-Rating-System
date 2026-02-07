from typing import AsyncIterator
import os
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.logging_config import setup_logging

from app.db.database import init_engine, close_engine, get_sessionmaker
from app.repositories.director import DirectorRepository
from app.repositories.genre import GenreRepository
from app.repositories.movie import MovieRepository
from app.repositories.rating import RatingRepository
from app.services.director import DirectorService
from app.services.genre import GenreService
from app.services.movie import MovieService
from app.services.rating import RatingService
from app.api.controllers.director import DirectorAPI
from app.api.controllers.genre import GenreAPI
from app.api.controllers.movie import MovieAPI
from app.api.controllers.rating import RatingAPI


class AppState:
    """Typed application state container.

    Attributes:
        director_api (DirectorAPI): director API instance.
        genre_api (GenreAPI): genre API instance.
        movie_api (MovieAPI): movie API instance.
        rating_api (RatingAPI): rating API instance.
    """

    def __init__(
        self,
        director_api: DirectorAPI,
        genre_api: GenreAPI,
        movie_api: MovieAPI,
        rating_api: RatingAPI,
    ) -> None:
        self.director_api = director_api
        self.genre_api = genre_api
        self.movie_api = movie_api
        self.rating_api = rating_api


load_dotenv()
setup_logging()

MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE"))
MIN_RELEASE_YEAR = int(os.getenv("MIN_RELEASE_YEAR"))


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle with manual dependency wiring.

    Args:
        application (FastAPI): application instance.

    Returns:
        AsyncIterator[None]: lifecycle context.
    """
    database_url = os.getenv("DATABASE_URL")
    init_engine(database_url)

    session_factory = get_sessionmaker()

    director_repo = DirectorRepository(session_factory)
    genre_repo = GenreRepository(session_factory)
    movie_repo = MovieRepository(session_factory)
    rating_repo = RatingRepository(session_factory)

    director_service = DirectorService(director_repo)
    genre_service = GenreService(genre_repo)
    movie_service = MovieService(movie_repo, MAX_PAGE_SIZE, MIN_RELEASE_YEAR)
    rating_service = RatingService(rating_repo)

    director_api = DirectorAPI(director_service)
    genre_api = GenreAPI(genre_service)
    movie_api = MovieAPI(movie_service)
    rating_api = RatingAPI(rating_service)

    application.include_router(movie_api.router)
    application.include_router(rating_api.router)

    application.state = AppState(
        director_api=director_api,
        genre_api=genre_api,
        movie_api=movie_api,
        rating_api=rating_api,
    )

    try:
        yield
    finally:
        close_engine()


app = FastAPI(
    title="Movie Rating System - Phase1",
    version="0.1.0",
    lifespan=lifespan,
)

cors_options = {
    "allow_origins": ["*"],
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["*"],
}

app.add_middleware(CORSMiddleware, **cors_options)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)