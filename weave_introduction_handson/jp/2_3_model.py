"""
2_3: Model Management - モデル管理

このスクリプトで学べること:
================================
1. weave.Model の作成と公開
2. 複数のメソッド（predict, invoke, generate など）
3. モデルパラメータの追跡
4. weave.ref() でモデルを読み込む
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import weave
from weave import Model

from config_loader import chat_completion, get_model_name

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# Path to store asset references
ASSETS_FILE = Path(__file__).parent.parent / "assets.json"


def save_asset_ref(asset_type: str, name: str, ref: str):
    """Save asset reference to local file."""
    assets = json.load(open(ASSETS_FILE)) if ASSETS_FILE.exists() else {}
    assets.setdefault(asset_type, {})[name] = ref
    json.dump(assets, open(ASSETS_FILE, 'w'), indent=2)
    print(f"Saved {asset_type}/{name}: {ref}")


# =============================================================================
# 1. weave.Model の作成
# =============================================================================
print("\n" + "=" * 60)
print("1. weave.Model の作成")
print("=" * 60)


class TextAssistant(Model):
    """テキスト処理アシスタント
    
    weave.Model を継承することで:
    - パラメータ (model_name, temperature など) が自動的に追跡される
    - @weave.op() を付けたメソッドが自動的にトレースされる
    - publish() でバージョン管理できる
    
    predict 以外のメソッド名も使えます！
    """
    model_name: str
    temperature: float = 0.3
    max_tokens: int = 150
    
    # ---------------------------------------------------------
    # predict: 標準的な予測メソッド
    # ---------------------------------------------------------
    @weave.op()
    def predict(self, question: str) -> dict:
        """質問に回答する（標準的なメソッド名）"""
        messages = [
            {"role": "system", "content": "Answer concisely."},
            {"role": "user", "content": question},
        ]
        answer = chat_completion(messages, temperature=self.temperature, max_tokens=self.max_tokens)
        return {"answer": answer, "model": self.model_name}
    
    # ---------------------------------------------------------
    # invoke: LangChain スタイルのメソッド名
    # ---------------------------------------------------------
    @weave.op()
    def invoke(self, prompt: str) -> str:
        """プロンプトを実行する（LangChain スタイル）"""
        messages = [{"role": "user", "content": prompt}]
        return chat_completion(messages, temperature=self.temperature, max_tokens=self.max_tokens)
    
    # ---------------------------------------------------------
    # generate: 生成タスク用
    # ---------------------------------------------------------
    @weave.op()
    def generate(self, topic: str, style: str = "informative") -> str:
        """トピックについてテキストを生成"""
        messages = [
            {"role": "system", "content": f"Write in a {style} style."},
            {"role": "user", "content": f"Write about: {topic}"},
        ]
        return chat_completion(messages, temperature=0.7, max_tokens=self.max_tokens)
    
    # ---------------------------------------------------------
    # analyze: 分析タスク用
    # ---------------------------------------------------------
    @weave.op()
    def analyze(self, text: str) -> dict:
        """テキストを分析"""
        messages = [
            {"role": "system", "content": "Analyze the text. Return JSON: {\"sentiment\": \"...\", \"summary\": \"...\"}"},
            {"role": "user", "content": text},
        ]
        result = chat_completion(messages, temperature=0, max_tokens=self.max_tokens)
        try:
            return json.loads(result)
        except:
            return {"raw": result}
    
    # ---------------------------------------------------------
    # translate: 翻訳タスク用
    # ---------------------------------------------------------
    @weave.op()
    def translate(self, text: str, target_lang: str = "English") -> str:
        """テキストを翻訳"""
        messages = [
            {"role": "system", "content": f"Translate to {target_lang}. Only output the translation."},
            {"role": "user", "content": text},
        ]
        return chat_completion(messages, temperature=0.3, max_tokens=self.max_tokens)


# モデルを作成
assistant = TextAssistant(
    model_name=get_model_name(),
    temperature=0.3,
    max_tokens=150,
)

# 公開
ref = weave.publish(assistant, name="text_assistant")
save_asset_ref("models", "text_assistant", ref.uri())


# =============================================================================
# 2. 各メソッドの実行
# =============================================================================
print("\n" + "=" * 60)
print("2. 各メソッドの実行")
print("=" * 60)

# predict
print("\n--- predict ---")
result = assistant.predict("What is Python?")
print(f"Answer: {result['answer'][:80]}...")

# invoke
print("\n--- invoke ---")
result = assistant.invoke("Explain AI in one sentence.")
print(f"Result: {result[:80]}...")

# generate
print("\n--- generate ---")
result = assistant.generate("machine learning", style="casual")
print(f"Generated: {result[:80]}...")

# analyze
print("\n--- analyze ---")
result = assistant.analyze("I absolutely love this new feature! It's amazing.")
print(f"Analysis: {result}")

# translate
print("\n--- translate ---")
result = assistant.translate("こんにちは、世界！", target_lang="English")
print(f"Translation: {result}")


# =============================================================================
# 3. weave.ref() でモデルを読み込む
# =============================================================================
print("\n" + "=" * 60)
print("3. weave.ref() でモデルを読み込む")
print("=" * 60)

if ASSETS_FILE.exists():
    assets = json.load(open(ASSETS_FILE))
    if "models" in assets and "text_assistant" in assets["models"]:
        # URI を使って読み込む
        model_uri = assets["models"]["text_assistant"]
        loaded = weave.ref(model_uri).get()
        
        print(f"Loaded model: {loaded.model_name}")
        print(f"  temperature: {loaded.temperature}")
        print(f"  max_tokens: {loaded.max_tokens}")
        
        # 読み込んだモデルでメソッドを実行
        result = loaded.predict("What is gravity?")
        print(f"Answer: {result['answer'][:60]}...")

print("""
weave.ref() の使い方:
========================

# URI を使って読み込む
model = weave.ref("weave:///entity/project/object/name:version").get()

# 名前で読み込む (最新バージョン)
model = weave.ref("text_assistant:latest").get()

# 特定のバージョンを読み込む
model = weave.ref("text_assistant:v1").get()

# 読み込んだモデルを使う
result = model.predict("question")
result = model.invoke("prompt")
result = model.generate("topic")
""")


print("\n" + "=" * 60)
print("Model Management Demo Complete!")
print("=" * 60)
print(f"\n登録したモデルは {ASSETS_FILE} に保存されました")
print("Weave UI でモデルのパラメータを確認してください")
