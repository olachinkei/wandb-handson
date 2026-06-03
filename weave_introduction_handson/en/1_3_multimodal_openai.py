"""
1_3: Multimodal Data Tracing - Tracing multimodal data

What you'll learn in this script:
================================
1. Adding media types with Annotated[bytes, Content[Literal[...]]]
2. Tracing PNG/JPG images
3. Tracing MP3 audio
4. Tracing MP4 video
5. Tracing PDFs
6. Tracing HTML

Where to look after running:
================================
- Traces tab: Preview each media payload
- Inputs/Outputs: Inspect byte payloads stored with Content types
"""

import io
import os
import base64
import tempfile
import urllib.request
from typing import Annotated, Literal

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw
import weave
from weave import Content

from config_loader import init_weave

# Load environment variables
load_dotenv()

# Initialize Weave
init_weave()

# OpenAI client
client = OpenAI()


def download_bytes(url: str, timeout: int = 60) -> bytes:
    """Small helper that downloads bytes from a URL."""
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


# =============================================================================
# 1. Image (PNG) - OpenAI gpt-image-1
# =============================================================================
print("\n" + "=" * 60)
print("1. Image (PNG) - OpenAI gpt-image-1")
print("=" * 60)


@weave.op()
def generate_image(prompt: str) -> Annotated[bytes, Content[Literal["png"]]]:
    """Generate an image with OpenAI and log it as PNG bytes in Weave."""
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
    )
    return base64.b64decode(response.data[0].b64_json)


image_bytes = generate_image("a small robot watering a flower in a lab, pixel art style")
print(f"PNG image payload size: {len(image_bytes):,} bytes")


# =============================================================================
# 2. Image (JPG) - Trace an existing image
# =============================================================================
print("\n" + "=" * 60)
print("2. Image (JPG) - Trace an existing image")
print("=" * 60)


@weave.op()
def create_sample_jpg_image() -> Annotated[bytes, Content[Literal["jpg"]]]:
    """Generate a sample JPG image so it can be previewed in Weave UI."""
    image = Image.new("RGB", (640, 360), color=(244, 247, 251))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 640, 90), fill=(31, 64, 104))
    draw.ellipse((72, 126, 252, 306), fill=(255, 195, 0), outline=(31, 64, 104), width=6)
    draw.rounded_rectangle((330, 130, 568, 300), radius=24, fill=(82, 167, 255), outline=(31, 64, 104), width=6)
    draw.line((92, 238, 232, 166), fill=(31, 64, 104), width=5)
    draw.line((366, 166, 530, 264), fill=(255, 255, 255), width=8)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


jpg_bytes = create_sample_jpg_image()
print(f"JPG image size: {len(jpg_bytes):,} bytes")


# =============================================================================
# 3. Audio (MP3) - OpenAI TTS
# =============================================================================
print("\n" + "=" * 60)
print("3. Audio (MP3) - OpenAI TTS")
print("=" * 60)


@weave.op()
def text_to_speech(text: str, voice: str = "alloy") -> Annotated[bytes, Content[Literal["mp3"]]]:
    """Generate audio with OpenAI TTS and log it as MP3 bytes in Weave."""
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        response_format="mp3",
    )
    if hasattr(response, "read"):
        return response.read()
    if hasattr(response, "content"):
        return response.content
    return b"".join(response.iter_bytes())


audio_bytes = text_to_speech(
    "Weights and Biases Weave helps you trace, evaluate, and monitor LLM applications."
)
print(f"MP3 audio size: {len(audio_bytes):,} bytes")


# =============================================================================
# 4. Video (MP4) - OpenAI Sora 2
# =============================================================================
print("\n" + "=" * 60)
print("4. Video (MP4) - OpenAI Sora 2")
print("=" * 60)


@weave.op()
def generate_video(
    prompt: str = "A small robot waters a flower in a bright lab, cinematic lighting",
) -> Annotated[bytes, Content[Literal["mp4"]]]:
    """Generate a video with OpenAI Sora 2 and log it as MP4 bytes in Weave."""
    reference_image_url = "https://assets.st-note.com/img/1762403176-PimhEZu3voSeGp5C0l9t4z2N.png"
    png = download_bytes(reference_image_url, timeout=30)

    video = client.videos.create(
        model="sora-2-pro",
        prompt=prompt,
        input_reference=("ref.png", io.BytesIO(png), "image/png"),
        size="1280x720",
        seconds="12",
    )
    result = client.videos.poll(video.id)
    if result.status != "completed":
        raise RuntimeError(f"Video generation failed: {result.error}")

    content = client.videos.download_content(video.id)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        content.write_to_file(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()


if os.getenv("RUN_EXPENSIVE_MULTIMODAL") == "1":
    video_bytes = generate_video()
    print(f"MP4 video size: {len(video_bytes):,} bytes")
else:
    print("Set RUN_EXPENSIVE_MULTIMODAL=1 to run the Sora 2 video generation example.")


# =============================================================================
# 5. PDF - arXiv paper
# =============================================================================
print("\n" + "=" * 60)
print("5. PDF - arXiv paper")
print("=" * 60)


@weave.op()
def fetch_arxiv_pdf(paper_id: str = "1706.03762") -> Annotated[bytes, Content[Literal["pdf"]]]:
    """Download an arXiv PDF and log it as PDF bytes in Weave."""
    return download_bytes(f"https://arxiv.org/pdf/{paper_id}.pdf", timeout=60)


pdf_bytes = fetch_arxiv_pdf()
print(f"PDF size: {len(pdf_bytes):,} bytes")


# =============================================================================
# 6. HTML - Web page
# =============================================================================
print("\n" + "=" * 60)
print("6. HTML - Web page")
print("=" * 60)


@weave.op()
def fetch_html(url: str = "https://example.com") -> Annotated[bytes, Content[Literal["html"]]]:
    """Return HTML as bytes so it can be previewed in Weave UI."""
    return download_bytes(url, timeout=30)


html_bytes = fetch_html()
print(f"HTML size: {len(html_bytes):,} bytes")


print("\n" + "=" * 60)
print("Multimodal Data Tracing Demo Complete!")
print("=" * 60)
print("""
Summary:
- Annotated[bytes, Content[Literal["png"]]]: PNG image
- Annotated[bytes, Content[Literal["jpg"]]]: JPG image
- Annotated[bytes, Content[Literal["mp3"]]]: MP3 audio
- Annotated[bytes, Content[Literal["mp4"]]]: MP4 video
- Annotated[bytes, Content[Literal["pdf"]]]: PDF
- Annotated[bytes, Content[Literal["html"]]]: HTML

Check in Weave UI:
- Use the Traces tab to preview images, audio, video, PDFs, and HTML
- Use Inputs/Outputs to inspect payloads stored with Content types
""")
