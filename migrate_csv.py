"""
One-off helper to migrate an old quotes_pandas.csv file (columns:
`الحكمة`, `الكاتب`) into the new schema pipeline.py expects:
`id`, `quote`, `author`, `used`, `date`.

Run this once if you already have quotes scraped under the old format.

Usage:
    python migrate_csv.py quotes_pandas.csv quotes.csv
"""
import csv
import sys

NEW_FIELDS = ["id", "quote", "author", "used", "date"]


def migrate(old_path: str, new_path: str) -> int:
    with open(old_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    with open(new_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=NEW_FIELDS)
        writer.writeheader()
        for i, row in enumerate(rows, start=1):
            writer.writerow(
                {
                    "id": i,
                    "quote": row.get("الحكمة", "").strip(),
                    "author": row.get("الكاتب", "").strip(),
                    "used": "False",
                    "date": "",
                }
            )

    return len(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python migrate_csv.py <old_csv> <new_csv>")
        raise SystemExit(1)

    count = migrate(sys.argv[1], sys.argv[2])
    print(f"Migrated {count} quote(s) into {sys.argv[2]}")