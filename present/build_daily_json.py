"""Build daily.json from cities-days CSV using a three-layer hierarchy: YYYY-MM -> day -> [city records]."""

import argparse
import json
import sys
from pathlib import Path

import duckdb

MONTH_NUM = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

QUERY = """
SELECT
    year,
    month,
    "day-number" AS day,
    "city-name" AS city,
    "max-temperature" AS temperature,
    "max-humidity" AS humidity
FROM read_csv_auto('{source}')
ORDER BY 1, 2, 3, 4
"""


def resolve_path(raw: str, is_dir: bool = False) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = Path.cwd() / p
    p = p.resolve()
    label = "Output directory" if is_dir else "Source file"
    print(f"{label}: {p}")
    return p


def validate_source(path: Path) -> None:
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    if path.suffix.lower() != ".csv":
        print(f"Error: file does not have .csv extension: {path}", file=sys.stderr)
        sys.exit(1)
    if path.stat().st_size == 0:
        print(f"Error: file is empty: {path}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build daily.json from a cities-days CSV."
    )
    parser.add_argument("source", help="Path to the source CSV file (relative or absolute)")
    parser.add_argument("output_dir", help="Path to the output directory (relative or absolute)")
    args = parser.parse_args()

    source = resolve_path(args.source)
    validate_source(source)

    output_dir = resolve_path(args.output_dir, is_dir=True)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        print(f"Created output directory: {output_dir}")

    rows = duckdb.sql(QUERY.format(source=source)).fetchall()

    data: dict = {}
    for year, month, day, city, temperature, humidity in rows:
        ym_key = f"{year}-{MONTH_NUM[month]:02d}"
        day_key = str(day)
        data.setdefault(ym_key, {}).setdefault(day_key, []).append(
            {"city": city, "temperature": temperature, "humidity": humidity}
        )

    output_path = output_dir / "daily.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"Written: {output_path}")


if __name__ == "__main__":
    main()
