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


class SpecialCourseDesignation(SyllabusItem):
    """Special course designations (CORE)."""

    KLPC = """\
    This course is specially designated as a Language, Philosophy, and Culture 
    core course. As such, the list below indicates the learning objectives 
    that come with the KLPC designation.

    1. Critical Thinking - The course will enhance creative thinking; 
    innovation; inquiry; and analysis, evaluation, and synthesis of 
    information through consistent reading and class discussion of key ideas 
    in various literary traditions in world literature.
    2. Communication Skills - The course will focus on the effective 
    development, interpretation, and expression of ideas through written, 
    oral, and visual communication.
    3. Social Responsibility - The course enhances intercultural competence; 
    knowledge of civic responsibility; and the ability to engage effectively 
    in regional, national, and global communities through various activities, 
    written assignments, exams, and class discussions that focus on how 
    history, religion, culture, and broader social forces have shaped the 
    distinctive literary traditions from around the world.
    4. Personal Responsibility - The course enhances the ability to connect 
    choices, actions, and consequences to ethical decision-making.\\
    """
