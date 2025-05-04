import aiohttp

from bs4 import BeautifulSoup
from datetime import datetime


def is_spring(date: datetime = datetime.now()) -> bool:
    """When it's spring the fall SOC becomes available, and vice versa.

    Args:
        date (datetime, optional): The date to check. Defaults to datetime.now().

    Returns:
        bool: True if the date is in the spring, False otherwise.
    """
    month = date.month
    day = date.day

    return (
        (month > 2 and month < 9)
        or (month == 2 and day >= 21)
        or (month == 9 and day <= 21)
    )


def get_closest_term_id(date: datetime = datetime.now()) -> str:
    """Get the closest term ID for the given date.

    Args:
        date (datetime, optional): The date to check. Defaults to datetime.now().

    Returns:
        str: The term ID for the closest term.
    """
    current_year = date.year

    if is_spring(date):
        return f"{current_year}08"
    else:
        return f"{current_year}01"


async def scrape_course(course_id: str, session: aiohttp.ClientSession):
    """Scrape the given course ID from Testudo SOC.

    Args:
        course_id (str): The course ID to scrape.
        session (aiohttp.ClientSession): The async session to use.

    Returns:
        list[dict]: A list of dictionaries representing the sections of the course.
    """
    async with session.get(
        f"https://app.testudo.umd.edu/soc/search?courseId={course_id}&sectionId=&termId={get_closest_term_id()}&_openSectionsOnly=on&creditCompare=%3E%3D&credits=0.0&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"
    ) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "html.parser")
        first_course = soup.select_one("#courses-page div.course")

        if not first_course:
            return []

        course_info = first_course.select_one(".course-info-container")
        sections = []

    # Scrape each section
    for section_el in course_info.select(".sections-container .section"):
        section_info = section_el.select_one(".section-info-container")
        seats_info = section_info.select_one(".seats-info-group .seats-info")
        class_info = section_el.select_one(".class-days-container")
        number = section_info.select_one(".section-id").get_text(strip=True)

        section = {
            "course": course_id,
            "section_id": f"{course_id}-{number}",
            "number": number,
            "instructors": [
                el.get_text(strip=True)
                for el in section_info.select(
                    ".section-instructors .section-instructor"
                )
            ],
            "seats": seats_info.select_one(".total-seats-count").get_text(strip=True),
            "open_seats": seats_info.select_one(".open-seats-count").get_text(
                strip=True
            ),
            "waitlist": (
                seats_info.select_one(".waitlist-count").get_text(strip=True)
                if seats_info.select_one(".waitlist-count")
                else ""
            ),
            "meetings": [],
        }

        # Scrape each meeting per section
        for row in class_info.select(".row"):
            start_time_str = row.select_one(".class-start-time")
            end_time_str = row.select_one(".class-end-time")
            class_type = row.select_one(".class-type")

            section["meetings"].append(
                {
                    "days": (
                        row.select_one(".section-days").get_text(strip=True)
                        if row.select_one(".section-days")
                        else ""
                    ),
                    "start_time": (
                        start_time_str.get_text(strip=True) if start_time_str else ""
                    ),
                    "end_time": (
                        end_time_str.get_text(strip=True) if end_time_str else ""
                    ),
                    "building": (
                        row.select_one(".building-code").get_text(strip=True)
                        if row.select_one(".building-code")
                        else ""
                    ),
                    "room": (
                        row.select_one(".class-room").get_text(strip=True)
                        if row.select_one(".class-room")
                        else ""
                    ),
                    "classtype": (
                        (
                            class_type.get_text(strip=True)[:3] + "."
                            if len(class_type.get_text(strip=True)) > 3
                            else class_type.get_text(strip=True)
                        )
                        if class_type
                        else ""
                    ),
                }
            )

        sections.append(section)

    # print(json.dumps(sections, indent=4))
    return sections
