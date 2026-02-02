"""
1_2_2: Multimodal (Gemini) - マルチモーダル対応

このスクリプトで学べること:
================================
1. 画像理解 (Gemini Vision)
2. 音声理解 (Gemini Audio)
3. 動画理解 (Gemini Video)
4. PDF理解 (Gemini)

Gemini API 対応状況:
====================
| メディア | 対応 | 備考 |
|----------|------|------|
| 画像生成 | △ | Imagen (アクセス限定的) |
| 画像理解 | ○ | Gemini Vision |
| 音声生成 | × | 非対応 |
| 音声理解 | ○ | Gemini Audio |
| 動画理解 | ○ | Gemini Video |
| PDF理解  | ○ | 直接アップロード可能 |

事前準備:
--------
export GOOGLE_API_KEY=your-api-key
"""

import os
import time
from pathlib import Path
from typing import Annotated
from dotenv import load_dotenv
import weave
from weave import Content
from PIL import Image, ImageDraw
import google.generativeai as genai
from config_loader import get_model_name

# Load environment variables
load_dotenv()

# Initialize Weave
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# 1. 画像理解 (Gemini Vision)
# =============================================================================
print("\n" + "=" * 60)
print("1. 画像理解 (Gemini Vision)")
print("=" * 60)


@weave.op()
def analyze_image(image_path: Annotated[str, Content]) -> str:
    """Gemini で画像を分析
    
    Gemini は Vision 機能で画像理解に対応しています。
    """
    model = genai.GenerativeModel(get_model_name())
    img = Image.open(image_path)
    response = model.generate_content(["この画像を簡潔に説明してください。", img])
    return response.text


# サンプル画像を作成
sample_img = Image.new('RGB', (200, 100), color='lightgreen')
draw = ImageDraw.Draw(sample_img)
draw.text((50, 40), "Hello Gemini!", fill='darkgreen')
sample_path = OUTPUT_DIR / "sample_image_gemini.png"
sample_img.save(sample_path)

description = analyze_image(str(sample_path))
print(f"画像分析結果: {description[:80]}...")


# =============================================================================
# 2. 音声理解 (Gemini Audio)
# =============================================================================
print("\n" + "=" * 60)
print("2. 音声理解 (Gemini Audio)")
print("=" * 60)


@weave.op()
def analyze_audio(audio_path: Annotated[str, Content]) -> str:
    """Gemini で音声を分析
    
    Gemini は音声ファイルをアップロードして理解できます。
    注意: 音声生成 (TTS) は非対応です。
    """
    audio_file = genai.upload_file(audio_path)
    model = genai.GenerativeModel(get_model_name())
    response = model.generate_content([audio_file, "この音声の内容を書き起こしてください。"])
    return response.text


# OpenAI TTS で生成した音声ファイルを使用
audio_path = OUTPUT_DIR / "tts_output.mp3"
if audio_path.exists():
    transcription = analyze_audio(str(audio_path))
    print(f"音声分析結果: {transcription[:80]}...")
else:
    print("音声ファイルが見つかりません。先に 1_2_2_multimodal_openai.py を実行してください。")


# =============================================================================
# 3. 動画生成とアップロード (Gemini Video)
# =============================================================================
print("\n" + "=" * 60)
print("3. 動画生成とアップロード (Gemini Video)")
print("=" * 60)


@weave.op()
def generate_video() -> Annotated[str, Content]:
    """imageioを使って動画を生成
    
    動画ファイルのパスを返し、Weaveに保存します。
    """
    import numpy as np
    import imageio.v3 as iio
    
    video_path = OUTPUT_DIR / "sample_video.mp4"
    
    # アニメーションフレームを作成（60フレーム、30fps = 2秒）
    frames = []
    for i in range(60):
        # PILで画像を作成
        img = Image.new('RGB', (640, 480), color=(100, 149, 237))
        draw = ImageDraw.Draw(img)
        
        # 移動するテキスト
        x = 100 + i * 5
        draw.rectangle([x, 200, x + 200, 280], fill=(255, 255, 255))
        draw.text((x + 20, 220), f"Frame {i+1}", fill=(0, 0, 0))
        
        # numpy配列に変換
        frames.append(np.array(img))
    
    # imageioで動画を保存
    iio.imwrite(str(video_path), frames, fps=30, codec='libx264')
    print(f"動画ファイル作成: {video_path}")
    
    return str(video_path)


@weave.op()
def analyze_video(video_path: Annotated[str, Content]) -> str:
    """Geminiで動画を分析
    
    Gemini は動画ファイルのアップロードと分析に対応しています。
    OpenAI は動画に非対応です。
    """
    # 動画をアップロード
    video_file = genai.upload_file(video_path)
    
    # 処理完了まで待機
    while video_file.state.name == "PROCESSING":
        time.sleep(2)
        video_file = genai.get_file(video_file.name)
    
    # 分析
    model = genai.GenerativeModel(get_model_name())
    response = model.generate_content([video_file, "この動画を簡潔に説明してください。"])
    return response.text


# 動画生成
video_path = generate_video()

# 動画分析
video_description = analyze_video(video_path)
print(f"動画分析結果: {video_description[:80]}...")


# =============================================================================
# 4. PDF理解 (Gemini)
# =============================================================================
print("\n" + "=" * 60)
print("4. PDF理解 (Gemini)")
print("=" * 60)

# サンプル PDF を作成
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    pdf_path = OUTPUT_DIR / "sample_document_gemini.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, "Gemini Multimodal Demo")
    c.drawString(100, 720, "This is a sample PDF document.")
    c.drawString(100, 690, "Gemini can directly upload and analyze PDF files.")
    c.save()
    print(f"PDFファイル作成: {pdf_path}")
except ImportError:
    print("reportlab がインストールされていません")
    pdf_path = None


@weave.op()
def analyze_pdf(pdf_path: Annotated[str, Content]) -> str:
    """Gemini で PDF を分析
    
    Gemini は PDF ファイルを直接アップロードして分析できます。
    画像変換不要で、OpenAI より簡潔に処理できます。
    """
    pdf_file = genai.upload_file(pdf_path)
    model = genai.GenerativeModel(get_model_name())
    response = model.generate_content([pdf_file, "この PDF の内容を要約してください。"])
    return response.text


if pdf_path:
    summary = analyze_pdf(str(pdf_path))
    print(f"PDF分析結果: {summary[:80]}...")
