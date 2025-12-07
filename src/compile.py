from string import Template

from templates import MarkdownEntry, SpecialCourseDesignation
from utils import wrap_paragraphs, flatten_config


def format_toml_tables(syllabus_data, items=None):
    """Format tables of arrays.

    Parameters
    ----------
    syllabus_data : dict
        Course metadata
    items : iterable or None
        Keys to access tables

    Returns
    -------
    dict
        Syllabus data with formatted tables
    """
    for item in items:
        entries = []
        for entry in syllabus_data[item]:
            entry_md = MarkdownEntry[item.upper()].render(**entry)
            entries.append(wrap_paragraphs(entry_md))

        syllabus_data[item + "s"] = "\n".join(entries)

    return syllabus_data


def format_schedule(schedule):
    """Format the schedule.

    Parameters
    ----------
    schedule : dict
        The schedule weeks

    Returns
    -------
    str
        Formatted schedule
    """
    schedule_md = []
    for week in schedule.values():
        num = week.get("num", "")
        title = week.get("title", "")

        week_md = MarkdownEntry.WEEK.render(num=num, title=title)
        schedule_md.append(week_md)

        for day in week.get("days", []):
            day_md = format_day(day)
            schedule_md.append(day_md)

    return "\n".join(schedule_md)


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


def format_course_designation(designation):
    """Format course designation.

    Parameters
    ----------
    designation : str
        The course designation code

    Returns
    -------
    str
        Course designation

    Raises
    ------
    NotImplementedError
        If the course designation doesn't have a template
    """
    if designation == "None":
        return designation
    elif designation == "KLPC":
        return SpecialCourseDesignation.KLPC.render()
    else:
        raise NotImplementedError(f"No template for {designation}")


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
    items = ("assignment", "book", "objective")
    syllabus_data = format_toml_tables(syllabus_data, items)
    syllabus_data["course_schedule"] = format_schedule(schedule)

    # Flatten the config for the rest of the items -- they aren't nested
    syllabus_data = flatten_config(syllabus_data)
    syllabus_data["course_description"] = wrap_paragraphs(
        syllabus_data.get("course_description", ""), width=79
    )

    desig = syllabus_data.get("course_designation", "None")
    syllabus_data["course_designation"] = format_course_designation(desig)

    # Open the markdown files, then unpack syllabus values in the mapping and
    # stream out the results
    docs = [file.read_text().strip() for file in md_files]
    content = Template("\n\n".join(docs)).safe_substitute(**syllabus_data)
    print(content)
