"""
Scraper for Arabic wisdom quotes.

Fetches <blockquote> entries from a source page, de-duplicates against an
existing CSV, and appends new quotes using a stable schema:

    id, quote, author, used, date

That schema is important: it's exactly what pipeline.py expects later on.
"""
from __future__ import annotations

import argparse
import csv
import logging
import os
from dataclasses import dataclass
from typing import Iterable

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Kept identical to the original source URL (Arabic IDN domain + percent-encoded path).
DEFAULT_URL = "http://حكم.net/%d8%ad%d9%83%d9%85-%d8%b9%d9%86-%d8%a7%d9%84%d8%ae%d8%b3%d8%a7%d8%b1%d8%a9"
DEFAULT_CSV = "quotes.csv"
FIELDNAMES = ["id", "quote", "author", "used", "date"]
REQUEST_TIMEOUT = 15


@dataclass(frozen=True)
class Quote:
    quote: str
    author: str


def fetch_page(url: str, timeout: int = REQUEST_TIMEOUT) -> str:
    """Download a page and return its correctly-decoded HTML text.

    Raises:
        requests.RequestException: on network failure or a non-2xx status.
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    response.encoding = response.apparent_encoding  # fixes Arabic mojibake
    return response.text


def parse_quotes(html: str) -> list[Quote]:
    """Extract quotes from every <blockquote> block on the page."""
    soup = BeautifulSoup(html, "html.parser")
    quotes: list[Quote] = []

    for block in soup.find_all("blockquote"):
        paragraph = block.find("p")
        quote_text = paragraph.text.strip() if paragraph else None
        if not quote_text:
            continue  # skip blocks with no usable text instead of storing junk

        author_el = block.find("cite", class_="author")
        author = author_el.text.strip() if author_el else "Unknown"
        quotes.append(Quote(quote=quote_text, author=author))

    return quotes


def load_existing(csv_path: str) -> tuple[set[tuple[str, str]], int]:
    """Read an existing CSV (if any) and return (seen keys, next free id)."""
    seen: set[tuple[str, str]] = set()
    max_id = 0

    if not os.path.exists(csv_path):
        return seen, 1

    with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            seen.add((row.get("quote", ""), row.get("author", "")))
            try:
                max_id = max(max_id, int(row.get("id", 0)))
            except ValueError:
                pass

    return seen, max_id + 1


def append_quotes(
    csv_path: str,
    quotes: Iterable[Quote],
    seen: set[tuple[str, str]],
    next_id: int,
) -> int:
    """Append quotes not already present in `seen`. Returns how many were added."""
    file_has_content = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
    added = 0

    with open(csv_path, mode="a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_has_content:
            writer.writeheader()

        for q in quotes:
            key = (q.quote, q.author)
            if key in seen:
                continue
            writer.writerow(
                {"id": next_id, "quote": q.quote, "author": q.author, "used": "False", "date": ""}
            )
            seen.add(key)
            next_id += 1
            added += 1

    return added


def scrape(url: str, csv_path: str) -> int:
    """Run fetch -> parse -> dedupe -> append. Returns the number of new quotes."""
    log.info("Fetching %s", url)
    html = fetch_page(url)

    quotes = parse_quotes(html)
    log.info("Found %d quote block(s) on the page", len(quotes))

    seen, next_id = load_existing(csv_path)
    added = append_quotes(csv_path, quotes, seen, next_id)

    log.info("Added %d new quote(s) to %s (total known: %d)", added, csv_path, len(seen))
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Arabic quotes into a CSV file.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Source page URL")
    parser.add_argument("--csv", default=DEFAULT_CSV, help="Path to the quotes CSV")
    args = parser.parse_args()

    try:
        scrape(args.url, args.csv)
    except requests.RequestException as exc:
        log.error("Failed to fetch page: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()