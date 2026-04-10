"""Union separate city-month CSV files into a single dataset."""

import argparse
import csv
import sys
from pathlib import Path

HEADERS = ["city-name", "month", "year", "day-number", "max-temperature", "max-humidity"]


def resolve_directory(raw: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = Path.cwd() / p
    p = p.resolve()
    print(f"Input directory: {p}")
    return p


def resolve_output(raw: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = Path.cwd() / p
    p = p.resolve()
    print(f"Output file: {p}")
    return p


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Union city-month CSV files into a single dataset."
    )
    parser.add_argument(
        "directory",
        help="Path to directory containing CSV files (relative or absolute)",
    )
    parser.add_argument(
        "--output",
        default="cities-days/cities-days.csv",
        help="Path to output file (relative or absolute). Default: cities-days/cities-days.csv",
    )
    args = parser.parse_args()

    directory = resolve_directory(args.directory)
    if not directory.exists():
        print(f"Error: directory not found: {directory}", file=sys.stderr)
        sys.exit(1)

    output_path = resolve_output(args.output)
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)
        print(f"Created directory: {output_path.parent}")

    csv_files = sorted(directory.glob("*.csv"))

    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(HEADERS)

        for csv_path in csv_files:
            with open(csv_path, newline="", encoding="utf-8") as in_f:
                reader = csv.reader(in_f)
                file_headers = next(reader, None)

                if file_headers != HEADERS:
                    print(f"Warning: skipping {csv_path.name} — schema mismatch: {file_headers}")
                    continue

                rows = list(reader)
                if not rows:
                    print(f"Warning: skipping {csv_path.name} — no data rows.")
                    continue

                writer.writerows(rows)
                print(f"{csv_path.name} -> {len(rows)} rows written")


if __name__ == "__main__":
    main()
