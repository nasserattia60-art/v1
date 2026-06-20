"""
Text-to-speech helper built on edge-tts (Microsoft Edge neural voices).

Used both standalone (CLI) and as the narration step inside pipeline.py.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

import edge_tts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DEFAULT_VOICE: str = "ar-SA-HamedNeural"  # mature male Saudi voice
DEFAULT_RATE: str = "-20%"  # 20% slower than the default speaking rate
DEFAULT_PITCH: str = "-10Hz"  # slightly deeper tone

# ---------------------------------------------------------------------------
# Pure construction  (no I/O – easy to test / mock)
# ---------------------------------------------------------------------------


def build_synthesizer(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
) -> edge_tts.Communicate:
    """Create an edge-tts Communicate object for the given parameters.

    Args:
        text: The text to synthesize.
        voice: An edge-tts voice name (e.g. ``"ar-SA-HamedNeural"``).
        rate: Speaking-rate adjustment (e.g. ``"-20%"``).
        pitch: Pitch adjustment (e.g. ``"-10Hz"``).

    Returns:
        A configured ``edge_tts.Communicate`` instance ready for streaming
        or saving.

    Raises:
        ValueError: If ``text`` is empty or whitespace-only.
    """
    if not text or not text.strip():
        raise ValueError("text must be a non-empty string")

    return edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


async def save_audio_stream(
    synthesizer: edge_tts.Communicate,
    output_path: str,
) -> str:
    """Stream audio chunks from a synthesizer and write them to a file.

    Args:
        synthesizer: An ``edge_tts.Communicate`` instance (from
            :func:`build_synthesizer`).
        output_path: Destination file path for the generated audio.

    Returns:
        The absolute path of the written file.

    Raises:
        OSError: If the output directory cannot be created.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    await synthesizer.save(str(output_file))
    log.info("Audio file created: %s", output_file)
    return str(output_file.resolve())


# ---------------------------------------------------------------------------
# Public API (convenience wrapper)
# ---------------------------------------------------------------------------


async def text_to_speech(
    text: str,
    output_file: str = "output.mp3",
    voice: str = DEFAULT_VOICE,
    rate: str = DEFAULT_RATE,
    pitch: str = DEFAULT_PITCH,
) -> str:
    """Convert ``text`` to an mp3 file using edge-tts.

    This is a convenience function that combines :func:`build_synthesizer`
    and :func:`save_audio_stream` into a single call.

    Args:
        text: The text to synthesize.
        output_file: Path for the generated audio file.
        voice: An edge-tts voice name.
        rate: Speaking-rate adjustment.
        pitch: Pitch adjustment.

    Returns:
        The absolute path to the generated audio file.

    Raises:
        ValueError: If ``text`` is empty.
        OSError: If the output directory cannot be created.
    """
    synthesizer = build_synthesizer(text, voice=voice, rate=rate, pitch=pitch)
    return await save_audio_stream(synthesizer, output_file)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for the TTS utility.

    Returns:
        A configured ``ArgumentParser``.
    """
    parser = argparse.ArgumentParser(
        description="Convert text to speech with edge-tts."
    )
    parser.add_argument("text", help="Text to synthesize")
    parser.add_argument("-o", "--output", default="output.mp3", help="Output mp3 path")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="edge-tts voice name")
    parser.add_argument("--rate", default=DEFAULT_RATE, help="Speaking-rate adjustment")
    parser.add_argument("--pitch", default=DEFAULT_PITCH, help="Pitch adjustment")
    return parser


def main() -> None:
    """Parse CLI arguments and run the TTS synthesis."""
    parser = build_parser()
    args = parser.parse_args()

    asyncio.run(
        text_to_speech(
            text=args.text,
            output_file=args.output,
            voice=args.voice,
            rate=args.rate,
            pitch=args.pitch,
        )
    )


# ---------------------------------------------------------------------------
# Example usage from another file:
#   import asyncio
#   from tts import text_to_speech
#   asyncio.run(text_to_speech("Sample text", "test.mp3"))
#   asyncio.run(
#       text_to_speech("Different voice", voice="ar-EG-ShakirNeural", rate="+10%")
#   )
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()