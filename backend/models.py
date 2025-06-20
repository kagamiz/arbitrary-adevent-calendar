from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    display_name = Column(String)
    profile_image_url = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    posts = relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_date = Column(Date, index=True)
    title = Column(String)
    url = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    user = relationship("User", back_populates="posts")

    @property
    def is_public(self):
        JST = timezone(timedelta(hours=9))
        now = datetime.now(JST).date()
        # 担当者・タイトル・URLが全て埋まっていて、公開日を過ぎている
        return (
            self.user_id is not None and
            self.title and self.title.strip() != "" and
            self.url and self.url.strip() != "" and
            self.post_date <= now
        )
