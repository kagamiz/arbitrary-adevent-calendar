# アドベントカレンダー Webアプリ

Adventarのようなアドベントカレンダー投稿Webアプリケーションです。

## 機能

- X (Twitter) アカウントでのユーザー認証
- ローカル環境でのモック認証（開発用）
- 投稿の予約・編集・削除
- 投稿者の公開制御（当日0時以降に公開）
- 管理者と投稿者のみが投稿者情報を閲覧可能
- レスポンシブデザイン

## 技術スタック

### バックエンド
- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- uv (依存関係管理)

### フロントエンド
- SvelteKit
- TypeScript
- Tailwind CSS
- Lucide Icons

## セットアップ

### 前提条件
- Docker
- Docker Compose

### Task (taskfile.dev) のインストール

Taskを使用すると、より簡単にDocker Composeを操作できます。

```bash
# Taskをインストール
./setup.sh

# または、手動でインストール
# https://taskfile.dev/installation/ を参照
```

### 開発環境の起動

Taskを使用した簡単な起動方法：

```bash
# 開発環境のセットアップと起動（推奨）
task dev:start

# または、個別に実行
task dev:setup
task docker-compose-up:local
```

### 手動でのセットアップ

1. リポジトリをクローン
```bash
git clone <repository-url>
cd arbitrary-adevent-calendar
```

2. 環境変数を設定
```bash
cp env.example .env
# .envファイルを編集して必要な値を設定
```

3. ローカル環境で起動
```bash
docker-compose -f docker-compose.local.yml up --build
```

4. ブラウザでアクセス
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000

5. モック認証でログイン
- ローカル環境では「モックログイン」ボタンが表示されます
- このボタンをクリックすると、X認証なしでログインできます
- モックユーザーには管理者権限が付与されます

### 本番環境でのデプロイ

Taskを使用した本番環境の起動：

```bash
task docker-compose-up:prod
```

手動での本番環境起動：

```bash
# 環境変数を設定
cp env.example .env
# .envファイルを編集して本番用の値を設定
# ENVIRONMENT=production に変更

# 本番環境で起動
docker-compose -f docker-compose.prod.yml up --build -d
```

## Taskコマンド一覧

### ローカル環境
```bash
task docker-compose-up:local     # ローカル環境で起動
task docker-compose-down:local   # ローカル環境で停止
task docker-compose-logs:local   # ローカル環境のログ表示
task docker-compose-restart:local # ローカル環境で再起動
```

### 本番環境
```bash
task docker-compose-up:prod      # 本番環境で起動
task docker-compose-down:prod    # 本番環境で停止
task docker-compose-logs:prod    # 本番環境のログ表示
task docker-compose-restart:prod # 本番環境で再起動
```

### 開発用
```bash
task dev:setup                   # 開発環境セットアップ
task dev:start                   # 開発環境起動
task dev:stop                    # 開発環境停止
```

### その他
```bash
task docker-compose-status       # 全環境のステータス表示
task docker-compose-clean        # 全環境を停止・クリーンアップ
task help                        # ヘルプを表示
```

## 環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `ENVIRONMENT` | 実行環境 | `local` / `production` |
| `DATABASE_URL` | データベース接続URL | `sqlite:///./advent_calendar.db` |
| `SECRET_KEY` | JWT署名用の秘密鍵 | `your-secret-key-here` |
| `X_CLIENT_ID` | X OAuth クライアントID | `your-x-client-id` |
| `X_CLIENT_SECRET` | X OAuth クライアントシークレット | `your-x-client-secret` |
| `X_REDIRECT_URI` | X OAuth リダイレクトURI | `https://sample-domain.com/api/auth/callback` |
| `X_BEARER_TOKEN` | X API Bearer Token（事前登録用） | `your-x-bearer-token` |
| `FRONTEND_URL` | フロントエンドのベースURL（APIとフロントエンド共通） | `https://sample-domain.com` |
| `CALENDAR_NAME` | カレンダー名 | `arbitrary-advent-calendar` |
| `CALENDAR_START_DATE` | カレンダー開始日 | `2024-12-01` |
| `CALENDAR_END_DATE` | カレンダー終了日 | `2024-12-25` |
| `ADMIN_USERNAMES` | 管理者ユーザー名（カンマ区切り、usernameで指定） | `admin1,admin2` |
| `VITE_CALENDAR_NAME` | フロントエンド用カレンダー名 | `arbitrary-advent-calendar` |

## X OAuth設定

1. [X Developer Portal](https://developer.twitter.com/) でアプリケーションを作成
2. OAuth 2.0設定で以下を設定：
   - Callback URL: `https://sample-domain.com/api/auth/callback`
   - App permissions: Read
3. 取得したClient IDとClient Secretを環境変数に設定

### 本番環境での設定例

本番環境では、以下の環境変数を適切に設定してください：

```env
ENVIRONMENT=production
X_CLIENT_ID=your-actual-client-id
X_CLIENT_SECRET=your-actual-client-secret
X_REDIRECT_URI=https://your-domain.com/api/auth/callback
FRONTEND_URL=https://your-domain.com
```

### 事前登録機能用の設定

管理者が事前に投稿者を登録する機能を使用する場合は、追加で以下を設定してください：

1. X Developer Portalでアプリケーションの「Keys and tokens」から「Bearer Token」を取得
2. 環境変数`X_BEARER_TOKEN`に設定
3. このトークンを使用してX APIからユーザー情報を取得し、事前登録時にユーザーがまだログインしていなくても登録可能になります

## 開発

### バックエンド開発

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

### フロントエンド開発

```bash
cd frontend
npm install
npm run dev
```

## ライセンス

MIT License 

## データベース初期化・マイグレーション

本番・新規環境では、DBファイル（backend/advent_calendar.db）が存在しない状態で下記コマンドを実行してください。

```bash
# 既存のDBファイルがある場合は削除（初回セットアップ時のみ）
rm -f backend/advent_calendar.db

# マイグレーション適用（テーブル作成）
docker compose -f docker-compose.local.yml exec backend uv run alembic upgrade head
```

- これにより、SQLAlchemyモデルに基づいたテーブルが自動作成されます。
- モデル変更時は、

```bash
docker compose -f docker-compose.local.yml exec backend uv run alembic revision --autogenerate -m "変更内容の説明"
docker compose -f docker-compose.local.yml exec backend uv run alembic upgrade head
```

- でマイグレーションを管理できます。
