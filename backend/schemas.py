from pydantic import BaseModel, computed_field
from datetime import date, datetime, timezone, timedelta
from typing import Optional


class UserBase(BaseModel):
    username: str
    display_name: str
    profile_image_url: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    post_date: date
    title: str
    url: str
    description: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class PostReserve(BaseModel):
    post_date: date


class PostPreRegister(BaseModel):
    post_date: str
    username: str


class PostContentUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class Post(BaseModel):
    id: int
    user_id: int
    post_date: date
    title: str
    url: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: User

    @computed_field
    @property
    def is_public(self) -> bool:
        JST = timezone(timedelta(hours=9))
        now = datetime.now(JST)
        publish_time = datetime.combine(
            self.post_date, datetime.min.time().replace(hour=22), tzinfo=JST
        )
        return (
            self.user_id is not None
            and self.title is not None
            and self.title.strip() != ""
            and self.url is not None
            and self.url.strip() != ""
            and now >= publish_time
        )

    class Config:
        from_attributes = True


class PostPublic(BaseModel):
    id: int
    post_date: date
    title: str
    url: str
    description: Optional[str] = None
    user: Optional[User] = None  # 公開されていない場合はNone

    @computed_field
    @property
    def is_public(self) -> bool:
        JST = timezone(timedelta(hours=9))
        now = datetime.now(JST).date()
        return (
            self.user is not None
            and self.title
            and self.title.strip() != ""
            and self.url
            and self.url.strip() != ""
            and self.post_date <= now
        )

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class CalendarInfo(BaseModel):
    start_date: str
    end_date: str
    total_days: int
    calendar_name: str


class OverviewUpdate(BaseModel):
    content: str


class OverviewResponse(BaseModel):
    content: str
