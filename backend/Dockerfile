FROM python:3.11-slim

WORKDIR /app

# 必要パッケージのインストール
# 依存パッケージと Chromium をインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    curl \
    unzip \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 \
    libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libglib2.0-0 libgtk-3-0 \
    libnspr4 libnss3 libpango-1.0-0 libx11-6 libx11-xcb1 libxcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
    libxrandr2 libxrender1 libxss1 libxtst6 lsb-release xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 最新版Chromiumのバージョンを取得
RUN chromium --version

# 適合する ChromeDriver を手動インストール（v137）
RUN curl -Lo /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.119/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /usr/local/bin/chromedriver-linux64

# uvをインストール
RUN pip install uv

# 依存関係ファイルをコピー
COPY pyproject.toml uv.lock ./

# 依存関係をインストール
RUN uv sync --frozen

# アプリケーションコードをコピー
COPY . .

# データディレクトリを作成
RUN mkdir -p /app/data

# ポート8000を公開
EXPOSE 8000

# アプリケーションを起動
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
