"""
Text-to-speech helper built on edge-tts (Microsoft Edge neural voices).

Used both standalone (CLI) and as the narration step inside pipeline.py.
"""
from __future__ import annotations

import argparse
import asyncio
import logging

import edge_tts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DEFAULT_VOICE = "ar-SA-HamedNeural"  # mature male Saudi voice
DEFAULT_RATE = "-20%"                # 20% slower than the default speaking rate
DEFAULT_PITCH = "-10Hz"              # slightly deeper tone


async def text_to_speech(
    text: str,
    output_file: str = "output.mp3",
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
) -> str:
    """Convert `text` to an mp3 file using edge-tts.

    Returns:
        The path to the generated audio file.
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_file)
    log.info("Audio file created: %s", output_file)
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert text to speech with edge-tts.")
    parser.add_argument("text", help="Text to synthesize")
    parser.add_argument("-o", "--output", default="output.mp3", help="Output mp3 path")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--rate", default=DEFAULT_RATE)
    parser.add_argument("--pitch", default=DEFAULT_PITCH)
    args = parser.parse_args()

    asyncio.run(text_to_speech(args.text, args.output, args.voice, args.rate, args.pitch))


# Example usage from another file:
#   import asyncio
#   from tts import text_to_speech
#   asyncio.run(text_to_speech("Sample text", "test.mp3"))
#   asyncio.run(text_to_speech("Different voice", voice="ar-EG-ShakirNeural", rate="+10%"))

if __name__ == "__main__":
    main()