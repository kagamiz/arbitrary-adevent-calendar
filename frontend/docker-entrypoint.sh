#!/bin/bash

# FRONTEND_URLからスキームを除いたホスト名を生成
export NGINX_SERVER_NAME=$(echo $FRONTEND_URL | sed 's|^https\?://||' | sed 's|/.*$||' | sed 's|:.*$||')

# nginx設定テンプレートから環境変数を展開してnginx設定を生成
envsubst '${NGINX_SERVER_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

cat /etc/nginx/nginx.conf

# nginxを起動
exec nginx -g "daemon off;" 
