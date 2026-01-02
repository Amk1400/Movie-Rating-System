from typing import Literal, Optional
from pydantic import BaseModel
from app.api.schemas.base import ErrorResponse  # optional usage elsewhere

class RatingCreateRequest(BaseModel):
    score: int

class RatingOut(BaseModel):
    rating_id: int
    movie_id: int
    score: int
    created_at: Optional[str]

class RatingCreateResponse(BaseModel):
    status: Literal["success"]
    data: RatingOut
