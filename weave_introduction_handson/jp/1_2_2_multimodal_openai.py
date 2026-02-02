"""
1_2_2: Multimodal (OpenAI) - マルチモーダル対応

このスクリプトで学べること:
================================
1. 画像生成 (DALL-E)
2. 画像理解 (GPT-4o Vision)
3. 音声生成 (TTS)
4. PDF理解 (GPT-4o)
5. HTMLコンテンツのトラッキング

OpenAI API 対応状況:
====================
| メディア | 対応 | API |
|----------|------|-----|
| 画像生成 | ○ | DALL-E |
| 画像理解 | ○ | GPT-4o Vision |
| 音声生成 | ○ | TTS |
| 音声理解 | ○ | Whisper |
| 動画理解 | × | 非対応 |
| PDF理解  | ○ | GPT-4o (画像変換) |
"""

import os
import base64
from pathlib import Path
from typing import Annotated, Literal
from dotenv import load_dotenv
import weave
from weave import Content
from PIL import Image, ImageDraw
import openai

# Load environment variables
load_dotenv()

# Initialize Weave
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# OpenAI client
client = openai.OpenAI()

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# 1. 画像生成 (DALL-E)
# =============================================================================
print("\n" + "=" * 60)
print("1. 画像生成 (DALL-E)")
print("=" * 60)


@weave.op()
def generate_image(prompt: str) -> Annotated[bytes, Content]:
    """DALL-E で画像を生成
    
    Annotated[bytes, Content] で Weave が自動的に画像としてトラッキングします。
    """
    import requests
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    image_response = requests.get(image_url)
    return image_response.content


image_bytes = generate_image("A cute cat wearing a wizard hat")
Path(OUTPUT_DIR / "dalle_image.png").write_bytes(image_bytes)
print(f"画像生成完了: {OUTPUT_DIR / 'dalle_image.png'}")


# =============================================================================
# 2. 画像理解 (GPT-4o Vision)
# =============================================================================
print("\n" + "=" * 60)
print("2. 画像理解 (GPT-4o Vision)")
print("=" * 60)


@weave.op()
def analyze_image(image_path: Annotated[str, Content]) -> str:
    """GPT-4o で画像を分析
    
    GPT-4o の Vision 機能で画像を理解できます。
    """
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    response = client.chat.completions.create(
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

description = analyze_image(str(sample_path))
print(f"画像分析結果: {description[:80]}...")


# =============================================================================
# 3. 音声生成 (TTS)
# =============================================================================
print("\n" + "=" * 60)
print("3. 音声生成 (TTS)")
print("=" * 60)


@weave.op()
def generate_speech(text: str) -> Annotated[bytes, Content[Literal['mp3']]]:
    """TTS で音声を生成
    
    Annotated[bytes, Content[Literal['mp3']]] で Weave が音声としてトラッキングします。
    """
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        response_format="mp3",
    )
    return response.content


audio_bytes = generate_speech("Hello from Weave!")
audio_path = OUTPUT_DIR / "tts_output.mp3"
audio_path.write_bytes(audio_bytes)
print(f"音声ファイル作成: {audio_path}")


# =============================================================================
# 4. PDF理解 (GPT-4o)
# =============================================================================
print("\n" + "=" * 60)
print("4. PDF理解 (GPT-4o)")
print("=" * 60)

# サンプル PDF を作成
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

pdf_path = OUTPUT_DIR / "sample_document.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=letter)
c.drawString(100, 750, "Weave Multimodal Demo")
c.drawString(100, 720, "This is a sample PDF document.")
c.drawString(100, 690, "PDF files can be tracked and analyzed in Weave.")
c.save()
print(f"PDFファイル作成: {pdf_path}")


@weave.op()
def analyze_pdf(pdf_path: Annotated[str, Content]) -> str:
    """GPT-4o で PDF を分析
    
    PDF を画像に変換して GPT-4o で分析します。
    """
    import fitz  # PyMuPDF
    
    # PDF を画像に変換
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")
    doc.close()
    
    image_data = base64.b64encode(img_bytes).decode()
    
    response = client.chat.completions.create(
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


summary = analyze_pdf(str(pdf_path))
print(f"PDF分析結果: {summary[:80]}...")


# =============================================================================
# 5. HTML コンテンツのトラッキング
# =============================================================================
print("\n" + "=" * 60)
print("5. HTML コンテンツのトラッキング")
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
    "OpenAI Multimodal Features",
    ["Image Generation (DALL-E)", "Image Understanding (GPT-4o Vision)", "Speech Generation (TTS)", "PDF Understanding (GPT-4o)"]
)
html_path = OUTPUT_DIR / "report_openai.html"
html_path.write_bytes(html_report)
print(f"HTMLレポート作成: {html_path}")
