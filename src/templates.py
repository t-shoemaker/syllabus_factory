import re
from enum import Enum
from string import Template


def dedent(string, indent=4):
    """Dedent a triple-quoted string.

    Parameters
    ----------
    string : str
        The string
    indent : int
        How many spaces to dedent

    Returns
    -------
    str
        The dedented string
    """
    return re.sub(r"(?m)^ {4}", "", string)


class ScheduleEntry(Enum):
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
        template_str = dedent(self.value)
        return Template(template_str).safe_substitute(**kwargs)


class MarkdownEntry(Enum):
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
        template_str = dedent(self.value)
        return Template(template_str).safe_substitute(**kwargs)
