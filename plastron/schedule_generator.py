"""A module for generating schedules.

Attributes:
    DAYS (list[str]): a list of the days of the week.
    COLORS (list[str]): a list of the colors to use for the sections.
    RESET (str): the ANSI reset code.
    ANSI_ESCAPE_RE (re.Pattern): a regular expression for matching ANSI escape codes.
    pad_ansi_string (function): a function for padding an ANSI string to a given width.
    generate_time_blocks (function): a function for generating a list of datetime objects for each time block in a given interval.
    get_color_map (function): a function for getting a color map for the sections.
    visualize_schedule (function): a function for visualizing a schedule by printing it to the console.
    ScheduleGenerator (class): a class for generating schedules.
"""

import aiohttp
import argparse
import asyncio
import re

from datetime import datetime, timedelta
from operator import itemgetter
from plastron.astar import optimize_schedule
from plastron.course import Course, Section

DAYS = ["M", "Tu", "W", "Th", "F"]
COLORS = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
    "\033[90m",  # Gray
]
RESET = "\033[0m"
ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def pad_ansi_string(s: str, width: int = 9) -> str:
    """Pad an ANSI string to a given width.

    Args:
        s (str): The string to pad.
        width (int, optional): The width to pad to. Defaults to 9.

    Returns:
        str: The padded string.
    """
    visible_len = len(ANSI_ESCAPE_RE.sub("", s) if s else "")
    return s + " " * (width - visible_len)


def generate_time_blocks(
    start: str = "8:00am", end: str = "6:00pm", interval_minutes: int = 30
) -> list[datetime]:
    """Generate a list of datetime objects for each time block in a given interval.

    Args:
        start (str, optional): The start time. Defaults to "8:00am".
        end (str, optional): The end time. Defaults to "6:00pm".
        interval_minutes (int, optional): The interval between time blocks. Defaults to 30.

    Returns:
        list[datetime]: A list of datetime objects for each time block in the interval.
    """
    t0 = datetime.strptime(start, "%I:%M%p")
    t1 = datetime.strptime(end, "%I:%M%p")
    blocks = []
    while t0 < t1:
        blocks.append(t0)
        t0 += timedelta(minutes=interval_minutes)
    return blocks


def get_color_map(sections: list[Section]) -> dict[str, str]:
    """Get a color map for the sections.

    Args:
        sections (list[Section]): A list of sections.

    Returns:
        dict[str, str]: A dictionary of section IDs and their corresponding colors.
    """
    color_map = {}
    for idx, section in enumerate(sections):
        color_map[section.section_id] = COLORS[idx % len(COLORS)]
    return color_map


def visualize_schedule(
    schedule: dict, time_blocks: list[datetime], grid: dict[datetime, dict[str, str]]
):
    """Visualize a schedule by printing it to the console.

    Args:
        schedule (dict): The schedule to visualize.
        time_blocks (list[datetime]): The time blocks to visualize.
        grid (dict[datetime, dict[str, str]]): The grid to visualize.
    """
    color_map = get_color_map(schedule["sections"])

    for section in schedule["sections"]:
        section_id = section.section_id
        color = color_map[section_id]
        for meeting in section.meetings:
            day = meeting.days
            start = meeting.start_time
            end = meeting.end_time
            for block in time_blocks:
                if start <= block < end and day in grid[block]:
                    grid[block][day] = f"{color}{section_id[4:]}{RESET}"

    print("\nTime    | " + " | ".join(f"{day:9}" for day in DAYS))
    print("-" * (8 + len(DAYS) * 12))

    for block in time_blocks:
        time_str = block.strftime("%I:%M%p")
        row = f"{time_str} | " + " | ".join(
            pad_ansi_string(grid[block][day]) for day in DAYS
        )
        print(row)


class ScheduleGenerator:
    """A class for generating schedules.

    Attributes:
        courses (list[Course]): The courses to generate schedules for.
        schedules (list[dict]): The generated schedules.
        hydrated (bool): Whether the courses have been hydrated.
        time_start (datetime): The time the generator started (for performance tracking).
    """

    def __init__(
        self,
        required_courses: list[str],
    ):
        """Initialize a ScheduleGenerator object.

        Args:
            required_courses (list[str]): List of required course IDs.
        """
        self.courses = [Course(course_id) for course_id in required_courses]
        self.schedules = []
        self.hydrated = False
        self.time_start = datetime.now()

    def hydrate_courses(self) -> None:
        """Hydrate all courses synchronously.

        Raises:
            Exception: If hydrating fails.

        Side effects:
            Sets self.hydrated to True if successful.
            Prints the time it takes to hydrate the courses.
        """
        print("Hydrating courses at", datetime.now() - self.time_start, "seconds")
        for course in self.courses:
            try:
                course.hydrate_sections()
            except Exception as e:
                print(f"Error hydrating course {course.course_id}: {e}")

        self.hydrated = True
        print("Hydrated courses at", datetime.now() - self.time_start, "seconds")

    async def hydrate_courses_async(self) -> None:
        """Hydrate all courses asynchronously.

        Side effects:
            Sets self.hydrated to True if successful.
            Prints the time it takes to hydrate the courses.
        """
        print(
            "Hydrating courses (async) at", datetime.now() - self.time_start, "seconds"
        )
        async with aiohttp.ClientSession() as session:
            tasks = [course.hydrate_sections_async(session) for course in self.courses]
            await asyncio.gather(*tasks)

        self.hydrated = True
        print(
            "Hydrated courses (async) at", datetime.now() - self.time_start, "seconds"
        )

    def generate_schedules(self, top: int = 1) -> list[dict]:
        """Generate schedules.

        Args:
            top (int, optional): The number of schedules to generate. Defaults to 1.

        Returns:
            list[dict]: The generated schedules.
        """
        if not self.hydrated:
            asyncio.run(self.hydrate_courses_async())

        self.schedules = optimize_schedule(self.courses, top)
        print("Generated schedules at", datetime.now() - self.time_start, "seconds")
        return self.schedules

    def visualize_schedules(self) -> None:
        """Visualize the schedules."""
        for schedule in self.schedules:
            # Finds the range of time blocks that will be displayed
            earliest_start = min(
                meeting.start_time
                for section in schedule["sections"]
                for meeting in section.meetings
            )
            latest_end = max(
                meeting.end_time
                for section in schedule["sections"]
                for meeting in section.meetings
            )
            time_blocks = generate_time_blocks(
                start=earliest_start.strftime("%I:%M%p"),
                end=latest_end.strftime("%I:%M%p"),
            )
            grid = {block: {day: "" for day in DAYS} for block in time_blocks}

            visualize_schedule(schedule, time_blocks, grid)
            print(f"Gap minutes: {schedule['total_gap_minutes']}")

            color_map = get_color_map(schedule["sections"])
            for section in schedule["sections"]:
                section_id = section.section_id
                # Wow, this is a lot just to destructure and assign at the same time, why python, why?
                instructors, seats, open_seats = itemgetter(
                    "instructors", "seats", "open_seats"
                )(section.raw_data)
                color = color_map[section_id]
                print(
                    f"{color}{section_id}{RESET} ({open_seats}/{seats}): {section.meetings}{', ' if instructors else ''}{', '.join(instructors)}"
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate class schedules")
    parser.add_argument(
        "courses",
        metavar="COURSE_ID",
        nargs="+",
        help="List of course IDs (e.g. MATH101)",
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=1,
        help="Number of schedules to generate (default: 1)",
    )

    # parser.add_argument(
    #     "-v",
    #     "--verbose",
    #     help="Verbose output",
    # )

    args = parser.parse_args()

    generator = ScheduleGenerator(args.courses)
    generator.generate_schedules(args.num)
    generator.visualize_schedules()
