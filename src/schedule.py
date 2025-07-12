import calendar
from datetime import datetime, timedelta

from formatting import Formatter


class Scheduler:
    format = "%Y-%m-%d"
    day_abbr = list(calendar.day_abbr)
    weekday_map = {"M": "Mon", "T": "Tue", "W": "Wed", "R": "Thu", "F": "Fri"}

    def __init__(self):
        """Initialize the Scheduler."""
        self.formatter = Formatter()

    def schedule(
        self, year, start, end, weekdays="MTWRF", exclude=None, **kwargs
    ):
        """Create a schedule.

        Parameters
        ----------
        year : str
            Year in YYYY format
        start : str
            Start date in MM-DD format
        end : str
            End date in MM-DD format
        weekdays : str
            Weekdays in shortcode format (e.g. MWF)
        exclude : list[str]
            Days to exclude in MM-DD format
        kwargs : dict
            Pass through keywords

        Returns
        -------
        str
            The schedule, which counts out weeks and enumerates meeting days
        """
        # Convert abbreviated weekdays to integer values
        weekdays = set(self.weekday_map[day] for day in list(weekdays))
        weekdays = set(self.day_abbr.index(day) for day in weekdays)

        # Define start and end dates, then build out the exclude list
        start = datetime.strptime(f"{year}-{start}", self.format)
        end = datetime.strptime(f"{year}-{end}", self.format)

        if exclude is None:
            exclude = []
        else:
            exclude = [
                datetime.strptime(f"{year}-{date}", self.format)
                for date in exclude
            ]

        # Initialize a week counter, open a buffer for the schedule, and roll
        # through the days
        weeks = 0
        schedule = []
        date = start
        while date <= end:
            # Is the day's weekday a target?
            weekday = date.weekday()
            if weekday not in weekdays:
                date += timedelta(days=1)
                continue

            # If the schedule is empty, count the week and add it to the
            # schedule. If the day's weekday is the earliest in the weekdays,
            # do the same
            if not schedule or weekday == min(weekdays):
                weeks += 1
                week = self.formatter.format([{"num": weeks}], "weeks")
                schedule.append(week)

            # Get the weekday name and format a line for the schedule
            day = calendar.day_name[weekday]
            day = self.formatter.format(
                [{"weekday": day, "month": date.month, "day": date.day}],
                template="days",
            )

            # Is the day an excluded one? If so, mark it
            if date in exclude:
                day += "\n\n**No class**"

            schedule.append(day)
            date += timedelta(days=1)

        return "\n\n".join(schedule)
