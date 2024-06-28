from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    GUEST = "Guest"
    PLAYER = "Player"
    ADMINISTRATOR = "Administrator"
    NANNY_MODERATOR = "NannyModerator"
    REGULAR_MODERATOR = "RegularModerator"
    SENIOR_MODERATOR = "SeniorModerator"


class BbParseMode(str, Enum):
    COMMON = 'Common'
    INFO = 'Info'
    POST = 'Post'
    CHAT = 'Chat'


class Rating(BaseModel):
    enabled: bool
    quality: int
    quantity: int


class Info(BaseModel):
    value: str
    parse_mode: str = Field(None, alias='parseMode')


class Paging(BaseModel):
    posts_per_page: int = Field(..., alias='postsPerPage')
    comments_per_page: int = Field(..., alias='commentsPerPage')
    topics_per_page: int = Field(..., alias='topicsPerPage')
    messages_per_page: int = Field(..., alias='messagesPerPage')
    entities_per_page: int = Field(..., alias='entitiesPerPage')


class ColorSchema(str, Enum):
    MODERN = 'Modern'
    PALE = 'Pale'
    CLASSIC = 'Classic'
    CLASSIC_PALE = 'ClassicPale'
    NIGHT = 'Night'


class Settings(BaseModel):
    color_schema: str = Field(None, alias='color_schema')
    nanny_greetings_message: str = Field(None, alias='nannyGreetingsMessage')
    paging: Paging


class User(BaseModel):
    login: str
    roles: List[UserRole]
    medium_picture_url: str = Field(None, alias='mediumPictureUrl')
    small_picture_url: str = Field(None, alias='smallPictureUrl')
    status: str = Field(None, alias='status')
    rating: Rating
    online: datetime = Field(None, alias='online')
    name: str = Field(None, alias='name')
    location: str = Field(None, alias='location')
    registration: datetime = Field(None, alias='registration')
    icq: str = Field(None, alias='icq')
    skype: str = Field(None, alias='skype')
    original_picture_url: str = Field(None, alias='originalPictureUrl')
    info: str
    settings: Settings


class UserDetailsEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource: Optional[User] = None
    metadata: Optional[str] = None
