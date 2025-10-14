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


def compile_md(syllabus_data, schedule, md_files):
    """Compile Markdown and send to stdout.

    Parameters
    ----------
    syllabus_data : dict
        Course metadata
    schedule : dict
        Schedule of meetings
    md_files : list[Path]
        Markdown template files for each syllabus component
    """
    # Format top-level information
    for item in ("assignment", "book", "objective"):
        entries = []
        for entry in syllabus_data[item]:
            md = MarkdownEntry[item.upper()].render(**entry)
            entries.append(wrap_paragraphs(md))

        syllabus_data[item + "s"] = "\n".join(entries)

    # Format the schedule
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

    syllabus_data["course_schedule"] = "\n".join(schedule_md)

    # Flatten the schedule config and wrap the course description
    syllabus_data = flatten_config(syllabus_data)
    if "course_description" in syllabus_data:
        syllabus_data["course_description"] = wrap_paragraphs(
            syllabus_data["course_description"], width=79
        )

    # Open the markdown files, then unpack syllabus values in the mapping and
    # stream out the results
    docs = [file.read_text().strip() for file in md_files]
    content = Template("\n\n".join(docs)).safe_substitute(**syllabus_data)
    print(content)
