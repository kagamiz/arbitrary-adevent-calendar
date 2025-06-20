from pydantic_settings import BaseSettings
from datetime import date
from typing import List
from pydantic import field_validator


class Settings(BaseSettings):
    app_name: str = "アドベントカレンダーAPI"
    app_description: str = "アドベントカレンダー投稿WebアプリのAPI"
    
    # データベース設定
    database_url: str = "sqlite:////db/advent_calendar.db"
    
    # セキュリティ設定
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # X OAuth設定
    x_client_id: str = ""
    x_client_secret: str = ""
    x_redirect_uri: str = "http://localhost:8000/auth/callback"
    x_bearer_token: str = ""
    
    # カレンダー設定（環境変数から読み込み）
    calendar_start_date: date = date(2024, 12, 1)
    calendar_end_date: date = date(2024, 12, 25)
    
    # 管理者ユーザー名（カンマ区切り）
    admin_usernames: str = ""
    
    CALENDAR_NAME: str = "Sample Advent Calendar"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 環境変数名のマッピング
        fields = {
            "calendar_start_date": {"env": "CALENDAR_START_DATE"},
            "calendar_end_date": {"env": "CALENDAR_END_DATE"},
            "admin_usernames": {"env": "ADMIN_USERNAMES"},
        }
    
    @field_validator("calendar_start_date", "calendar_end_date", mode="before")
    @classmethod
    def parse_date(cls, v):
        """日付文字列をdateオブジェクトに変換"""
        if isinstance(v, str):
            return date.fromisoformat(v)
        return v
    
    @property
    def admin_user_id_list(self) -> List[str]:
        """管理者ユーザーIDのリストを取得"""
        if not self.admin_usernames:
            return []
        return [u.strip() for u in self.admin_usernames.split(",") if u.strip()]


settings = Settings()
