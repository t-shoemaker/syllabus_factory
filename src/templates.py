from enum import Enum
from string import Template

from utils import dedent


class SyllabusItem(Enum):
    """Base template class for Markdown entries."""

    def render(self, **kwargs):
        """Render an entry.

        Parameters
        ----------
        kwargs : dict
            Keywords for the template

        Returns
        -------
        str
            The rendered entry
        """
        template_str = dedent(self.value, indent=4)
        return Template(template_str).safe_substitute(**kwargs)


class ScheduleEntry(SyllabusItem):
    """Entries for the TOML schedule."""

    WEEK = """\
    [week-$num]
    num = $num
    title = ""
    """
    DAY = """\
      [[week-$num.days]]
      date = "$month/$day"
      weekday = "$weekday"
      no_class = $no_class
      agenda = []
    """


class MarkdownEntry(SyllabusItem):
    """Entries for the rendered markdown."""

    OBJECTIVE = "+ $description"
    BOOK = "+ $author. $title ($isbn)"
    ASSIGNMENT = "| $due | $points | $name |"
    WEEK = """\
    **[Week $num -- $title]{.smallcaps}**
    """
    DAY = """\
    $weekday ($date)

    $agenda\\
    """
    AGENDA_ITEM = """+ $item\n"""
    NO_CLASS = """+ **No class**\n"""
