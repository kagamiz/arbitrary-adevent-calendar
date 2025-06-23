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
        now = datetime.now(JST)

        # 公開日の22:00を設定
        publish_time = datetime.combine(
            self.post_date, datetime.min.time().replace(hour=22), tzinfo=JST
        )

        # 担当者・タイトル・URLが全て埋まっていて、公開日の22:00を過ぎている
        return (
            self.user_id is not None
            and self.title
            and self.title.strip() != ""
            and self.url
            and self.url.strip() != ""
            and now >= publish_time
        )


class Overview(Base):
    __tablename__ = "overview"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
