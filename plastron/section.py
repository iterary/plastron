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


def expand_days(days_str: str) -> list:
    """Expand day codes like 'MW' to a list of individual days ['M', 'W'].

    Args:
        days_str (str): Day codes like 'MW'

    Returns:
        list: List of individual days.
    """
    if not days_str:
        return []
    return re.findall("[A-Z][^A-Z]*", days_str)


def process_meetings(meetings: list) -> list:
    meetings_objects = []
    for meeting in meetings:
        days = expand_days(meeting["days"])
        start_time, end_time = parse_time(meeting["start_time"]), parse_time(
            meeting["end_time"]
        )
        for day in days:
            meetings_objects.append(Meeting(day, start_time, end_time, meeting))
    return meetings_objects


class Meeting:
    def __init__(
        self, days: list, start_time: datetime, end_time: datetime, meeting: dict
    ):
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.meeting = meeting

    def __repr__(self):
        return f"{self.days} {self.start_time.strftime('%I:%M%p')} - {self.end_time.strftime('%I:%M%p')} {self.meeting['building']}{self.meeting['room']}"
        # return json.dumps(
        #     {
        #         "days": self.days,
        #         "start_time": self.start_time.strftime("%I:%M%p"),
        #         "end_time": self.end_time.strftime("%I:%M%p"),
        #     },
        #     indent=2,
        # )


class Section:
    def __init__(self, course_id: str, raw_data: dict):
        self.course_id = course_id
        self.section_id = raw_data["section_id"]
        self.raw_data = raw_data
        self.meetings = process_meetings(raw_data["meetings"])

    def __repr__(self):
        return json.dumps(
            {
                "section_id": self.section_id,
                "meetings": [json.loads(str(meeting)) for meeting in self.meetings],
            },
            indent=2,
        )
