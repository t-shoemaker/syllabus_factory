from string import Template

from templates import MarkdownEntry, SpecialCourseDesignation
from utils import flatten_config, wrap_paragraphs


class SyllabusValidator:
    """Validates syllabus data before compilation."""

    REQUIRED = ["instructor", "course", "schedule"]

    def validate(self, syllabus_data):
        """Validate required fields and data types.

        Parameters
        ----------
        syllabus_data : dict
            Course metadata

        Raises
        ------
        ValueError
            If required fields are missing or invalid
        """
        missing = [f for f in self.REQUIRED if f not in syllabus_data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")


class FormatterRegistry:
    """Registry of data formatters for different content types."""

    def __init__(self):
        """Initialize the object."""
        self._formatters = {}

    def register(self, key, func):
        """Register a formatter for a data key.

        Parameters
        ----------
        key : str
            The data key to format
        func : callable
            Function that formats the data
        """
        self._formatters[key] = func

    def format(self, key, data):
        """Apply registered formatter to data.

        Parameters
        ----------
        key : str
            The data key
        data : any
            The data to format

        Returns
        -------
        any
            Formatted data, or original if no formatter registered
        """
        if key in self._formatters:
            return self._formatters[key](data)

        return data

    def has_formatter(self, key):
        """Check if a formatter is registered for a key.

        Parameters
        ----------
        key : str
            The data key for a formatter

        Returns
        -------
        bool
            If True, the formatter is registered
        """
        return key in self._formatters


class TableFormatter:
    """Formats TOML table arrays into markdown."""

    @staticmethod
    def format_items(items, item_type):
        """Format a list of items into markdown.

        Parameters
        ----------
        items : list[dict]
            List of items to format
        item_type : str
            Type of item (objective, book, assignment)

        Returns
        -------
        str
            Formatted markdown entries
        """
        entries = []
        for entry in items:
            entry_md = MarkdownEntry[item_type.upper()].render(**entry)
            entries.append(wrap_paragraphs(entry_md))

        return "\n".join(entries)


class ScheduleFormatter:
    """Formats schedule data into markdown."""

    def __init__(self, schedule_data):
        """Initialize the object.

        Parameters
        ----------
        schedule_data : dict
            Schedule data
        """
        self.schedule = schedule_data

    def format(self):
        """Format complete schedule.

        Returns
        -------
        str
            Formatted schedule markdown
        """
        return "\n".join(
            self._format_week(week) for week in self.schedule.values()
        )

    def _format_week(self, week):
        """Format a single week.

        Parameters
        ----------
        week : dict
            Week data

        Returns
        -------
        str
            Formatted week markdown
        """
        num = week.get("num", "")
        title = week.get("title", "")

        week_md = MarkdownEntry.WEEK.render(num=num, title=title)
        days = "\n".join(self._format_day(day) for day in week.get("days", []))

        return f"{week_md}\n{days}"

    def _format_day(self, day):
        """Format a single day.

        Parameters
        ----------
        day : dict
            Day information

        Returns
        -------
        str
            Rendered day markdown
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
            weekday=weekday, date=date, agenda=agenda_md
        )


class DescriptionFormatter:
    """Formats text descriptions with word wrapping."""

    def __init__(self, width=79):
        """Initialize the object.

        Parameters
        ----------
        width : int
            Width for word wrapping
        """
        self.width = width

    def format(self, text):
        """Format a description with paragraph wrapping.

        Parameters
        ----------
        text : str
            Text to format

        Returns
        -------
        str
            Wrapped text
        """
        return wrap_paragraphs(text, width=self.width)


class DesignationFormatter:
    """Formats course designations."""

    @staticmethod
    def format(designation):
        """Format course designation.

        Parameters
        ----------
        designation : str
            The course designation code

        Returns
        -------
        str
            Formatted course designation

        Raises
        ------
        NotImplementedError
            If the course designation doesn't have a template
        """
        match designation:
            case "None":
                return designation
            case "KLPC":
                return SpecialCourseDesignation.KLPC.render()
            case _:
                raise NotImplementedError(f"No template for {designation}")


class SyllabusDataFormatter:
    """Handles all syllabus data transformations."""

    tables = ("assignment", "book", "objective")
    descriptors = [
        ("catalog_description", "course_catalog"),
        ("section_description", "course_description"),
    ]

    def __init__(self, syllabus_data, schedule):
        """Initialize the object.

        Parameters
        ----------
        syllabus_data : dict
            Course metadata
        schedule : dict
            Schedule data
        """
        self.data = syllabus_data.copy()
        self.schedule = schedule
        self.registry = self._create_registry()

    def _create_registry(self):
        """Create and configure the formatter registry.

        Returns
        -------
        FormatterRegistry
            The formatter registry
        """
        registry = FormatterRegistry()

        # Register table formatters
        for item_type in self.tables:
            registry.register(
                item_type,
                lambda items, t=item_type: TableFormatter.format_items(
                    items, t
                ),
            )

        return registry

    def format(self):
        """Apply all formatting transformations.

        Returns
        -------
        dict
            Formatted syllabus data
        """
        self._format_tables()
        self._format_schedule()
        self._flatten_data()
        self._format_descriptions()
        self._format_designation()

        return self.data

    def _format_tables(self):
        """Format TOML table arrays."""
        for item_type in self.tables:
            if item_type not in self.data:
                continue

            md = self.registry.format(item_type, self.data[item_type])
            self.data[f"{item_type}s"] = md

    def _format_schedule(self):
        """Format the schedule."""
        formatter = ScheduleFormatter(self.schedule)
        self.data["course_schedule"] = formatter.format()

    def _flatten_data(self):
        """Flatten nested data structure."""
        self.data = flatten_config(self.data)

    def _format_descriptions(self):
        """Format catalog and course descriptions."""
        formatter = DescriptionFormatter()
        for new_key, old_key in self.descriptors:
            if old_key not in self.data:
                continue

            self.data[new_key] = formatter.format(self.data[old_key])

    def _format_designation(self):
        """Format course designation."""
        desig = self.data.get("course_designation", "None")
        self.data["course_designation"] = DesignationFormatter.format(desig)


class TemplateRenderer:
    """Renders markdown templates with formatted data."""

    def __init__(self, template_paths):
        """Initialize the object.

        Parameters
        ----------
        template_paths : list[Path]
            Paths to template files
        """
        self.template_paths = template_paths

    def render(self, context):
        """Render templates with provided context.

        Parameters
        ----------
        context : dict
            Template context data

        Returns
        -------
        str
            Rendered markdown content
        """
        docs = [path.read_text().strip() for path in self.template_paths]
        template = Template("\n\n".join(docs))

        return template.safe_substitute(**context)


class SyllabusCompiler:
    """Compiles syllabus data into markdown."""

    def __init__(self, syllabus_data, schedule, template_paths):
        """Initialize the object.

        Parameters
        ----------
        syllabus_data : dict
            Course metadata
        schedule : dict
            Schedule data
        template_paths : list[Path]
            Paths to template files
        """
        self.syllabus_data = syllabus_data
        self.schedule = schedule
        self.template_paths = template_paths
        self.validator = SyllabusValidator()

    def compile(self):
        """Execute the compilation pipeline.

        Returns
        -------
        str
            Compiled markdown

        Raises
        ------
        ValueError
            If validation fails
        """
        self.validator.validate(self.syllabus_data)

        formatter = SyllabusDataFormatter(self.syllabus_data, self.schedule)
        formatted = formatter.format()

        renderer = TemplateRenderer(self.template_paths)
        output = renderer.render(formatted)

        return output


def compile_md(syllabus_data, schedule, template_paths):
    """Compile to markdown and send to stdout.

    Parameters
    ----------
    syllabus_data : dict
        Course metadata
    schedule : dict
        Schedule data
    template_paths : list[Path]
        Paths to template files
    """
    compiler = SyllabusCompiler(syllabus_data, schedule, template_paths)
    output = compiler.compile()
    print(output)
