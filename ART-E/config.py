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

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelConfig:
    """
    モデル設定
    
    Attributes:
        name: モデル名（W&Bに表示される名前）
        project: プロジェクト名（Weave/W&Bのプロジェクト名）
        base_model: ベースモデルのHugging Face ID
    """
    name: str = "email-agent-003"
    project: str = "ARTE-Email-Search-Agent"
    base_model: str = "OpenPipe/Qwen3-14B-Instruct"


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
        - ノートブックのデフォルト値は小さめ（デモ用）
        - 本番トレーニングではより大きな値を推奨
        
        デモ用（ノートブック）:
            groups_per_step=2, rollouts_per_group=4, max_steps=50
        
        本番用（推奨）:
            groups_per_step=8, rollouts_per_group=8, max_steps=500
    """
    # ===========================================
    # トレーニングパラメータ
    # ===========================================
    
    # 各ステップでトレーニングするグループ数
    # 大きいほど1ステップあたりのデータが多くなる
    groups_per_step: int = 8
    
    # エポック数（データセット全体を何回繰り返すか）
    num_epochs: int = 20
    
    # 各グループのロールアウト数
    # GRPOで相対比較するため、4以上を推奨
    rollouts_per_group: int = 8
    
    # 学習率
    learning_rate: float = 1e-5
    
    # 最大トレーニングステップ数
    # 早期終了のための上限
    max_steps: int = 500
    
    # バリデーションを実行するステップ間隔
    validation_step_interval: int = 10
    
    # ===========================================
    # エージェントパラメータ
    # ===========================================
    
    # エージェントの最大ターン数（ツール呼び出し回数の上限）
    max_turns: int = 8


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
        - ノートブックのデフォルト値は小さめ（デモ用）
        - 本番トレーニングではより大きな値を推奨
        
        デモ用（ノートブック）:
            train_limit=50, val_limit=20
        
        本番用（推奨）:
            train_limit=500, val_limit=100
    """
    # トレーニングシナリオ数
    train_limit: int = 500
    
    # バリデーションシナリオ数
    val_limit: int = 100
    
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


# ===========================================
# デフォルト設定インスタンス
# ===========================================

# デフォルト設定（本番用）
default_config = Config()

# デモ用設定（ノートブックと同じ小さなパラメータ）
demo_config = Config(
    training=TrainingConfig(
        groups_per_step=2,
        num_epochs=20,
        rollouts_per_group=4,
        learning_rate=1e-5,
        max_steps=50,
        validation_step_interval=5,
        max_turns=6,
    ),
    dataset=DatasetConfig(
        train_limit=50,
        val_limit=20,
        max_messages=1,
        shuffle=True,
        seed=42,
    ),
)


def get_config(use_demo: bool = False) -> Config:
    """
    設定を取得
    
    Args:
        use_demo: Trueでデモ用の小さな設定を使用
    
    Returns:
        Config: 設定オブジェクト
    """
    if use_demo:
        return demo_config
    return default_config

