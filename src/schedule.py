#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import calendar
import tomllib
from datetime import datetime, timedelta
from pathlib import Path

from templates import ScheduleEntry


class Scheduler:
    """Scheduler for compiling and rendering TOML schedules."""

    date_format = "%Y-%m-%d"
    day_abbr = list(calendar.day_abbr)
    weekday_map = {"M": "Mon", "T": "Tue", "W": "Wed", "R": "Thu", "F": "Fri"}

    def _convert_weekdays(self, *weekdays):
        """Convert abbreviated weekdays to integer values.

        Parameters
        ----------
        weekdays : str
            Weekdays to convert

        Returns
        -------
        set[int]
            Integer values of weekdays

        Raises
        ------
        KeyError
            If weekdays aren't MTWRF
        """
        invalid = [day for day in weekdays if day not in self.weekday_map]
        if invalid:
            raise ValueError("Invalid weekdays; select from 'MWTRF'")

        return {self.day_abbr.index(self.weekday_map[day]) for day in weekdays}

    def make_schedule(
        self, year, start, end, weekdays="MTWRF", exclude=None, **kwargs
    ):
        """Create a schedule.

        Parameters
        ----------
        year : str
            Year in YYYY format
        start : str
            State date in MM-DD format
        end : str
            End date in MM-DD format
        weekdays : str
            Weekdays in shortcode format (e.g. MWF)
        exclude : list[str]
            Days to exclude in MM-DD format
        kwargs : dict
            Pass-through keywords

        Returns
        -------
        str
            Schedule formatted as TOML
        """
        weekdays = self._convert_weekdays(*weekdays)

        start = datetime.strptime(f"{year}-{start}", self.date_format)
        end = datetime.strptime(f"{year}-{end}", self.date_format)

        if exclude is None:
            exclude = []
        else:
            exclude = [
                datetime.strptime(f"{year}-{date}", self.date_format)
                for date in exclude
            ]

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
            # schedule. If the day's  weekday is the earliest in the weekdays,
            # do the same
            if not schedule or weekday == min(weekdays):
                weeks += 1
                week_rendered = ScheduleEntry.WEEK.render(num=weeks)
                schedule.append(week_rendered)

            # Get the weekday name, determine whether it's a no-class day, and
            # format a line for the schedule
            day = calendar.day_name[weekday]
            no_class = "true" if date in exclude else "false"
            day_rendered = ScheduleEntry.DAY.render(
                num=weeks,
                month=date.month,
                day=date.day,
                weekday=day,
                no_class=no_class,
            )

            schedule.append(day_rendered)
            date += timedelta(days=1)

        return "\n".join(schedule)


def main(args):
    """Run the script."""
    with args.config.open("rb") as f:
        syllabus = tomllib.load(f)

    scheduler = Scheduler()
    schedule = scheduler.make_schedule(**syllabus["schedule"])
    print(schedule)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a course schedule")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        required=True,
        help="Syllabus config (.toml)",
    )
    args = parser.parse_args()
    main(args)
