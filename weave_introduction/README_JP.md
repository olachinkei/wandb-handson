# W&B Weave ハンズオン

[English version is here](README.md)

このリポジトリには、W&B Weaveを学ぶためのハンズオン教材が含まれています。W&B Weaveは、LLMベースのアプリケーションの追跡、実験、評価、デプロイ、改善のためのフレームワークです。

## 前提条件

- Python 3.8以上
- [uv](https://github.com/astral-sh/uv)（推奨）または pip

## 環境構築

1. **リポジトリをクローン:**
   ```bash
   git clone https://github.com/olachinkei/wandb-handson.git
   cd wandb-handson/weave_introduction
   ```

2. **uvを使用した環境構築（推奨）:**
   ```bash
   # uvがインストールされていない場合はインストール
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # 仮想環境を作成・アクティベート
   uv venv
   source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate

   # 依存関係をインストール
   uv pip install -r requirements.txt
   ```

   **pipを使用する場合:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **環境変数の設定:**
   ```bash
   export WANDB_BASE_URL="https://api.wandb.ai"
   export OPENAI_API_KEY="your_openai_api_key_here"
   export WANDB_API_KEY="your_wandb_api_key_here"
   export GOOGLE_API_KEY="your_google_api_key" # otional if you want to try video
   ```
   
   **注意:** dedicated cloudやオンプレミス環境をお使いの場合は、`WANDB_BASE_URL`を適切に変更してください。

4. ** wandbにログイン *
   ```bash  
   wandb login
   ```

5. **Jupyter Labを起動してノートブックを開く:**
   ```bash
   jupyter lab weave_intro_notebook.ipynb
   ```

## 含まれるもの

- `weave_introduction/`: メインのハンズオンノートブック
  - `weave_intro_notebook.ipynb`: W&B Weaveを学ぶためのインタラクティブノートブック
  - `requirements.txt`: Python依存関係

## リソース

- **ドキュメント**: [W&B Weave Documentation](https://weave-docs.wandb.ai/)
- **動画**:
  - [日本語チュートリアル](https://www.youtube.com/watch?v=Ua0Wx9fqhDo&t=295s)
  - [英語チュートリアル](https://www.youtube.com/watch?v=sJNjw6U2Tvg&t=522s) 