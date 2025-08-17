# W&B Weave ハンズオン

[English version is here](README.md)

## 概要（このスクリプトで実現すること）
このリポジトリには、W&B Weaveを学ぶためのハンズオン教材が含まれています。LLMベースのアプリケーションの追跡、実験、評価、デプロイ、改善のためのフレームワークであるW&B Weaveと、W&Bが提供する推論サービスW&B Inferenceを体験していきます。

Weaveの全体像を理解されたい方は、[こちらのページ](https://wandbai.notion.site/W-B-Models-Weave-22dad8882177429ba1e9f0f05e7ceac3?source=copy_link)を参照してください。[Weaveのデモ(10分)](https://www.youtube.com/watch?v=Ua0Wx9fqhDo&t=144s)や[Weaveドキュメント](https://wandb.me/weave)などのリンクをまとめています。


## 環境構築・事前準備

1. **W&Bのアカウント発行・環境構築方法**
   
   [こちらのページ](https://wandbai.notion.site/W-B-Models-Weave-22dad8882177429ba1e9f0f05e7ceac3?source=copy_link)にW&Bのアカウント発行方法・環境構築方法を記載しています。instructionに従いながら、W&Bのアカウントを発行、API keyの取得を行なってください。Enterpriseのお客様で発行方法やWANDB_BASE_URLがわからない方は、担当のW&Bエンジニアまでご連絡ください。

2. **W&B Inferencの準備**

   LLMのAPIの推論には、W&B Inference (β機能)を利用します。2025年より、W&Bが推論のエンドポイントを提供しています。$5までは無料で利用できるので、ハンズオンではこちらを利用していきます。W&B Inferenceのドキュメントは[こちら](https://docs.wandb.ai/guides/inference/)です。W&B Inferenceで利用できるモデルの一覧は[こちら](https://wandb.ai/inference)です。W&B Inferenceを利用するために、個人のentity以外のentityの中に、projectを作成してください。推論でそのprojectを利用します。projectは以下の画像の"New project"から作成できます。entityは以下の画像の場合、wandb-japanになります。個人のentity(keisuke-kamataなどのアカウントの名前がついたentity)ではinferenceは使えないので、ご注意ください。

   ![W&B Inferenceのプロジェクト作成例](img/Screenshot1.png)

3. **環境構築**

   3.1 Google Colabを利用する場合
      - Google Colabの場合は、以下のリンクを利用してください

   3.2 ローカル実行の場合
   - Python 3.8以上 / [uv](https://github.com/astral-sh/uv)（推奨）または pip

      ローカル実行の場合は、以下のフローに従って環境構築をしてください:
   - **リポジトリをクローン:**
      ```bash
      git clone https://github.com/olachinkei/wandb-handson.git
      cd wandb-handson/weave_introduction
      ```

   - **uvを使用した環境構築（推奨）:**
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
      
      **Jupyter Labを起動してノートブックを開く:**
      ```bash
      jupyter lab weave_intro_notebook.ipynb
      ```

4. **環境変数の設定**
   `WANDB_API_KEY`は[こちら](https://docs.wandb.ai/support/find_api_key/)を参考にして取得してください。
   ```bash
   Google Colabを利用の方は、最初のセルに入力をしてください。

   export WANDB_BASE_URL="https://api.wandb.ai" # dedicated cloudやオンプレミスを利用の方のみ
   export WANDB_API_KEY="your_wandb_api_key_here" 
   export WANDB_API_KEY_PUBLIC_CLOUD= "your_public_cloud_wandb_api_key_here"  # Public cloudユーザーはWANDB_API_KEYと同じ値を使用
   export GOOGLE_API_KEY="your_google_api_key" # optional if you want to try video
   ```
   **注意:** 
   - dedicated cloudやオンプレミス環境をお使いの場合は、`WANDB_BASE_URL`を適切に変更してください。
   - Azure OpenAIを使用する場合は、環境変数に`USE_AZURE_OPENAI=true`を設定してください。

5. **ハンズオンまでに確認いただきたいステップ**

   jupyter notebook（または Google Colab）の中の以下のセクションが実装できることをご確認ください。
   - 🪄 `weave`ライブラリのインストールとログイン
   - 関数の入力と出力をトラッキング
      - カスタム関数のトラッキング
      - Integrationを利用したトラッキング（W&B Inference、OpenAI、Anthropic、Mistralなど）

   ご不明なことがあれば、W&B鎌田 (keisuke.kamata@wandb.com)までご連絡ください。

## リソース

- **ドキュメント**: [W&B Weave Documentation](https://weave-docs.wandb.ai/)
- **動画**:
  - [日本語チュートリアル](https://www.youtube.com/watch?v=Ua0Wx9fqhDo&t=295s)
  - [英語チュートリアル](https://www.youtube.com/watch?v=sJNjw6U2Tvg&t=522s) 