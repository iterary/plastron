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
from plastron.section import Section
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
}

DEFAULT_FILTERS = {
    "no_esg": True,
    "no_fc": True,
    "open_seats": True,
    "earliest_start": "7:30am",
    "latest_end": "6:30pm",
    # Not created yet
    "restrict_days": ["Tu"],
    # Not created yet, to leave time open for lunch?
    "restrict_time_range": [("12:00pm", "1:00pm")],
    "avoid_instructors": [],
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
        # self.url = f"https://api.umd.io/v1/courses/{self.course_id}/sections"

        # Merge default with provided
        self.filters = {**DEFAULT_FILTERS, **filters}

    # Unused, previously used to hydrate sections from the umd.io API, but kept for reference
    # def hydrate_sections(self) -> list[Section]:
    #     """Hydrate the sections of the course synchronously. Sets hydrated to True if successful.

    #     Raises:
    #         Exception: If hydration fails.

    #     Returns:
    #         list[Section]: The sections of the course.
    #     """
    #     try:
    #         response = requests.get(self.url)
    #         data = response.json()

    #         if not isinstance(data, list) and "error_code" in data:
    #             raise Exception(data["message"])

    #         self.sections = self.filter_sections(data)
    #         self.hydrated = True
    #     except Exception as e:
    #         print(f"Error hydrating sections for course {self.course_id}: {e}")
    #         raise e
    #     finally:
    #         return self.sections

    # async def hydrate_sections_async(
    #     self, session: aiohttp.ClientSession
    # ) -> list[Section]:
    #     """Hydrate the sections of the course asynchronously. Sets hydrated to True if successful.

    #     Args:
    #         session (aiohttp.ClientSession): The async session to use.

    #     Raises:
    #         Exception: If hydration fails.

    #     Returns:
    #         list[Section]: The sections of the course.
    #     """
    #     try:
    #         # print(f"Hydrating sections for course {self.course_id} at {datetime.now()}")
    #         async with session.get(self.url) as response:
    #             data = await response.json()

    #             if not isinstance(data, list) and "error_code" in data:
    #                 raise Exception(data["message"])

    #             self.sections = self.filter_sections(data)
    #             self.sections.reverse()
    #             self.hydrated = True
    #     except Exception as e:
    #         print(f"Error hydrating sections for course {self.course_id}: {e}")
    #         raise e

    #     # print(f"Hydrated sections for course {self.course_id} at {datetime.now()}")
    #     return self.sections

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

    # TODO: Cache responses from scraping and use them if available
    # Upstash + Redis is a good choice here
    async def get_cached_response(self):
        """Get the cached response for the course.

        Returns:
            dict: The cached response.
        """
        pass

    def filter_sections(self, raw_sections: list[dict]) -> list[Section]:
        """Filter the sections of the course.

        Args:
            raw_sections (list[dict]): The raw sections of the course.

        Returns:
            list[Section]: The sections of the course.
        """
        return [
            Section(self.course_id, section_data)
            for section_data in raw_sections
            if all(
                get_filter_function(filter)(section_data)
                for filter in self.filters.items()
            )
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
