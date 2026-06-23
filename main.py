from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import PROJECT_ROOT
from engine.generator import ContentGenerator, GeneratorError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate social carousel slides from a CSV file and local images."
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to the CSV file containing post definitions.",
    )
    parser.add_argument(
        "--platform",
        default="tiktok",
        choices=["tiktok", "pinterest"],
        help="Target platform preset.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = PROJECT_ROOT / csv_path

    try:
        generator = ContentGenerator(platform=args.platform)
        generated = generator.generate_from_csv(csv_path)
    except GeneratorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Generated {generated} post(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
