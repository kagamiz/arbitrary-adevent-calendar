# ビルドステージ
FROM node:18-alpine AS builder

WORKDIR /app

# 依存関係をコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci

# ソースコードをコピー
COPY . .

# 環境変数をビルド時に設定
ARG VITE_API_BASE_URL
ARG VITE_CALENDAR_NAME
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_CALENDAR_NAME=$VITE_CALENDAR_NAME

# SvelteKitの設定を生成
RUN npx svelte-kit sync

# アプリケーションをビルド
RUN npm run build

# 本番ステージ
FROM nginx:alpine

# nginx設定をコピー
COPY nginx.conf /etc/nginx/nginx.conf

# ビルドされたファイルをコピー
COPY --from=builder /app/build /usr/share/nginx/html

# ポート80を公開
EXPOSE 80

# nginxを起動
CMD ["nginx", "-g", "daemon off;"] 
