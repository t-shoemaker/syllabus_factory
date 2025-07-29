#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tomllib
from pathlib import Path
from string import Template
from textwrap import wrap

from formatting import Formatter
from schedule import Scheduler
from utils import flatten_config


def main(args):
    """Run the script."""
    with args.config.open("rb") as fin:
        syllabus = tomllib.load(fin)

    # Fill out the schedule and run formatting for array items in the TOML
    formatter = Formatter()
    scheduler = Scheduler()
    syllabus.update(
        {
            "assignments": formatter.format(
                syllabus["assignments"], "assignments"
            ),
            "books": formatter.format(syllabus["books"], "books"),
            "objectives": formatter.format(
                syllabus["objectives"], "objectives"
            ),
            "course_schedule": scheduler.schedule(**syllabus["schedule"]),
        }
    )

    # Flatten the schedule config and wrap the course description
    syllabus = flatten_config(syllabus)
    description = "\n".join(
        wrap(
            syllabus["course_description"], width=79, replace_whitespace=False
        )
    )
    syllabus.update({"course_description": description})

    # Open the markdown files, then unpack syllabus values in the mapping and
    # stream out the results
    docs = [file.read_text().strip() for file in args.files]
    content = Template("\n\n".join(docs)).safe_substitute(**syllabus)
    print(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", type=Path, required=True, help="TOML syllabus config"
    )
    parser.add_argument(
        "-f",
        "--files",
        type=Path,
        nargs="+",
        required=True,
        help="Markdown files with variables",
    )
    args = parser.parse_args()
    main(args)
