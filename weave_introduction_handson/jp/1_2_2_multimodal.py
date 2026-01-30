"""
1_2_2: Multimodal - マルチモーダル対応

このスクリプトで学べること:
================================
1. 画像のトラッキング (Images)
2. 音声のトラッキング (Audio)
3. 動画のトラッキング (Video)
4. PDF/ドキュメントのトラッキング (Documents)
5. HTMLコンテンツのトラッキング

API対応状況:
============
| メディア | OpenAI | Gemini |
|----------|--------|--------|
| 画像生成  | DALL-E | Imagen (限定的) |
| 画像理解  | GPT-4o Vision | Gemini Vision |
| 音声生成  | TTS | 非対応 |
| 音声理解  | Whisper | Gemini Audio |
| 動画理解  | 非対応 | Gemini Video |
| PDF理解   | GPT-4o | Gemini |
"""

import os
from pathlib import Path
from typing import Annotated, Literal
from dotenv import load_dotenv
import weave
from weave import Content
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# 1. Images - 画像のトラッキング
# =============================================================================
print("\n" + "=" * 60)
print("1. Images - 画像のトラッキング")
print("=" * 60)

# -----------------------------------------------------------------------------
# OpenAI Version - 画像生成 (DALL-E)
# -----------------------------------------------------------------------------
print("\n--- OpenAI Version ---")

import openai
openai_client = openai.OpenAI()


@weave.op()
def generate_image_openai(prompt: str) -> Annotated[bytes, Content]:
    """OpenAI DALL-E で画像を生成
    
    OpenAI は DALL-E による画像生成に対応しています。
    Annotated[bytes, Content] で Weave が自動的に画像としてトラッキングします。
    """
    import requests
    
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    return image_response.content


# コストがかかるため、コメントアウト
# image_bytes = generate_image_openai("A cute cat wearing a wizard hat")
# Path(OUTPUT_DIR / "dalle_image.png").write_bytes(image_bytes)
print("generate_image_openai() - DALL-E で画像生成 (コメントアウト中)")


@weave.op()
def analyze_image_openai(image_path: Annotated[str, Content]) -> str:
    """OpenAI GPT-4o で画像を分析
    
    OpenAI は GPT-4o の Vision 機能で画像理解に対応しています。
    """
    import base64
    
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "この画像を簡潔に説明してください。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
                ],
            }
        ],
        max_tokens=100,
    )
    return response.choices[0].message.content


# サンプル画像を作成
sample_img = Image.new('RGB', (200, 100), color='lightblue')
draw = ImageDraw.Draw(sample_img)
draw.text((50, 40), "Hello Weave!", fill='navy')
sample_path = OUTPUT_DIR / "sample_image.png"
sample_img.save(sample_path)

description = analyze_image_openai(str(sample_path))
print(f"OpenAI 画像分析: {description[:60]}...")

# -----------------------------------------------------------------------------
# Gemini Version - 画像理解
# -----------------------------------------------------------------------------
print("\n--- Gemini Version ---")

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    @weave.op()
    def analyze_image_gemini(image_path: Annotated[str, Content]) -> str:
        """Gemini で画像を分析
        
        Gemini は Vision 機能で画像理解に対応しています。
        画像生成 (Imagen) は API アクセスが限定的です。
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        img = Image.open(image_path)
        response = model.generate_content(["この画像を簡潔に説明してください。", img])
        return response.text
    
    description = analyze_image_gemini(str(sample_path))
    print(f"Gemini 画像分析: {description[:60]}...")
    
except ImportError:
    print("google-generativeai がインストールされていません")
except Exception as e:
    print(f"Gemini エラー: {e}")


# =============================================================================
# 2. Audio - 音声のトラッキング
# =============================================================================
print("\n" + "=" * 60)
print("2. Audio - 音声のトラッキング")
print("=" * 60)

# -----------------------------------------------------------------------------
# OpenAI Version - 音声生成 (TTS)
# -----------------------------------------------------------------------------
print("\n--- OpenAI Version ---")


@weave.op()
def generate_speech_openai(text: str) -> Annotated[bytes, Content[Literal['mp3']]]:
    """OpenAI TTS で音声を生成
    
    OpenAI は TTS (Text-to-Speech) に対応しています。
    Annotated[bytes, Content[Literal['mp3']]] で Weave が音声としてトラッキングします。
    """
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="mp3",
    )
    return response.content


audio_bytes = generate_speech_openai("Hello from Weave!")
audio_path = OUTPUT_DIR / "tts_output.mp3"
audio_path.write_bytes(audio_bytes)
print(f"Created: {audio_path}")

# -----------------------------------------------------------------------------
# Gemini Version - 音声生成
# -----------------------------------------------------------------------------
print("\n--- Gemini Version ---")
print("Gemini は直接的な TTS (音声生成) API を提供していません。")
print("   音声理解 (Speech-to-Text) は対応しています。")


# =============================================================================
# 3. Video - 動画のトラッキング
# =============================================================================
print("\n" + "=" * 60)
print("3. Video - 動画のトラッキング")
print("=" * 60)

# -----------------------------------------------------------------------------
# OpenAI Version - 動画
# -----------------------------------------------------------------------------
print("\n--- OpenAI Version ---")
print("OpenAI は現在、動画の入力・生成に対応していません。")

# -----------------------------------------------------------------------------
# Gemini Version - 動画理解
# -----------------------------------------------------------------------------
print("\n--- Gemini Version ---")

try:
    import google.generativeai as genai
    import time
    
    @weave.op()
    def analyze_video_gemini(video_path: Annotated[str, Content]) -> str:
        """Gemini で動画を分析
        
        Gemini は動画ファイルのアップロードと分析に対応しています。
        OpenAI は動画に非対応です。
        """
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # 動画をアップロード
        video_file = genai.upload_file(video_path)
        
        # 処理完了まで待機
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        # 分析
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([video_file, "この動画を簡潔に説明してください。"])
        return response.text
    
    print("analyze_video_gemini() - 動画分析関数を定義")
    print("   使用例: analyze_video_gemini('path/to/video.mp4')")
    
except ImportError:
    print("google-generativeai がインストールされていません")


# =============================================================================
# 4. PDF/Documents - ドキュメントのトラッキング
# =============================================================================
print("\n" + "=" * 60)
print("4. PDF/Documents - ドキュメントのトラッキング")
print("=" * 60)

# サンプル PDF を作成
pdf_path = OUTPUT_DIR / "sample_document.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=letter)
c.drawString(100, 750, "Weave Multimodal Demo")
c.drawString(100, 720, "This is a sample PDF document.")
c.drawString(100, 690, "PDF files can be tracked and analyzed in Weave.")
c.save()
print(f"Created: {pdf_path}")

# -----------------------------------------------------------------------------
# OpenAI Version - PDF理解
# -----------------------------------------------------------------------------
print("\n--- OpenAI Version ---")


@weave.op()
def analyze_pdf_openai(pdf_path: Annotated[str, Content]) -> str:
    """OpenAI で PDF を分析
    
    OpenAI は PDF を画像として読み込み、GPT-4o で分析できます。
    """
    import fitz  # PyMuPDF
    import base64
    
    # PDF を画像に変換
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")
    doc.close()
    
    image_data = base64.b64encode(img_bytes).decode()
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "この PDF の内容を要約してください。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
                ],
            }
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content


try:
    import fitz
    summary = analyze_pdf_openai(str(pdf_path))
    print(f"OpenAI PDF分析: {summary[:80]}...")
except ImportError:
    print("PyMuPDF (fitz) をインストールすると PDF 分析が可能です")
    print("   pip install pymupdf")

# -----------------------------------------------------------------------------
# Gemini Version - PDF理解
# -----------------------------------------------------------------------------
print("\n--- Gemini Version ---")

try:
    import google.generativeai as genai
    
    @weave.op()
    def analyze_pdf_gemini(pdf_path: Annotated[str, Content]) -> str:
        """Gemini で PDF を分析
        
        Gemini は PDF ファイルを直接アップロードして分析できます。
        """
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        pdf_file = genai.upload_file(pdf_path)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([pdf_file, "この PDF の内容を要約してください。"])
        return response.text
    
    summary = analyze_pdf_gemini(str(pdf_path))
    print(f"Gemini PDF分析: {summary[:80]}...")
    
except ImportError:
    print("google-generativeai がインストールされていません")
except Exception as e:
    print(f"Gemini エラー: {e}")


# =============================================================================
# 5. HTML - HTMLコンテンツのトラッキング
# =============================================================================
print("\n" + "=" * 60)
print("5. HTML - HTMLコンテンツのトラッキング")
print("=" * 60)


@weave.op()
def generate_html_report(title: str, items: list) -> Annotated[bytes, Content[Literal['html']]]:
    """HTML レポートを生成
    
    Annotated[bytes, Content[Literal['html']]] で HTML として保存します。
    Weave UI でプレビュー可能です。
    """
    html = f"""<!DOCTYPE html>
<html>
<head><title>{title}</title>
<style>
body {{ font-family: Arial; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
.container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
h1 {{ color: #333; }}
ul {{ line-height: 2; }}
</style>
</head>
<body>
<div class="container">
<h1>{title}</h1>
<ul>{"".join(f"<li>{item}</li>" for item in items)}</ul>
</div>
</body>
</html>"""
    return html.encode('utf-8')


html_report = generate_html_report(
    "Weave Multimodal Features",
    ["画像 (Images)", "音声 (Audio)", "動画 (Video)", "PDF (Documents)", "HTML"]
)
html_path = OUTPUT_DIR / "report.html"
html_path.write_bytes(html_report)
print(f"Created: {html_path}")


# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 60)
print("Multimodal Demo Complete!")
print("=" * 60)
print(f"\n出力ファイルは {OUTPUT_DIR} に保存されました")
print("""
API 対応まとめ:
==================
| メディア   | OpenAI           | Gemini           |
|------------|------------------|------------------|
| 画像生成   | DALL-E        | 限定的        |
| 画像理解   | GPT-4o Vision | Gemini Vision |
| 音声生成   | TTS           | 非対応        |
| 音声理解   | Whisper       | Gemini        |
| 動画理解   | 非対応        | Gemini        |
| PDF理解    | GPT-4o        | Gemini        |
""")
