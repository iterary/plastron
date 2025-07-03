"""A module for courses.

Attributes:
    FILTER_FUNCTIONS (dict[str, Callable]): a dictionary of filter functions.
    DEFAULT_FILTERS (list[str | tuple]): the default filters that sections must pass to be included.
    Course (class): a class for courses.
"""

import aiohttp
import json

# import requests

from datetime import datetime
from plastron.section import Section, expand_days
from plastron.scraper import scrape_course
from typing import Any, Callable

# TODO: Add more filters and filter functions
FILTER_FUNCTIONS = {
    "no_esg": lambda active: lambda section: (
        "ESG" not in section["section_id"] if active else True
    ),
    "no_fc": lambda active: lambda section: (
        "FC" not in section["section_id"] if active else True
    ),
    "open_seats": lambda active: lambda section: (
        section["open_seats"] != "0" if active else True
    ),
    "earliest_start": lambda time: lambda section: all(
        not meeting["start_time"]
        or datetime.strptime(meeting["start_time"], "%I:%M%p")
        >= datetime.strptime(time, "%I:%M%p")
        for meeting in section["meetings"]
    ),
    "latest_end": lambda time: lambda section: all(
        not meeting["end_time"]
        or datetime.strptime(meeting["end_time"], "%I:%M%p")
        <= datetime.strptime(time, "%I:%M%p")
        for meeting in section["meetings"]
    ),
    "avoid_instructors": lambda instructors: lambda section: all(
        instructor not in section["instructors"] for instructor in instructors
    ),
    "max_waitlist": lambda limit: lambda section: int(section["waitlist"]) <= limit,
    "restrict_days": lambda days: lambda section: not any(
        any(day in days for day in expand_days(meeting["days"]))
        for meeting in section["meetings"]
    ),
}

DEFAULT_FILTERS = {
    "no_esg": True,
    "no_fc": True,
    "open_seats": True,
    "earliest_start": "7:30am",
    "latest_end": "6:30pm",
    "avoid_instructors": [],
    "max_waitlist": 9999,
    "restrict_days": [],
    # # Not created yet, to leave time open for lunch?
    # "restrict_time_range": [("12:00pm", "1:00pm")],
}

READABLE_FILTERS = {
    "no_esg": "no ESG sections",
    "no_fc": "no FC sections",
    "open_seats": "open seats",
    "earliest_start": "earliest start",
    "latest_end": "latest end",
    "avoid_instructors": "instructor preferences",
    "max_waitlist": "max waitlist",
    "restrict_days": "restricted days",
}


def get_filter_function(key: tuple[str, Any]) -> Callable:
    """Leverage closures to return a function that can be used as a filter

    Args:
        key (tuple[str, Any]): The key to get the filter function equivalent to (filter_name, filter_args).

    Returns:
        function: The filter function.
    """
    # If the filter function is not in the FILTER_FUNCTIONS dictionary, return a closure that always evaluates to True
    if key[0] not in FILTER_FUNCTIONS:
        return lambda _: True

    return FILTER_FUNCTIONS[key[0]](key[1])


class Course:
    """A course with sections.

    Attributes:
        course_id (str): The course ID.
        hydrated (bool): Whether the course has been hydrated (i.e. sections have been fetched).
        sections (list[Section]): The sections of the course.
        filters (dict[str, Any]): The filters that sections must pass to be included.
    """

    def __init__(self, course_id: str, filters: dict[str, Any] = {}):
        """Initialize a Course object.

        Args:
            course_id (str): The course ID.
            filters (dict[str, Any]): The filters that sections must pass to be included.
        """
        self.course_id = course_id.upper()
        self.hydrated = False
        self.sections = []

        # Merge default with provided
        self.filters = {**DEFAULT_FILTERS, **filters}

    async def scrape_sections(self, session: aiohttp.ClientSession):
        """Hydrate the sections of the course by scraping Testudo SOC website. Sets hydrated to True if successful.

        Args:
            session (aiohttp.ClientSession): The async session to use.

        Raises:
            Exception: If scraping fails.
        """
        try:
            sections = await scrape_course(self.course_id, session)

            self.sections = self.filter_sections(sections)

            # Reversing sections, on average, favors courses that are later in the day
            self.sections.reverse()
            self.hydrated = True
        except Exception as e:
            print(f"Error scraping sections for course {self.course_id}: {e}")
            raise e

    def filter_sections(self, raw_sections: list[dict]) -> list[Section]:
        """Filter the sections of the course.

        Args:
            raw_sections (list[dict]): The raw sections of the course.

        Returns:
            list[Section]: The sections of the course.
        """
        if not raw_sections:
            raise Exception(
                f"No sections exist for {self.course_id}. Please make sure this course is being offered."
            )

        filtered_sections = [
            section_data
            for section_data in raw_sections
            if all(
                get_filter_function(filter)(section_data)
                for filter in self.filters.items()
            )
        ]

        if not filtered_sections:
            # Check which filters are eliminating all sections
            failing_filters = []
            for filter_name, filter_value in self.filters.items():
                if not any(
                    get_filter_function((filter_name, filter_value))(section_data)
                    for section_data in raw_sections
                ):
                    failing_filters.append(
                        (READABLE_FILTERS[filter_name], filter_value)
                    )

            if failing_filters:
                raise Exception(
                    f"Could not find any sections of {self.course_id} with {', '.join(str(filter) for filter in failing_filters)}.\n"
                    "Consider relaxing these filters."
                )
            else:
                filter_stats = []
                total_sections = len(raw_sections)

                for filter_name, filter_value in self.filters.items():
                    sections_passing = sum(
                        1
                        for section_data in raw_sections
                        if get_filter_function((filter_name, filter_value))(
                            section_data
                        )
                    )
                    sections_eliminated = total_sections - sections_passing
                    filter_stats.append(
                        (
                            READABLE_FILTERS[filter_name],
                            sections_eliminated,
                            sections_passing,
                        )
                    )

                # Sort by most restrictive (eliminates most sections)
                filter_stats.sort(key=lambda x: x[1], reverse=True)

                # Create a helpful message
                restrictive_filters = [
                    f"{name} (eliminates {eliminated}/{total_sections})"
                    for name, eliminated, passing in filter_stats[
                        :3
                    ]  # Show top 3 most restrictive
                    if eliminated > 0
                ]

                if restrictive_filters:
                    raise Exception(
                        f"Could not find any sections for {self.course_id} that satisfy all filters simultaneously.\n"
                        f"Most restrictive filters: {', '.join(restrictive_filters)}.\n"
                        f"Consider relaxing these filters."
                    )
                else:
                    raise Exception(
                        f"Could not find any sections for {self.course_id} that satisfy all filters simultaneously.\n"
                        f"Consider relaxing some filters."
                    )

        return [
            Section(self.course_id, section_data) for section_data in filtered_sections
        ]

    def __repr__(self):
        """Represent a Course object as a stringified JSON.

        Returns:
            str: Stringified JSON representation of the Course object.
        """
        return json.dumps(
            {
                "course_id": self.course_id,
                "sections": [json.loads(str(section)) for section in self.sections],
            },
            indent=2,
        )

    # TODO: Cache responses from scraping and use them if available
    # Upstash + Redis is a good choice here
    async def get_cached_response(self):
        """Get the cached response for the course.

        Returns:
            dict: The cached response.
        """
        pass
