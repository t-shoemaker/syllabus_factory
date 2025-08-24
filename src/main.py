#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import tomllib
from pathlib import Path
from string import Template

from templates import MarkdownEntry
from utils import wrap_paragraphs, flatten_config


def format_day(day):
    """Format a day.

    Parameters
    ----------
    day : dict
        Day information

    Returns
    -------
    str
        Rendered day
    """
    no_class = day.get("no_class", False)
    weekday = day.get("weekday", "")
    date = day.get("date", "")

    if no_class:
        return MarkdownEntry.DAY.render(
            weekday=weekday,
            date=date,
            agenda=MarkdownEntry.NO_CLASS.render(),
        )

    agenda_md = "".join(
        MarkdownEntry.AGENDA_ITEM.render(item=item)
        for item in day.get("agenda", [])
    )

    return MarkdownEntry.DAY.render(
        weekday=weekday,
        date=date,
        agenda=agenda_md,
    )


def main(args):
    """Run the script."""
    with args.config.open("rb") as f:
        syllabus = tomllib.load(f)

    # Format top-level information
    for item in ("assignment", "book", "objective"):
        entries = []
        for entry in syllabus[item]:
            md = MarkdownEntry[item.upper()].render(**entry)
            entries.append(wrap_paragraphs(md))

        syllabus[item + "s"] = "\n".join(entries)

    # Format the schedule
    with args.schedule.open("rb") as f:
        schedule = tomllib.load(f)

    schedule_md = []
    for week in schedule.values():
        md = MarkdownEntry.WEEK.render(
            num=week.get("num", ""),
            title=week.get("title", ""),
        )
        schedule_md.append(md)
        for day in week.get("days", []):
            md = format_day(day)
            schedule_md.append(md)

    syllabus["course_schedule"] = "\n".join(schedule_md)

    # Flatten the schedule config and wrap the course description
    syllabus = flatten_config(syllabus)
    if "course_description" in syllabus:
        syllabus["course_description"] = wrap_paragraphs(
            syllabus["course_description"], width=79
        )

    # Open the markdown files, then unpack syllabus values in the mapping and
    # stream out the results
    docs = [file.read_text().strip() for file in args.files]
    content = Template("\n\n".join(docs)).safe_substitute(**syllabus)
    print(content)


if __name__ == "__main__":
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
    main(args)
