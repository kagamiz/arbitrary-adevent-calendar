from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, date, timezone, timedelta
from typing import List, Optional
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from config import settings
from database import get_db, engine
from models import Base, User, Post, Overview
from schemas import (
    User as UserSchema,
    Post as PostSchema,
    PostCreate,
    PostUpdate,
    PostReserve,
    PostPreRegister,
    PostContentUpdate,
    PostPublic,
    Token,
    CalendarInfo,
    OverviewUpdate,
    OverviewResponse,
)
from auth import (
    get_current_active_user,
    get_x_oauth_url,
    exchange_code_for_token,
    get_x_user_info,
    create_access_token,
    is_admin_user,
    get_twitter_profile_info,
)

# データベーステーブルを作成
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name, description=settings.app_description, version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "アドベントカレンダーAPI"}


@app.get("/auth/x/url")
async def get_x_auth_url():
    """X OAuth認証URLを取得"""
    # ローカル環境ではモックURLを返す
    if os.getenv("ENVIRONMENT") == "local":
        return {"auth_url": "http://localhost:8000/auth/mock"}
    return {"auth_url": get_x_oauth_url()}


@app.get("/auth/mock")
async def mock_auth_callback(db: Session = Depends(get_db)):
    """ローカル環境用のモック認証"""
    if os.getenv("ENVIRONMENT") != "local":
        raise HTTPException(status_code=404, detail="Not found")

    # モックユーザーを作成または取得
    user = db.query(User).filter(User.username == "mock_user").first()
    if not user:
        # 管理者判定
        is_admin = is_admin_user("mock_user")
        user = User(
            username="mock_user",
            display_name="モックユーザー",
            profile_image_url=None,
            is_admin=is_admin,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # JWTトークンを生成
    access_token = create_access_token(data={"sub": user.username})

    # フロントエンドにリダイレクト
    return RedirectResponse(
        url=f"http://localhost:3000/auth/success?token={access_token}"
    )


@app.get("/auth/mock2")
async def mock_auth_callback2(db: Session = Depends(get_db)):
    """ローカル環境用のモック認証（管理者権限なしユーザー）"""
    if os.getenv("ENVIRONMENT") != "local":
        raise HTTPException(status_code=404, detail="Not found")
    # モックユーザー２を作成または取得
    user = db.query(User).filter(User.username == "mock_user2").first()
    if not user:
        user = User(
            username="mock_user2",
            display_name="モックユーザー２",
            profile_image_url=None,
            is_admin=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # JWTトークンを生成
    access_token = create_access_token(data={"sub": user.username})
    # フロントエンドにリダイレクト
    return RedirectResponse(
        url=f"http://localhost:3000/auth/success?token={access_token}"
    )


@app.get("/auth/callback")
async def auth_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """X OAuth認証コールバック"""

    # エラーパラメータがある場合はフロントエンドにリダイレクト
    if error:
        print(f"Debug: Auth callback received with error: {error}")
        redirect_url = f"{settings.frontend_url}/?auth_error=login_failed"
        return RedirectResponse(url=redirect_url)

    # codeパラメータがない場合もエラーとして処理
    if not code:
        print("Debug: Auth callback received without code parameter")
        redirect_url = f"{settings.frontend_url}/?auth_error=login_failed"
        return RedirectResponse(url=redirect_url)

    print(f"Debug: Auth callback received with code: {code}")

    # 認証コードをアクセストークンと交換
    token_data = await exchange_code_for_token(code)
    if not token_data:
        print("Debug: Token exchange failed")
        redirect_url = f"{settings.frontend_url}/?auth_error=login_failed"
        return RedirectResponse(url=redirect_url)

    print(f"Debug: Token exchange successful: {token_data}")

    # X APIからユーザー情報を取得
    user_info = await get_x_user_info(token_data["access_token"])
    if not user_info:
        print("Debug: Failed to get user info")
        redirect_url = f"{settings.frontend_url}/?auth_error=login_failed"
        return RedirectResponse(url=redirect_url)

    print(f"Debug: User info retrieved: {user_info}")

    # ユーザーをデータベースに保存または更新
    user = db.query(User).filter(User.username == user_info["username"]).first()
    if not user:
        # 管理者判定
        is_admin = is_admin_user(user_info["username"])
        user = User(
            username=user_info["username"],
            display_name=user_info["name"],
            profile_image_url=user_info.get("profile_image_url"),
            is_admin=is_admin,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Debug: New user created: {user.username}")
    else:
        # 既存ユーザーの管理者権限を更新
        is_admin = is_admin_user(user_info["username"])
        if (
            user.is_admin != is_admin
            or user.profile_image_url != user_info.get("profile_image_url")
            or user.display_name != user_info.get("name")
        ):
            user.is_admin = is_admin
            user.profile_image_url = user_info.get("profile_image_url")
            user.display_name = user_info.get("name")
            db.commit()
            db.refresh(user)
        print(f"Debug: Existing user updated: {user.username}")

    # JWTトークンを生成
    access_token = create_access_token(data={"sub": user.username})
    print(f"Debug: JWT token generated for user: {user.username}")

    # フロントエンドにリダイレクト
    redirect_url = f"{settings.frontend_url}/auth/success?token={access_token}"
    print(f"Debug: Redirecting to: {redirect_url}")

    return RedirectResponse(url=redirect_url)


@app.get("/debug/config")
async def debug_config():
    """デバッグ用：現在の設定値を表示"""
    return {
        "calendar_start_date": settings.calendar_start_date,
        "calendar_end_date": settings.calendar_end_date,
        "admin_user_ids": settings.admin_user_ids,
        "admin_user_id_list": settings.admin_user_id_list,
        "environment": os.getenv("ENVIRONMENT"),
    }


@app.get("/calendar/info", response_model=CalendarInfo)
def get_calendar_info():
    start_date = settings.calendar_start_date
    end_date = settings.calendar_end_date
    total_days = (end_date - start_date).days + 1
    return CalendarInfo(
        start_date=str(start_date),
        end_date=str(end_date),
        total_days=total_days,
        calendar_name=settings.CALENDAR_NAME,
    )


@app.get("/posts/public", response_model=List[PostPublic])
async def get_public_posts(db: Session = Depends(get_db)):
    """投稿一覧を取得（未ログイン時用、公開済みの投稿のみ）"""
    posts = (
        db.query(Post)
        .filter(
            Post.post_date >= settings.calendar_start_date,
            Post.post_date <= settings.calendar_end_date,
        )
        .all()
    )

    result = []
    for post in posts:
        if post.is_public:
            result.append(
                PostPublic(
                    id=post.id,
                    post_date=post.post_date,
                    title=post.title,
                    url=post.url,
                    description=post.description,
                    user=post.user,
                    is_public=True,
                )
            )
        else:
            result.append(
                PostPublic(
                    id=post.id,
                    post_date=post.post_date,
                    title="？？？",
                    url="",
                    description="？？？",
                    user=None,
                    is_public=False,
                )
            )
    return result


@app.post("/posts", response_model=PostSchema)
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """投稿を作成"""
    # 投稿日がカレンダー期間内かチェック
    if (
        post.post_date < settings.calendar_start_date
        or post.post_date > settings.calendar_end_date
    ):
        raise HTTPException(status_code=400, detail="投稿日がカレンダー期間外です")

    # 既にその日に投稿があるかチェック
    existing_post = db.query(Post).filter(Post.post_date == post.post_date).first()
    if existing_post:
        raise HTTPException(
            status_code=400, detail="その日は既に投稿が予約されています"
        )

    db_post = Post(**post.dict(), user_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.post("/posts/reserve", response_model=PostSchema)
async def reserve_post(
    post_reserve: PostReserve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """担当者を予約（記事情報なしで）"""
    # 投稿日がカレンダー期間内かチェック
    if (
        post_reserve.post_date < settings.calendar_start_date
        or post_reserve.post_date > settings.calendar_end_date
    ):
        raise HTTPException(status_code=400, detail="投稿日がカレンダー期間外です")

    # トランザクションを使用して競合状態を防ぐ
    try:
        # 既にその日に投稿があるかチェック
        existing_post = (
            db.query(Post).filter(Post.post_date == post_reserve.post_date).first()
        )
        if existing_post:
            raise HTTPException(
                status_code=400, detail="その日は既に投稿が予約されています"
            )

        # 空の記事情報で投稿を作成
        db_post = Post(
            post_date=post_reserve.post_date,
            title="",
            url="",
            description="",
            user_id=current_user.id,
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail="予約に失敗しました")


@app.put("/posts/{post_id}/content", response_model=PostSchema)
async def update_post_content(
    post_id: int,
    content_update: PostContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """記事情報を更新（タイトル、URL、説明のみ）"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")

    # 投稿者本人または管理者のみ更新可能
    if db_post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="権限がありません")

    # 記事情報のみ更新
    for field, value in content_update.dict(exclude_unset=True).items():
        setattr(db_post, field, value)

    db.commit()
    db.refresh(db_post)
    return db_post


@app.put("/posts/{post_id}", response_model=PostSchema)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """投稿を更新"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")

    # 投稿者本人または管理者のみ更新可能
    if db_post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="権限がありません")

    for field, value in post_update.dict(exclude_unset=True).items():
        setattr(db_post, field, value)

    db.commit()
    db.refresh(db_post)
    return db_post


@app.post("/posts/{post_id}/publish")
async def publish_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """投稿を公開"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")

    # 投稿者本人または管理者のみ公開可能
    if db_post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="権限がありません")

    # is_publicは動的に計算されるため、データベースには保存しない
    db.commit()
    db.refresh(db_post)
    return db_post


@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """投稿を削除"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")

    # 投稿者本人または管理者のみ削除可能
    if db_post.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="権限がありません")

    db.delete(db_post)
    db.commit()
    return {"message": "投稿を削除しました"}


@app.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """現在のユーザー情報を取得"""
    return current_user


@app.get("/posts", response_model=List[PostSchema])
async def get_posts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """投稿一覧を取得（認証済みユーザー用、全投稿）"""
    posts = (
        db.query(Post)
        .filter(
            Post.post_date >= settings.calendar_start_date,
            Post.post_date <= settings.calendar_end_date,
        )
        .all()
    )
    return posts


@app.get("/debug/posts")
async def debug_posts(db: Session = Depends(get_db)):
    """デバッグ用：投稿の詳細情報を表示"""
    posts = (
        db.query(Post)
        .filter(
            Post.post_date >= settings.calendar_start_date,
            Post.post_date <= settings.calendar_end_date,
        )
        .all()
    )

    result = []
    for post in posts:
        result.append(
            {
                "id": post.id,
                "post_date": str(post.post_date),
                "title": post.title,
                "url": post.url,
                "user_id": post.user_id,
                "user_display_name": post.user.display_name if post.user else None,
                "is_public": post.is_public,
                "has_title": bool(post.title and post.title.strip()),
                "has_url": bool(post.url and post.url.strip()),
                "has_user": post.user_id is not None,
                "date_passed": post.post_date
                <= datetime.now(timezone(timedelta(hours=9))).date(),
            }
        )

    return result


@app.post("/posts/pre-register")
async def pre_register_post(
    pre_register: PostPreRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """事前登録：日付とXユーザーIDを指定して投稿を予約（ユーザー名やアイコンは空でOK）"""
    # 管理者のみ実行可能
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="管理者のみ実行可能です")

    # 投稿日をdate型に変換
    try:
        post_date_obj = datetime.strptime(pre_register.post_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400, detail="日付形式が正しくありません (YYYY-MM-DD)"
        )

    # 投稿日がカレンダー期間内かチェック
    if (
        post_date_obj < settings.calendar_start_date
        or post_date_obj > settings.calendar_end_date
    ):
        raise HTTPException(status_code=400, detail="投稿日がカレンダー期間外です")

    # 既にその日に投稿があるかチェック
    existing_post = db.query(Post).filter(Post.post_date == post_date_obj).first()
    if existing_post:
        raise HTTPException(
            status_code=400, detail="その日は既に投稿が予約されています"
        )
    user = db.query(User).filter(User.username == pre_register.username).first()
    if not user:
        is_admin = is_admin_user(pre_register.username)
        user = User(
            username=pre_register.username,
            display_name="",
            profile_image_url=None,
            is_admin=is_admin,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    # 既存ユーザーがいる場合は情報を更新
    try:
        twitter_profile_info = get_twitter_profile_info(pre_register.username)
        user.display_name = twitter_profile_info["display_name"]
        user.profile_image_url = twitter_profile_info["profile_image_url"]
        user.is_admin = is_admin_user(pre_register.username)
        db.commit()
        db.refresh(user)
    except Exception as e:
        print("[WARNING] Twitter profile info の取得に失敗しました。")
        print(e)

    # 空の記事情報で投稿を作成
    db_post = Post(
        post_date=post_date_obj, title="", url="", description="", user_id=user.id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return {
        "message": f"{pre_register.post_date} の担当者として username {user.username} を登録しました",
        "post": db_post,
    }


@app.get("/overview", response_model=OverviewResponse)
async def get_overview(db: Session = Depends(get_db)):
    """概要情報を取得"""
    overview = db.query(Overview).first()
    content = overview.content if overview else ""
    return OverviewResponse(content=content)


@app.put("/overview", response_model=OverviewResponse)
async def update_overview(
    update: OverviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """概要情報を更新（管理者のみ）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="管理者権限が必要です")

    overview = db.query(Overview).first()
    if overview:
        overview.content = update.content
        overview.updated_at = datetime.utcnow()
    else:
        overview = Overview(content=update.content, updated_at=datetime.utcnow())
        db.add(overview)
    db.commit()
    return OverviewResponse(content=overview.content)
