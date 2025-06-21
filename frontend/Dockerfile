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
ARG VITE_FRONTEND_URL
ARG VITE_CALENDAR_NAME
ENV VITE_FRONTEND_URL=$VITE_FRONTEND_URL
ENV VITE_CALENDAR_NAME=$VITE_CALENDAR_NAME

# SvelteKitの設定を生成
RUN npx svelte-kit sync

# アプリケーションをビルド
RUN npm run build

# 本番ステージ
FROM nginx:alpine

# 必要なツールをインストール
RUN apk add --no-cache bash

# nginx設定テンプレートをコピー
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# 起動スクリプトをコピー
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# ビルドされたファイルをコピー
COPY --from=builder /app/build /usr/share/nginx/html

# ポート80を公開
EXPOSE 80

# 起動スクリプトを実行
ENTRYPOINT ["/docker-entrypoint.sh"] 
