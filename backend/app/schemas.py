from typing import Literal

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    plex_id: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    role: str | None = "user"


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class MediaItem(BaseModel):
    tmdb_id: int
    title: str | None = None
    overview: str | None = None
    poster_url: str | None = None
    media_type: Literal["movie", "tv"] = "movie"


class RecommendationCategory(BaseModel):
    title: str
    reason: str
    items: list[MediaItem]


class RecommendationsResponse(BaseModel):
    movies: list[RecommendationCategory] = []
    tv: list[RecommendationCategory] = []
    documentaries: list[RecommendationCategory] = []


class MediaStatusResponse(BaseModel):
    tmdb_id: int
    status: Literal["missing", "requested", "available", "unknown"] = "unknown"


class RateMediaRequest(BaseModel):
    rating: Literal["up", "down"]
    media_type: Literal["movie", "tv"] = "movie"


class MediaRequestBody(BaseModel):
    media_type: Literal["movie", "tv"] = "movie"


class MessageResponse(BaseModel):
    message: str


from datetime import datetime

class HistoryItem(BaseModel):
    tmdb_id: int
    media_type: str | None = "movie"
    rating: int
    created_at: datetime
    title: str | None = None
    poster_url: str | None = None


class HistoryResponse(BaseModel):
    history: list[HistoryItem]
