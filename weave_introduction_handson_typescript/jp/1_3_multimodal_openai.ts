/**
 * 1_3: Multimodal Data Tracing - マルチモーダルデータのトレース
 *
 * TypeScript 対応: 一部対応
 *
 * Python 版では `Annotated[bytes, Content[Literal["png"]]]` のように、
 * bytes に media type を付けて Weave UI で preview できます。
 *
 * TypeScript SDK では現時点で公式 helper が次に限られます。
 * - weave.weaveImage({ data }) -> PNG
 * - weave.weaveAudio({ data, audioType: "wav" }) -> WAV
 *
 * JPG / MP3 / MP4 / PDF / HTML は通常 object として metadata trace はできますが、
 * Python の Content annotation と同じ media preview としては扱っていません。
 *
 * 対応状況:
 * - PNG image: Python 対応 / TypeScript 対応 (weaveImage)
 * - JPG image: Python 対応 / TypeScript 未対応 (preview helper なし)
 * - MP3 audio: Python 対応 / TypeScript 未対応 (preview helper なし)
 * - WAV audio: Python 版 1_3 では未使用 / TypeScript 対応 (weaveAudio)
 * - MP4 video: Python 対応 / TypeScript 未対応 (preview helper なし)
 * - PDF: Python 対応 / TypeScript 未対応 (preview helper なし)
 * - HTML: Python 対応 / TypeScript 未対応 (preview helper なし)
 */

import * as weave from "weave";

import {
  getImageModelName,
  getOpenAIClient,
  getTtsModelName,
  initWeave,
  printSection,
} from "../src/config.js";

await initWeave();

const SAMPLE_VISIBLE_PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAUAAAAC0CAYAAADl5PURAAADbUlEQVR42u3UMQ3DQBBFwWMSKsYQFGEWIKZkyUWKCwCXdixFb4oh8Hf1xmN5TYCiYQRAAAEEEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEAAAQQQEEBDAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCPDTAG77ZwIUCSAggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAAC+OfmOi5jTxDAVPTEEARQ9MQQBFD4hBAEUPiEEARQ+IQQBFD4hBAEUPxEEARQ/EQQBLAdPiEEARQ/EQQBrMdPBEEA0/ETQRDAdPxEEAQwHT8RBAEUQI9+8HxPbiaA4ieCAiiAAih+IiiAAiiA4ieCAiiAAiiAAiiAAiiA4ieCAiiAAiiAAiiAAiiA4ieCAiiAAiiAAiiAAiiA4ieCAiiAAiiAAhgPoJiJoAAKoAAigAIogAKIAAqgAAYCKGIiKIACKIAIoAAKoAAigAIogIEAipcICqAACiACKIACKIAIoAAKoAAigAIogAKIAAqgAAogAiiAAiiACKAACqAAIoAIoAAigAigAAqgACKAAiiAAogACqAACiACKIACKIAIoAAKoAAigAIogAKIAAqgAAogAiiAAiiACKAACqAAIoACKIACiACKoPgJoAAKoAAKoAAKoAAKoAAKoAAKoAiKnwAKoAAKoAAKoAAKoAAKoAAKoACKoPgJoAAKoAAKoAAKoACKoPgJoAAKoAAKoAAKoACKoPgJoAAKoAAKoAAKYD6AIih+AiiAAogACqAAFgMoguIngAKYDqAIip8ACmA6gCIofgIogAIogAigABYDWI+g2AmgAMYDWI2g0AmgAApgMoIiJ4ACKIDJCAqcAAqgACYjKG4CKIACmAuhqAmgAApgMoKCJoACKIDJCLqfAAqgAOZC6F4CKIACmAuh+wigAApgLoTuIYACKIC5ENpfAAVQAFMxtLMACqAApmJoTwEUQAEEARRAAQQQQAABBBBAAAEEEEAAAQQQQAABBBBAAAEEEEBAAI0ACCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAKc9wUAIELiSQyF+gAAAABJRU5ErkJggg==",
  "base64"
);

function isWeaveImage(value: unknown): value is weave.WeaveImage {
  return (
    typeof value === "object" &&
    value !== null &&
    "_weaveType" in value &&
    (value as { _weaveType?: unknown })._weaveType === "Image"
  );
}

async function imageResultToWeavePng(item: unknown): Promise<weave.WeaveImage> {
  if (isWeaveImage(item)) {
    return item;
  }

  const image = item as { b64_json?: string; url?: string };
  if (image.b64_json) {
    return weave.weaveImage({ data: Buffer.from(image.b64_json, "base64") });
  }

  if (image.url) {
    const response = await fetch(image.url);
    if (!response.ok) {
      throw new Error(`Failed to download generated image: ${response.status}`);
    }
    return weave.weaveImage({ data: Buffer.from(await response.arrayBuffer()) });
  }

  throw new Error("OpenAI image response did not include b64_json, url, or WeaveImage data.");
}

// =============================================================================
// SECTION 1: PNG Image Tracing
// =============================================================================
printSection("1. 画像 (PNG) - TypeScript 対応: weaveImage");

const createSamplePng = weave.op(function createSamplePng() {
  return weave.weaveImage({ data: SAMPLE_VISIBLE_PNG });
});

const sampleImage = await createSamplePng();
console.log(`Sample PNG recorded as Weave media: ${sampleImage._weaveType}, bytes=${sampleImage.data.length}`);

const generateImage = weave.op(async function generateImage(prompt: string) {
  const response = await getOpenAIClient().images.generate({
    model: getImageModelName(),
    prompt,
    size: "1024x1024",
  });
  const firstImage = response.data?.[0];
  if (!firstImage) {
    throw new Error("OpenAI image response did not include any image data.");
  }
  return imageResultToWeavePng(firstImage);
});

if (process.env.RUN_EXPENSIVE_MULTIMODAL === "1") {
  const generated = await generateImage("a small robot watering a flower in a lab, pixel art style");
  console.log(`Generated PNG recorded as Weave media: ${generated._weaveType}`);
} else {
  console.log("RUN_EXPENSIVE_MULTIMODAL=1 を設定すると OpenAI 画像生成の PNG trace 例を実行します。");
}

// =============================================================================
// SECTION 2: JPG Image Tracing
// =============================================================================
// TypeScript 対応: 未対応
// Python 版:
//   def create_sample_jpg_image() -> Annotated[bytes, Content[Literal["jpg"]]]:
//       ...
//
// TypeScript SDK の ImageType は現時点で "png" のみです。
// JPG bytes を Python 版と同じ media preview として trace する helper はありません。

// =============================================================================
// SECTION 3: MP3 Audio Tracing
// =============================================================================
// TypeScript 対応: 未対応
// Python 版:
//   def text_to_speech(...) -> Annotated[bytes, Content[Literal["mp3"]]]:
//       ...
//
// OpenAI TTS は TypeScript でも response_format: "mp3" を指定できます。
// ただし TypeScript SDK の AudioType は現時点で "wav" のみなので、
// MP3 bytes を Python 版と同じ media preview として trace する helper はありません。

// =============================================================================
// SECTION 4: WAV Audio Tracing
// =============================================================================
printSection("4. 音声 (WAV) - TypeScript 対応: weaveAudio");

const textToSpeechWav = weave.op(async function textToSpeechWav(text: string) {
  const response = await getOpenAIClient().audio.speech.create({
    model: getTtsModelName(),
    voice: "alloy",
    input: text,
    response_format: "wav",
  });
  return weave.weaveAudio({ data: Buffer.from(await response.arrayBuffer()), audioType: "wav" });
});

if (process.env.RUN_EXPENSIVE_MULTIMODAL === "1") {
  const audio = await textToSpeechWav(
    "Weights and Biases Weave helps you trace, evaluate, and monitor LLM applications."
  );
  console.log(`Generated WAV recorded as Weave media: ${audio._weaveType}`);
} else {
  console.log("RUN_EXPENSIVE_MULTIMODAL=1 を設定すると OpenAI TTS の WAV trace 例を実行します。");
}

// =============================================================================
// SECTION 5: MP4 Video Tracing
// =============================================================================
// TypeScript 対応: 未対応
// Python 版:
//   def generate_video(...) -> Annotated[bytes, Content[Literal["mp4"]]]:
//       ...
//
// TypeScript SDK には MP4 用の media helper がありません。
// この教材では TypeScript 版の MP4 trace 実行例は用意していません。

// =============================================================================
// SECTION 6: PDF Tracing
// =============================================================================
// TypeScript 対応: 未対応
// Python 版:
//   def fetch_arxiv_pdf(...) -> Annotated[bytes, Content[Literal["pdf"]]]:
//       ...
//
// TypeScript SDK には PDF 用の Content annotation / media helper がありません。
// PDF を扱う場合は URL や byte size などを通常 object として trace する代替になります。

// =============================================================================
// SECTION 7: HTML Tracing
// =============================================================================
// TypeScript 対応: 未対応
// Python 版:
//   def fetch_html(...) -> Annotated[bytes, Content[Literal["html"]]]:
//       ...
//
// TypeScript SDK には HTML 用の Content annotation / media helper がありません。
// HTML を扱う場合は preview text や metadata object として trace する代替になります。

// =============================================================================
// COMPLETE
// =============================================================================
printSection("Multimodal Data Tracing Demo Complete!");
console.log(`
まとめ:
- Python: png / jpg / mp3 / mp4 / pdf / html を Content annotation で media preview として trace
- TypeScript: PNG は weaveImage で media trace
- TypeScript: WAV は weaveAudio で media trace
- TypeScript: JPG / MP3 / MP4 / PDF / HTML は、この教材ではコメントで未対応理由のみ説明
`);
