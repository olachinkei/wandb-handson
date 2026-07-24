# W&B Models Hands-on

[English Version](README_EN.md)

W&B Models を使った実験管理、データとモデルのバージョン管理、ハイパーパラメータ探索、成果共有のハンズオンです。

## W&B Models を初めて聞いたという方へ

W&B Models の機能や価値については、[こちらのページ](https://note.com/wandb_jp/n/n94100f3961fc)にまとめています。

## W&B のアカウント発行・環境構築方法

[こちらのページ](https://wandbai.notion.site/W-B-Models-Weave-22dad8882177429ba1e9f0f05e7ceac3?source=copy_link)に、W&B のアカウント発行方法・環境構築方法を記載しています。手順に従って、W&B アカウントの発行と API キーの取得を行ってください。

利用している環境によって、アカウント発行方法が異なります。

- **W&B Multitenant SaaS を利用する場合**
  - [https://www.wandb.jp/](https://www.wandb.jp/) にアクセスし、右上のサインアップボタンからアカウントを作成してください。
- **Dedicated Cloud またはオンプレミス環境を利用する場合**
  - 管理者にユーザーアカウントの発行を依頼してください。
  - アカウント発行後に届くメール内のリンクからログインしてください。
  - 環境変数 `WANDB_BASE_URL` を、W&B から案内された URL に設定してください。
  - ログインできない場合、`WANDB_BASE_URL` が未設定であることがよくあります。URL がわからない場合は、管理者または担当の W&B エンジニアに確認してください。

**Team による作業環境管理**

W&B Models では、Team、Project、Run という単位で実験を管理します。Team は共同作業の単位で、同じ Team に所属するメンバーには実験結果が共有されます。Project は Team 配下のフォルダのような管理単位で、Run は個々の実験を表します。

Enterprise 環境では、Team の作成は Admin のみが行えます。既存の Team 名を Admin に確認するか、新しい Team の作成を依頼してください。Free plan では作成できる Team は 1 つです。

## ハンズオン Agenda

### 1. Experiment Tracking（実験管理）

- Config、Tags、Group、Job Type による Run の整理
- 学習・検証メトリクスの記録と比較
- カスタム X 軸と Summary Metrics

使用するスクリプト: `jp/1_experiment.py`

### 2. Tables and Rich Media（テーブルとリッチメディア）

- `wandb.Table` による構造化データの記録
- 画像とセグメンテーションマスクの可視化
- 時系列 Table の比較

使用するスクリプト: `jp/2_table.py`

### 3. Artifacts（データとモデルのバージョン管理）

- Dataset Artifact と Model Artifact の作成
- `use_artifact()` による入力バージョンの指定
- データ生成、前処理、学習をつなぐ Lineage の確認

使用するスクリプト: `jp/3_artifacts.py`

### 4. Sweeps（ハイパーパラメータ探索）

- Random Sweep の作成
- learning rate、epoch、batch size の探索
- Sweep Dashboard での試行比較

使用するスクリプト: `jp/4_sweeps.py`

このスクリプトはローカルで6回の試行を実行します。

### 5. Registry（モデルのキュレーション）

- Artifact Version の Registry Collection へのリンク
- Alias、Tags、Collection Card の設定
- Registry からの Artifact 取得と Lineage の確認

使用するスクリプト: `jp/5_registry.py`

この章を実行する前に、`jp/3_artifacts.py` を実行して Model Artifact を作成してください。Registry への書き込み権限も必要です。

また、[W&B Registry](https://wandb.ai/registry/) で次のCollectionを手動作成してください。スクリプトからCollectionは作成しません。

1. Registry `models_handson` を開きます。存在しない場合はUIから作成します。
2. **Create collection**を選びます。
3. Collection名を `handson`、Artifact typeを `model` にします。
4. Target pathが `wandb-registry-models_handson/handson` であることを確認します。

詳細: [Create a collection](https://docs.wandb.ai/models/registry/create_collection#python-sdk-beta)

### 6. Reports（実験結果の可視化と共有）

- Run Set と Panel Grid による実験結果の整理
- 学習曲線と Sweep のパラメータ重要度の可視化
- Report の下書き作成と共有

使用するスクリプト: `jp/6_report.py`

この章では、前章までに作成した Run、Artifact、Sweep の結果を利用します。Report and Workspace API は Public Preview のため、最新仕様は[公式ドキュメント](https://docs.wandb.ai/models/reports/create-a-report)を確認してください。

### 7. Extended Capabilities（W&B SDK の拡張機能）

- Run の再開
- Public API による履歴取得
- PR Curve、Audio、Offline Run の記録
- 環境設定の確認
- 明示的に許可した場合のみ Alert を送信

使用するスクリプト: `jp/7_extended_capabilities.py`

### Notebook

`jp/W&B_models_intro_notebook.ipynb` では、主要な機能を Jupyter Notebook 形式で学べます。

## 環境構築・実行方法

### 1. プロジェクトディレクトリに移動

```bash
cd models_handson
```

### 2. 環境変数を設定

まず W&B にログインします。すでにログイン済みの場合、保存済みの認証情報が使用されます。

```bash
wandb login
```

次に、`models_handson` 直下の `.env` に記録先を設定します。

```env
# 任意: 保存先の W&B Team を明示する場合
WANDB_ENTITY=your_team_name

# オプション
WANDB_PROJECT=wandb-models-handson

# Dedicated Cloud やオンプレミスを利用している場合
WANDB_BASE_URL=https://your-instance.wandb.io

# 別のRegistry Collectionを使う場合
WANDB_REGISTRY_TARGET_PATH=wandb-registry-models_handson/handson
```

`WANDB_ENTITY` を省略すると、W&B SDK がログイン情報からデフォルトの Entity を自動的に選択します。保存先の Team を明示したい場合は、その Entity 名を指定してください。`WANDB_PROJECT` を省略すると `wandb-models-handson` が使用されます。W&B Cloud で Team の Entity 名を確認するには、Team のページを開き、URL `https://wandb.ai/<ENTITY>` の `<ENTITY>` 部分を確認します。

`.env` の各行を Python プロセスから参照できる環境変数として読み込みます。

```bash
set -a
source .env
set +a
```

> **重要:** `WANDB_ENTITY=...` 形式の `.env` に対して `source .env` だけを実行すると、値はシェル変数にはなりますが `export` されません。そのため、Python の `os.getenv("WANDB_ENTITY")` からは参照できません。上記の `set -a` を使用するか、`.env` の各行を `export WANDB_ENTITY=...` の形式で記述してください。

読み込み結果を確認します。

```bash
printenv WANDB_ENTITY
```

`.env` で保存先を明示した場合、Team の Entity 名が表示されれば読み込み完了です。何も表示されない場合でもW&B SDKのデフォルトEntityで実行できますが、保存先を固定したい場合は、変数名が大文字の `WANDB_ENTITY` になっているか、上記の読み込みコマンドを同じターミナルで実行したかを確認してください。

`.env` には認証情報が含まれる場合があるため、Git にコミットしないでください。

### 3. 依存関係をインストール

Python 3.11 以上と [uv](https://docs.astral.sh/uv/) を使用します。

```bash
uv sync
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 4. 受講前の一括動作確認

ハンズオンを始める前に、認証・依存関係・主要機能が動作することを1コマンドで確認できます。

```bash
python test.py
```

`test.py` は短時間で確認できる最小構成として、次のオブジェクトを作成します。

1. Experiment Run: 3ステップのConfigとMetricsを記録するRunを1つ
2. Table: 同じ実験結果をまとめたTableを1つ
3. Artifact: 実験結果のJSONを含むArtifactを1つ
4. Report: 実験メトリクスのグラフを1枚含むDraft Reportを1つ

この確認はDry Runではありません。現在選択されているW&B EntityとProjectに、実際のRun、Artifact、Draft Reportを作成します。実行開始時に表示されるEntity、Project、URLが意図した保存先であることを確認してください。

最後に `ALL CHECKS PASSED` と表示されれば、主要機能の事前確認は完了です。途中で失敗した場合は、表示されたエラーを修正してから、同じコマンドを再実行してください。

Sweeps、Registry、Extended Capabilitiesはこの一括確認には含まれません。

### 5. スクリプトを実行

最初の章を実行する例:

```bash
python jp/1_experiment.py
```

実行後、ターミナルに表示される Run URL を開き、W&B UI で記録された Config、Metrics、Tags、Group を確認してください。

章を順番に進める場合:

```bash
python jp/1_experiment.py
python jp/2_table.py
python jp/3_artifacts.py
python jp/4_sweeps.py
python jp/5_registry.py
python jp/6_report.py
python jp/7_extended_capabilities.py
```

Notebook を利用する場合:

```bash
jupyter lab jp/W\&B_models_intro_notebook.ipynb
```

## 注意事項

- スクリプトは W&B に Run や Artifact を記録します。意図した Team と Project が設定されていることを確認してから実行してください。
- `jp/4_sweeps.py` は6回の Sweep 試行を実行します。
- `jp/5_registry.py` は、事前に手動作成した Registry Collectionを更新します。既定のTarget pathは `wandb-registry-models_handson/handson` です。別のCollectionを使用する場合は `WANDB_REGISTRY_TARGET_PATH` を変更してください。
- `jp/6_report.py` は非公開の下書きとして Report を保存します。内容を確認後、W&B UI から公開してください。
- `jp/7_extended_capabilities.py --demo alert` は、`--enable-alert` を追加した場合にのみ外部通知を送信します。

## リソース

- **W&B Models ドキュメント**: [W&B Models Documentation](https://docs.wandb.ai/models)
- **日本語キャッチアップ資料**: [W&B Models / Weave](https://note.com/wandb_jp/n/n94100f3961fc)
- **Experiments**: [Track experiments](https://docs.wandb.ai/models/track)
- **Tables**: [W&B Tables](https://docs.wandb.ai/models/tables)
- **Artifacts**: [W&B Artifacts](https://docs.wandb.ai/models/artifacts)
- **Sweeps**: [W&B Sweeps](https://docs.wandb.ai/models/sweeps)
- **Registry**: [W&B Registry](https://docs.wandb.ai/models/registry)
- **Reports**: [W&B Reports](https://docs.wandb.ai/models/reports)
