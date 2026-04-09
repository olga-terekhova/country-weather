"""Cross join cities and months CSVs into a single CSV using DuckDB."""

import argparse
import sys
from pathlib import Path

import duckdb


def resolve_path(raw: str, label: str) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = Path.cwd() / p
    p = p.resolve()
    print(f"{label}: {p}")
    return p


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross join cities.csv and months.csv into cities-months.csv."
    )
    parser.add_argument(
        "--cities-csv",
        default="cities/cities.csv",
        help="Path to cities CSV (default: cities/cities.csv)",
    )
    parser.add_argument(
        "--months-csv",
        default="months/months.csv",
        help="Path to months CSV (default: months/months.csv)",
    )
    parser.add_argument(
        "--cities-months-csv",
        default="cities-months/cities-months.csv",
        help="Path to output CSV (default: cities-months/cities-months.csv)",
    )
    args = parser.parse_args()

    cities_path = resolve_path(args.cities_csv, "cities-csv")
    if not cities_path.exists():
        print(f"Error: cities CSV not found: {cities_path}", file=sys.stderr)
        sys.exit(1)

    months_path = resolve_path(args.months_csv, "months-csv")
    if not months_path.exists():
        print(f"Error: months CSV not found: {months_path}", file=sys.stderr)
        sys.exit(1)

    output_path = resolve_path(args.cities_months_csv, "cities-months-csv")
    if not output_path.parent.exists():
        print(f"Creating directory: {output_path.parent}")
        output_path.parent.mkdir(parents=True)

    query = f"""
        SELECT
            cities."city-name",
            months.month,
            cities."city-url" || months.month || '/' AS "city-month-url",
            cities."city-name" || '-' || months.month || '.html' AS "city-month-file"
        FROM read_csv_auto('{cities_path}') AS cities
        CROSS JOIN read_csv_auto('{months_path}') AS months
    """

    export_query = f"COPY ({query}) TO '{output_path}' (HEADER, DELIMITER ',', QUOTE '\"', FORCE_QUOTE *)"

    conn = duckdb.connect()
    conn.execute(export_query)
    row_count = conn.execute(f"SELECT COUNT(*) FROM read_csv_auto('{output_path}')").fetchone()[0]
    conn.close()

    print(f"{row_count} rows written to {output_path}")


if __name__ == "__main__":
    main()
