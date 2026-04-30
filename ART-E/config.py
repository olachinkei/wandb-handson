"""
===========================================
ART-E Email Search Agent - 設定モジュール
===========================================

このモジュールには以下が含まれます：
- トレーニング設定
- モデル設定
- データセット設定

設定を変更する場合は、このファイルを編集してください。
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelConfig:
    """
    モデル設定

    Attributes:
        name: モデル名（W&Bに表示される名前）
        project: "entity/project" 形式のプロジェクト名
        base_model: ベースモデルのHugging Face ID
    """
    name: str = "email-agent-003"
    project: str = "ARTE-Email-Search-Agent"
    base_model: str = "OpenPipe/Qwen3-14B-Instruct"

    @property
    def entity(self) -> Optional[str]:
        """project から entity 部分を取得（"entity/project" 形式の場合）"""
        if "/" in self.project:
            return self.project.split("/", 1)[0]
        return None

    @property
    def project_name(self) -> str:
        """project からプロジェクト名部分のみ取得"""
        if "/" in self.project:
            return self.project.split("/", 1)[1]
        return self.project


@dataclass
class TrainingConfig:
    """
    トレーニング設定
    
    Attributes:
        groups_per_step: 各ステップでトレーニングするグループ数
        num_epochs: エポック数
        rollouts_per_group: 各グループのロールアウト数（GRPOの比較に使用）
        learning_rate: 学習率
        max_steps: 最大トレーニングステップ数
        validation_step_interval: バリデーションを実行するステップ間隔
        max_turns: エージェントの最大ターン数
    
    Note:
        ハンズオン用のデフォルト値は約5分で完了する設定です。
        本番トレーニングでは CLI 引数で値を大きくしてください。

        ハンズオン用（デフォルト）:
            groups_per_step=2, rollouts_per_group=4, max_steps=5

        本番用（推奨）:
            groups_per_step=8, rollouts_per_group=8, max_steps=500
    """
    groups_per_step: int = 2
    num_epochs: int = 1
    rollouts_per_group: int = 4
    learning_rate: float = 1e-5
    max_steps: int = 5
    validation_step_interval: int = 5
    max_turns: int = 6


@dataclass
class DatasetConfig:
    """
    データセット設定
    
    Attributes:
        train_limit: トレーニングシナリオの上限数
        val_limit: バリデーションシナリオの上限数
        max_messages: シナリオあたりの最大参照メッセージ数
        shuffle: シャッフルするかどうか
        seed: 乱数シード（再現性のため）
    
    Note:
        ハンズオン用のデフォルト値は約5分で完了する設定です。
        本番トレーニングでは CLI 引数で値を大きくしてください。
    """
    train_limit: int = 20
    val_limit: int = 5
    
    # シナリオあたりの最大参照メッセージ数
    # 1にすると単一メール参照のシナリオのみ使用
    max_messages: int = 1
    
    # シャッフル設定
    shuffle: bool = True
    
    # 乱数シード（Noneで毎回異なる結果）
    seed: Optional[int] = 42


@dataclass
class RulerConfig:
    """
    RULER評価設定
    
    Attributes:
        judge_model: ジャッジに使用するモデル
        correctness_judge_model: 正確性判定に使用するモデル
        debug: デバッグモードを有効にするか
    """
    # RULERスコアリングに使用するモデル
    judge_model: str = "openai/o4-mini"
    
    # 正確性判定に使用するモデル
    correctness_judge_model: str = "openai/gpt-4.1"
    
    # デバッグモード（Trueでより詳細な出力）
    debug: bool = True


@dataclass
class BackendConfig:
    """
    バックエンド設定

    Attributes:
        use_local: Trueでローカル GPU を使用（LocalBackend）
        local_path: LocalBackend のデータ保存先パス
    """
    use_local: bool = False
    local_path: str = "./.art"


@dataclass
class Config:
    """
    全体設定

    各種設定をまとめて管理するクラス

    使用例:
        config = Config()
        config.training.learning_rate = 1e-6
        config.model.project = "my-custom-project"
    """
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    ruler: RulerConfig = field(default_factory=RulerConfig)
    backend: BackendConfig = field(default_factory=BackendConfig)


# ===========================================
# デフォルト設定インスタンス
# ===========================================

# デフォルト設定（本番用）
default_config = Config()

# デモ用設定（デフォルトと同じ）
demo_config = Config()


def get_config(use_demo: bool = False) -> Config:
    """
    設定を取得

    環境変数 WANDB_ENTITY, WANDB_PROJECT が設定されている場合、
    "entity/project" 形式で config.model.project を構築します。

    Args:
        use_demo: Trueでデモ用の小さな設定を使用

    Returns:
        Config: 設定オブジェクト
    """
    config = demo_config if use_demo else default_config

    entity = os.environ.get("WANDB_ENTITY")
    project = os.environ.get("WANDB_PROJECT")

    if project:
        config.model.project = project
    if entity:
        config.model.project = f"{entity}/{config.model.project}"

    return config

