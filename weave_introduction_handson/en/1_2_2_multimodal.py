"""
1_2_2: Multimodal - Multimodal Support

What you'll learn in this script:
================================
1. Image Tracking (Images)
2. Audio Tracking (Audio)
3. Video Tracking (Video)
4. PDF/Document Tracking (Documents)
5. HTML Content Tracking

API Support Status:
============
| Media    | OpenAI | Gemini |
|----------|--------|--------|
| Image Gen | DALL-E | Imagen (limited) |
| Image Understanding | GPT-4o Vision | Gemini Vision |
| Audio Gen | TTS | Not supported |
| Audio Understanding | Whisper | Gemini Audio |
| Video Understanding | Not supported | Gemini Video |
| PDF Understanding | GPT-4o | Gemini |
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
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# 1. Images - Image Tracking
# =============================================================================
print("\n" + "=" * 60)
print("1. Images - Image Tracking")
print("=" * 60)

# -----------------------------------------------------------------------------
# OpenAI Version - Image Generation (DALL-E)
# -----------------------------------------------------------------------------
print("\n--- OpenAI Version ---")

import openai
openai_client = openai.OpenAI()


@weave.op()
def generate_image_openai(prompt: str) -> Annotated[bytes, Content]:
    """Generate images with OpenAI DALL-E
    
    OpenAI supports image generation via DALL-E.
    Annotated[bytes, Content] allows Weave to automatically track as image.
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


# Commented out due to cost
# image_bytes = generate_image_openai("A cute cat wearing a wizard hat")
# Path(OUTPUT_DIR / "dalle_image.png").write_bytes(image_bytes)
print("generate_image_openai() - Generate images with DALL-E (commented out)")


@weave.op()
def analyze_image_openai(image_path: Annotated[str, Content]) -> str:
    """Analyze images with OpenAI GPT-4o
    
    OpenAI supports image understanding via GPT-4o Vision.
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
                    {"type": "text", "text": "Briefly describe this image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}},
                ],
            }
        ],
        max_tokens=100,
    )
    return response.choices[0].message.content


# Create sample image
sample_img = Image.new('RGB', (200, 100), color='lightblue')
draw = ImageDraw.Draw(sample_img)
draw.text((50, 40), "Hello Weave!", fill='navy')
sample_path = OUTPUT_DIR / "sample_image.png"
sample_img.save(sample_path)

description = analyze_image_openai(str(sample_path))
print(f"OpenAI image analysis: {description[:60]}...")

# -----------------------------------------------------------------------------
# Gemini Version - Image Understanding
# -----------------------------------------------------------------------------
print("\n--- Gemini Version ---")

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    @weave.op()
    def analyze_image_gemini(image_path: Annotated[str, Content]) -> str:
        """Analyze images with Gemini
        
        Gemini supports image understanding via Vision.
        Image generation (Imagen) has limited API access.
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        img = Image.open(image_path)
        response = model.generate_content(["Briefly describe this image.", img])
        return response.text
    
    description = analyze_image_gemini(str(sample_path))
    print(f"Gemini image analysis: {description[:60]}...")
    
except ImportError:
    print("google-generativeai is not installed")
except Exception as e:
    print(f"Gemini error: {e}")


# =============================================================================
# 2. Audio - Audio Tracking
# =============================================================================
print("\n" + "=" * 60)
print("2. Audio - Audio Tracking")
print("=" * 60)

# -----------------------------------------------------------------------------
# OpenAI Version - Speech Generation (TTS)
# -----------------------------------------------------------------------------
print("\n--- OpenAI Version ---")


@weave.op()
def generate_speech_openai(text: str) -> Annotated[bytes, Content[Literal['mp3']]]:
    """Generate speech with OpenAI TTS
    
    OpenAI supports TTS (Text-to-Speech).
    Annotated[bytes, Content[Literal['mp3']]] allows Weave to track as audio.
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
# Gemini Version - Speech Generation
# -----------------------------------------------------------------------------
print("\n--- Gemini Version ---")
print("Gemini does not provide direct TTS (speech generation) API.")
print("   Speech-to-Text (audio understanding) is supported.")


# =============================================================================
# 3. Video - Video Tracking
# =============================================================================
print("\n" + "=" * 60)
print("3. Video - Video Tracking")
print("=" * 60)

# -----------------------------------------------------------------------------
# OpenAI Version - Video
# -----------------------------------------------------------------------------
print("\n--- OpenAI Version ---")
print("OpenAI does not currently support video input/generation.")

# -----------------------------------------------------------------------------
# Gemini Version - Video Understanding
# -----------------------------------------------------------------------------
print("\n--- Gemini Version ---")

try:
    import google.generativeai as genai
    import time
    
    @weave.op()
    def analyze_video_gemini(video_path: Annotated[str, Content]) -> str:
        """Analyze videos with Gemini
        
        Gemini supports video file upload and analysis.
        OpenAI does not support video.
        """
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Upload video
        video_file = genai.upload_file(video_path)
        
        # Wait for processing
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
        
        # Analyze
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([video_file, "Briefly describe this video."])
        return response.text
    
    print("analyze_video_gemini() - Video analysis function defined")
    print("   Usage: analyze_video_gemini('path/to/video.mp4')")
    
except ImportError:
    print("google-generativeai is not installed")


# =============================================================================
# 4. PDF/Documents - Document Tracking
# =============================================================================
print("\n" + "=" * 60)
print("4. PDF/Documents - Document Tracking")
print("=" * 60)

# Create sample PDF
pdf_path = OUTPUT_DIR / "sample_document.pdf"
c = canvas.Canvas(str(pdf_path), pagesize=letter)
c.drawString(100, 750, "Weave Multimodal Demo")
c.drawString(100, 720, "This is a sample PDF document.")
c.drawString(100, 690, "PDF files can be tracked and analyzed in Weave.")
c.save()
print(f"Created: {pdf_path}")

# -----------------------------------------------------------------------------
# OpenAI Version - PDF Understanding
# -----------------------------------------------------------------------------
print("\n--- OpenAI Version ---")


@weave.op()
def analyze_pdf_openai(pdf_path: Annotated[str, Content]) -> str:
    """Analyze PDF with OpenAI
    
    OpenAI can read PDFs as images and analyze with GPT-4o.
    """
    import fitz  # PyMuPDF
    import base64
    
    # Convert PDF to image
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
                    {"type": "text", "text": "Summarize the content of this PDF."},
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
    print(f"OpenAI PDF analysis: {summary[:80]}...")
except ImportError:
    print("Install PyMuPDF (fitz) for PDF analysis")
    print("   pip install pymupdf")

# -----------------------------------------------------------------------------
# Gemini Version - PDF Understanding
# -----------------------------------------------------------------------------
print("\n--- Gemini Version ---")

try:
    import google.generativeai as genai
    
    @weave.op()
    def analyze_pdf_gemini(pdf_path: Annotated[str, Content]) -> str:
        """Analyze PDF with Gemini
        
        Gemini can upload and analyze PDF files directly.
        """
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        pdf_file = genai.upload_file(pdf_path)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([pdf_file, "Summarize the content of this PDF."])
        return response.text
    
    summary = analyze_pdf_gemini(str(pdf_path))
    print(f"Gemini PDF analysis: {summary[:80]}...")
    
except ImportError:
    print("google-generativeai is not installed")
except Exception as e:
    print(f"Gemini error: {e}")


# =============================================================================
# 5. HTML - HTML Content Tracking
# =============================================================================
print("\n" + "=" * 60)
print("5. HTML - HTML Content Tracking")
print("=" * 60)


@weave.op()
def generate_html_report(title: str, items: list) -> Annotated[bytes, Content[Literal['html']]]:
    """Generate HTML report
    
    Annotated[bytes, Content[Literal['html']]] saves as HTML.
    Previewable in Weave UI.
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
    ["Images", "Audio", "Video", "PDF (Documents)", "HTML"]
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
print(f"\nOutput files saved to {OUTPUT_DIR}")
print("""
API Support Summary:
==================
| Media        | OpenAI           | Gemini           |
|--------------|------------------|------------------|
| Image Gen    | DALL-E           | Limited          |
| Image Understanding | GPT-4o Vision | Gemini Vision |
| Audio Gen    | TTS              | Not supported    |
| Audio Understanding | Whisper   | Gemini           |
| Video Understanding | Not supported | Gemini        |
| PDF Understanding | GPT-4o      | Gemini           |
""")
