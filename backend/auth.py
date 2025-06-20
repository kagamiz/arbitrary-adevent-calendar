from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
import requests
from bs4 import BeautifulSoup
import httpx
import time

from config import settings
from database import get_db
from models import User
from schemas import TokenData

# JWT設定
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTPBearer
security = HTTPBearer()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報を取得できませんでした",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(credentials.credentials, credentials_exception)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(status_code=400, detail="無効なユーザーです")
    return current_user


def get_x_oauth_url() -> str:
    """X OAuth認証URLを生成"""
    base_url = "https://twitter.com/i/oauth2/authorize"
    params = {
        "response_type": "code",
        "client_id": settings.x_client_id,
        "redirect_uri": settings.x_redirect_uri,
        "scope": "tweet.read users.read offline.access",
        "state": "state",
        "code_challenge": "challenge",
        "code_challenge_method": "plain",
    }
    
    # クエリパラメータを構築
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{query_string}"


async def exchange_code_for_token(code: str) -> Optional[dict]:
    """認証コードをアクセストークンと交換"""
    token_url = "https://api.twitter.com/2/oauth2/token"
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.x_redirect_uri,
        "client_id": settings.x_client_id,
        "client_secret": settings.x_client_secret,
        "code_verifier": "challenge",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code == 200:
            return response.json()
        return None


async def get_x_user_info(access_token: str) -> Optional[dict]:
    """X APIからユーザー情報を取得"""
    user_url = "https://api.twitter.com/2/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(user_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            user_data = data.get("data", {})
            return {
                "id": user_data.get("id"),
                "username": user_data.get("username"),
                "name": user_data.get("name"),
                "profile_image_url": user_data.get("profile_image_url"),
            }
        return None


def is_admin_user(username: str) -> bool:
    """ユーザーが管理者かどうかを判定（admin_usernamesで判定）"""
    if os.getenv("ENVIRONMENT") == "local" and username == "mock_user":
        return True
    admin_usernames = settings.admin_user_id_list
    return username in admin_usernames

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager



def get_twitter_profile_info(username: str) -> dict:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0 Safari/537.36")
    options.binary_location = '/usr/bin/chromium'

    driver = webdriver.Chrome(
        service=Service('/usr/local/bin/chromedriver'),
        options=options
    )

    try:
        url = f"https://twitter.com/{username}"
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        # 表示名の要素が現れるのを待つ
        name_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@data-testid="UserName"]//span[1]')
        ))
        display_name = name_elem.text

        # プロフィール画像の要素が現れるのを待つ
        img_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//img[starts-with(@src, "https://pbs.twimg.com/profile_images/")]')
        ))
        profile_image_url = img_elem.get_attribute("src")

        return {
            "username": username,
            "display_name": display_name,
            "profile_image_url": profile_image_url
        }

    finally:
        driver.quit()
