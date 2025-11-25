from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    plex_id = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    thumb = Column(String, nullable=True)
    auth_token = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    tautulli_user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recommendations = relationship("RecommendationCache", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")

class RecommendationCache(Base):
    __tablename__ = "recommendation_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recommendations = Column(Text) # JSON blob
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="recommendations")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tmdb_id = Column(Integer, index=True)
    media_type = Column(String) # 'movie' or 'tv'
    rating = Column(Integer) # 1 = Up, -1 = Down, 0 = Seen
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="preferences")


class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
