"""
Video helpers: muxing narration audio onto a background video clip.

The ffmpeg-based implementation is the default used by pipeline.py — it's
fast and needs no heavy Python video libraries. A moviepy-based fallback is
kept here too, for cases where you need clip-level editing ffmpeg alone
won't give you easily (the moviepy import is also fixed for moviepy 2.0+,
which dropped the old `moviepy.editor` module used in the original script).
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def merge_audio_video_ffmpeg(audio_path: str, video_path: str, output_path: str) -> bool:
    """Mux `audio_path` onto `video_path`, replacing any existing audio track.

    Returns:
        True on success, False if ffmpeg reported an error.
    """
    for path in (audio_path, video_path):
        if not Path(path).exists():
            log.error("Input file not found: %s", path)
            return False

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        log.info("Final video created: %s", output_path)
        return True

    log.error("ffmpeg failed: %s", result.stderr.strip()[-500:])
    return False


def merge_audio_video_moviepy(audio_path: str, video_path: str, output_path: str) -> bool:
    """Same result as merge_audio_video_ffmpeg, via moviepy.

    Slower and pulls in a heavier dependency, but handy if you later want
    clip-level edits (trimming, fades, overlays) before muxing.
    Requires the `moviepy` package.
    """
    try:
        from moviepy import VideoFileClip, AudioFileClip  # moviepy >= 2.0
    except ImportError:
        from moviepy.editor import VideoFileClip, AudioFileClip  # moviepy < 2.0

    for path in (audio_path, video_path):
        if not Path(path).exists():
            log.error("Input file not found: %s", path)
            return False

    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    try:
        if hasattr(video_clip, "with_audio"):  # moviepy >= 2.0 API
            final_clip = video_clip.with_audio(audio_clip)
        else:  # moviepy < 2.0 API
            final_clip = video_clip.set_audio(audio_clip)

        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        log.info("Final video created: %s", output_path)
        return True
    except Exception as exc:  # surfacing any moviepy failure instead of crashing silently
        log.error("moviepy merge failed: %s", exc)
        return False
    finally:
        video_clip.close()
        audio_clip.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Merge an audio track onto a video.")
    parser.add_argument("audio", help="Path to the audio file")
    parser.add_argument("video", help="Path to the background video")
    parser.add_argument("-o", "--output", default="final_output.mp4")
    parser.add_argument("--engine", choices=["ffmpeg", "moviepy"], default="ffmpeg")
    args = parser.parse_args()

    merge_fn = merge_audio_video_ffmpeg if args.engine == "ffmpeg" else merge_audio_video_moviepy
    merge_fn(args.audio, args.video, args.output)