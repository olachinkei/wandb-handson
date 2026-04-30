#!/usr/bin/env bash
# .env と uv の仮想環境を有効化する（1回だけ source すれば、あとは python をそのまま使える）
# 使い方: source ./activate.sh   ※ source で実行すること

# スクリプトのディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# .env を読み込み
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# 依存関係を同期
uv sync

# 仮想環境を有効化
source .venv/bin/activate

echo "環境が有効化されました。python コマンドでスクリプトを実行できます。"
echo "例: python jp/1_1_0_basic_trace.py"
