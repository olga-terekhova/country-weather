"""Extract day-number, max-temperature, and max-humidity from cities-months HTML files."""

import argparse
import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

FILENAME_PATTERN = re.compile(r'^([^-]+)-([^-]+)-([^-]+)\.html$')


def resolve_directory(raw: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = Path.cwd() / p
    p = p.resolve()
    print(f"Directory: {p}")
    return p


def extract_days(html_path: Path, city_name: str, month: str, year: str) -> list[dict]:
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    rows = []
    for day_div in soup.select("div.day_calendar[data-logger='pogoda__ForecastMonthDayItem']"):
        date_div = day_div.select_one("div.day__date")
        day_num = int(date_div.contents[0].strip())

        temp_div = day_div.select_one("div.day__temperature")
        max_temp = int(temp_div.contents[0].strip().rstrip("\u00b0"))

        hum_span = day_div.select_one("span[title^='\u0412\u043b\u0430\u0436\u043d\u043e\u0441\u0442\u044c']")
        max_humidity = int(hum_span["title"].split(": ")[1].rstrip("%"))

        rows.append({
            "city-name": city_name,
            "month": month,
            "year": year,
            "day-number": day_num,
            "max-temperature": max_temp,
            "max-humidity": max_humidity,
        })

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract weather data from cities-months HTML files into CSVs."
    )
    parser.add_argument(
        "directory",
        help="Path to directory containing HTML files (relative or absolute)",
    )
    args = parser.parse_args()

    directory = resolve_directory(args.directory)
    if not directory.exists():
        print(f"Error: directory not found: {directory}", file=sys.stderr)
        sys.exit(1)

    html_files = sorted(directory.glob("*.html"))
    if not html_files:
        print("No .html files found in directory.")
        return

    for html_path in html_files:
        match = FILENAME_PATTERN.match(html_path.name)
        if not match:
            print(
                f"Error: filename does not match expected format "
                f"[string1]-[string2]-[string3].html: {html_path.name}",
                file=sys.stderr,
            )
            sys.exit(1)

        city_name, month, year = match.group(1), match.group(2), match.group(3)
        rows = extract_days(html_path, city_name, month, year)

        csv_path = html_path.with_suffix(".csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["city-name", "month", "year", "day-number", "max-temperature", "max-humidity"],
            )
            writer.writeheader()
            writer.writerows(rows)

        print(f"{html_path.name} -> {csv_path.name} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
