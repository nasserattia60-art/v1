"""
End-to-end pipeline: pick the next unused quote from the CSV, narrate it
with TTS, lay the narration over a background video, then mark the quote
as used so it isn't processed again.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import logging
import os
from datetime import datetime
from typing import Optional

from tts import text_to_speech, DEFAULT_VOICE, DEFAULT_RATE, DEFAULT_PITCH
from video import merge_audio_video_ffmpeg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

CSV_FILE = "quotes.csv"
VIDEO_BG = "background.mp4"
OUTPUT_DIR = "output"
FIELDNAMES = ["id", "quote", "author", "used", "date"]


# ------- CSV helpers -------

def load_rows(csv_file: str) -> list[dict]:
    with open(csv_file, mode="r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def save_rows(csv_file: str, rows: list[dict]) -> None:
    with open(csv_file, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def get_next_quote(csv_file: str = CSV_FILE) -> tuple[Optional[dict], list[dict]]:
    """Return (first unused row, all rows), or (None, rows) if none are left."""
    rows = load_rows(csv_file)
    for row in rows:
        if row.get("used", "False").strip() != "True":
            return row, rows
    return None, rows


def mark_as_used(quote_id: str, rows: list[dict], csv_file: str = CSV_FILE) -> None:
    """Flip a row's `used` flag and stamp the processing date, then rewrite the CSV."""
    for row in rows:
        if row["id"] == quote_id:
            row["used"] = "True"
            row["date"] = datetime.now().isoformat()
            break
    save_rows(csv_file, rows)


# ------- Processing -------

async def process_quote(
    quote_id: str,
    quote_text: str,
    author: str,
    output_dir: str = OUTPUT_DIR,
    video_bg: str = VIDEO_BG,
) -> tuple[str, str]:
    """Narrate one quote and merge the narration onto the background video.

    Returns:
        (audio_file_path, video_file_path)

    Raises:
        RuntimeError: if the video merge step fails.
    """
    os.makedirs(output_dir, exist_ok=True)

    full_text = f"{quote_text}. Said by: {author}"
    audio_file = os.path.join(output_dir, f"{quote_id}.mp3")
    video_file = os.path.join(output_dir, f"{quote_id}.mp4")

    log.info("Processing quote #%s by %s", quote_id, author)
    log.info("Text: %s", quote_text)

    await text_to_speech(full_text, audio_file, DEFAULT_VOICE, DEFAULT_RATE, DEFAULT_PITCH)

    if not merge_audio_video_ffmpeg(audio_file, video_bg, video_file):
        raise RuntimeError(f"Video merge failed for quote #{quote_id}")

    return audio_file, video_file


async def process_next_quote(
    csv_file: str = CSV_FILE,
    video_bg: str = VIDEO_BG,
    output_dir: str = OUTPUT_DIR,
) -> Optional[dict]:
    """Process a single, next unused quote.

    Returns:
        A dict describing the result, or None if there was nothing to do.
    """
    if not os.path.exists(video_bg):
        log.warning("Background video '%s' not found — add it before running.", video_bg)
        return None

    if not os.path.exists(csv_file):
        log.warning("CSV file '%s' not found — run the scraper first.", csv_file)
        return None

    quote, all_rows = get_next_quote(csv_file)
    if quote is None:
        log.info("All quotes have already been processed.")
        return None

    quote_id = quote["id"]
    audio_file, video_file = await process_quote(
        quote_id, quote["quote"], quote["author"], output_dir, video_bg
    )
    mark_as_used(quote_id, all_rows, csv_file)

    log.info("Quote #%s done -> %s", quote_id, video_file)
    return {
        "id": quote_id,
        "text": quote["quote"],
        "author": quote["author"],
        "audio": audio_file,
        "video": video_file,
    }


async def process_all_quotes(
    csv_file: str = CSV_FILE,
    video_bg: str = VIDEO_BG,
    output_dir: str = OUTPUT_DIR,
) -> int:
    """Process every unused quote in sequence. Returns how many were processed."""
    count = 0
    while True:
        result = await process_next_quote(csv_file, video_bg, output_dir)
        if result is None:
            break
        count += 1

    log.info("Processed %d quote(s) this run.", count)
    return count


# ✅ Example usage from another file:
# import asyncio
# from pipeline import process_next_quote, process_all_quotes
#
# asyncio.run(process_next_quote())          # process exactly one quote
# asyncio.run(process_all_quotes())          # process every remaining quote


def main() -> None:
    parser = argparse.ArgumentParser(description="Turn quotes into narrated videos.")
    parser.add_argument("--csv", default=CSV_FILE)
    parser.add_argument("--video", default=VIDEO_BG)
    parser.add_argument("--output-dir", default=OUTPUT_DIR)
    parser.add_argument("--all", action="store_true", help="Process every unused quote, not just one")
    args = parser.parse_args()

    if args.all:
        asyncio.run(process_all_quotes(args.csv, args.video, args.output_dir))
    else:
        asyncio.run(process_next_quote(args.csv, args.video, args.output_dir))


if __name__ == "__main__":
    main()