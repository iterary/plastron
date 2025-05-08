"""A module for sections.

Attributes:
    parse_time (function): a function for parsing a time string to a datetime object.
    expand_days (function): a function for expanding day codes like 'MW' to a list of individual days ['M', 'W'].
    Meeting (class): a class for meetings.
    Section (class): a class for sections.
"""

import json
import re

from datetime import datetime


def parse_time(time_str: str) -> datetime:
    """Convert a time string to a datetime object.

    Args:
        time_str (str): Time string like '12:00pm'

    Returns:
        datetime: Datetime object.
    """
    if not time_str:
        return None
    return datetime.strptime(time_str, "%I:%M%p")


def expand_days(days_str: str) -> list[str]:
    """Expand day codes like 'MW' to a list of individual days ['M', 'W'].

    Args:
        days_str (str): Day codes like 'MW'

    Returns:
        list[str]: List of individual days.
    """
    if not days_str:
        return []
    return re.findall("[A-Z][^A-Z]*", days_str)


class Meeting:
    """A meeting of a section.

    Attributes:
        days (list[str]): List of days.
        start_time (datetime): Start time.
        end_time (datetime): End time.
        meeting (dict): Raw meeting data.
    """

    def __init__(
        self, days: list[str], start_time: datetime, end_time: datetime, meeting: dict
    ):
        """Initialize a Meeting object.

        Args:
            days (list[str]): List of days.
            start_time (datetime): Start time.
            end_time (datetime): End time.
            meeting (dict): Raw meeting data.
        """
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.meeting = meeting

    def __repr__(self):
        return f"{self.days} {self.start_time.strftime('%I:%M%p')} - {self.end_time.strftime('%I:%M%p')} {self.meeting['building']}{self.meeting['room']}"


class Section:
    """A section of a course.

    Attributes:
        course_id (str): Course ID.
        section_id (str): Section ID.
        raw_data (dict): Raw data.
        meetings (list): List of Meeting objects.
    """

    def __init__(self, course_id: str, raw_data: dict):
        """Initialize a Section object.

        Args:
            course_id (str): Course ID.
            raw_data (dict): Raw data.
        """
        self.course_id = course_id
        self.section_id = raw_data["section_id"]
        self.raw_data = raw_data
        self.meetings = self.process_meetings(raw_data["meetings"])

    def process_meetings(self, meetings: list[dict]) -> list[Meeting]:
        """Process a list of meetings into a list of Meeting objects.

        Args:
            meetings (list[dict]): List of meetings.

        Returns:
            list[Meeting]: List of Meeting objects.
        """
        meetings_objects = []
        for meeting in meetings:
            days = expand_days(meeting["days"])
            start_time, end_time = parse_time(meeting["start_time"]), parse_time(
                meeting["end_time"]
            )
            for day in days:
                meetings_objects.append(Meeting(day, start_time, end_time, meeting))
        return meetings_objects

    def __repr__(self):
        """Represent a Section object as a stringified JSON.

        Returns:
            str: Stringified JSON representation of the Section object.
        """
        return json.dumps(
            {
                "section_id": self.section_id,
                "meetings": [str(meeting) for meeting in self.meetings],
            },
            indent=2,
        )
