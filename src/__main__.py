#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import tomllib
from pathlib import Path

from compile import compile_md
from reference import get_reference_docx
from schedule import build_schedule


def load_toml(path):
    """Load TOML file.

    Parameters
    ----------
    path : Path or str
        Path to the file

    Returns
    -------
    dict
        TOML data
    """
    path = Path(path)
    with path.open("rb") as f:
        data = tomllib.load(f)

    return data


def main(argv=None):
    """Run the script."""
    parser = argparse.ArgumentParser(
        description="Compile course data into a Markdown file",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Build the schedule",
        description="Create a schedule from a syllabus config",
    )
    schedule_parser.add_argument(
        "-c",
        "--config",
        type=Path,
        required=True,
        metavar="CONFIG",
        help="Syllabus config (.toml)",
    )

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile the Markdown",
        description="Compile Markdown from syllabus and schedule configs",
    )
    compile_parser.add_argument(
        "-c",
        "--config",
        type=Path,
        required=True,
        metavar="CONFIG",
        help="Syllabus config (.toml)",
    )
    compile_parser.add_argument(
        "-s",
        "--schedule",
        type=Path,
        required=True,
        metavar="SCHEDULE",
        help="Course schedule (.toml)",
    )
    compile_parser.add_argument(
        "-f",
        "--files",
        type=Path,
        nargs="+",
        required=True,
        metavar="FILES",
        help="Templates (.md)",
    )

    reference_parser = subparsers.add_parser(
        "reference",
        help="Download a reference document",
        description="Download a TAMU minimum syllabus requirements .docx file",
    )
    reference_parser.add_argument(
        "-f",
        "--filename",
        type=Path,
        required=True,
        metavar="FILENAME",
        help="Name of the file (.docx)",
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "reference":
        get_reference_docx(args.filename)
        return

    syllabus_data = load_toml(args.config)

    if args.command == "schedule":
        build_schedule(syllabus_data)

    elif args.command == "compile":
        schedule = load_toml(args.schedule)
        compile_md(syllabus_data, schedule, args.files)


if __name__ == "__main__":
    main()
