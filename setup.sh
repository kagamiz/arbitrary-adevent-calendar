#!/bin/bash

# Task (taskfile.dev) インストールスクリプト
# https://taskfile.dev/installation/

set -e

echo "Task (taskfile.dev) をインストールしています..."

# OS判定
OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
    Linux*)     MACHINE=linux;;
    Darwin*)    MACHINE=darwin;;
    CYGWIN*)    MACHINE=windows;;
    MINGW*)     MACHINE=windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

case "${ARCH}" in
    x86_64)     ARCH=amd64;;
    aarch64)    ARCH=arm64;;
    arm64)      ARCH=arm64;;
    *)          ARCH="UNKNOWN:${ARCH}"
esac

# 最新バージョンを取得
LATEST_VERSION=$(curl -s https://api.github.com/repos/go-task/task/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

echo "最新バージョン: ${LATEST_VERSION}"
echo "OS: ${MACHINE}"
echo "Architecture: ${ARCH}"

# ダウンロードURL
DOWNLOAD_URL="https://github.com/go-task/task/releases/download/${LATEST_VERSION}/task_${MACHINE}_${ARCH}.tar.gz"

echo "ダウンロードURL: ${DOWNLOAD_URL}"

# 一時ディレクトリを作成
TEMP_DIR=$(mktemp -d)
cd "${TEMP_DIR}"

# Taskをダウンロード
echo "Taskをダウンロードしています..."
curl -L "${DOWNLOAD_URL}" -o task.tar.gz

# アーカイブを展開
echo "アーカイブを展開しています..."
tar -xzf task.tar.gz

# 実行権限を付与
chmod +x task

# インストール先を決定
if [ "$(id -u)" -eq 0 ]; then
    # rootユーザーの場合
    INSTALL_DIR="/usr/local/bin"
else
    # 一般ユーザーの場合
    INSTALL_DIR="${HOME}/.local/bin"
    mkdir -p "${INSTALL_DIR}"
fi

# Taskをインストール
echo "Taskを ${INSTALL_DIR} にインストールしています..."
sudo mv task "${INSTALL_DIR}/"

# PATHに追加（まだ追加されていない場合）
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo ""
    echo "PATHに ${INSTALL_DIR} を追加してください:"
    echo "export PATH=\"${INSTALL_DIR}:\$PATH\""
    echo ""
    echo "永続的に追加するには、~/.bashrc または ~/.zshrc に追加してください。"
fi

# 一時ディレクトリを削除
cd - > /dev/null
rm -rf "${TEMP_DIR}"

echo ""
echo "Taskのインストールが完了しました！"
echo "バージョンを確認:"
"${INSTALL_DIR}/task" --version

echo ""
echo "利用可能なタスクを確認:"
"${INSTALL_DIR}/task" --list 
