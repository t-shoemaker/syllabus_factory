#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tomllib
from pathlib import Path

from render import render_md


def main(argv=None):
    """Run the script."""
    parser = argparse.ArgumentParser(description="Render course Markdown")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        required=True,
        help="Syllabus config (.toml)",
    )
    parser.add_argument(
        "-s",
        "--schedule",
        type=Path,
        required=True,
        help="Course schedule (.toml)",
    )
    parser.add_argument(
        "-f",
        "--files",
        type=Path,
        nargs="+",
        required=True,
        help="Templates (.md)",
    )
    args = parser.parse_args()

    # Open the syllabus and config
    with args.config.open("rb") as f:
        syllabus_data = tomllib.load(f)

    with args.schedule.open("rb") as f:
        schedule = tomllib.load(f)

    render_md(syllabus_data, schedule, args.files)


if __name__ == "__main__":
    main()
