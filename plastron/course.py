import aiohttp
import json
import requests

from datetime import datetime
from plastron.section import Section

EARLY_BIRD = datetime.strptime("7:00am", "%I:%M%p")
SENIORITIS = datetime.strptime("11:00am", "%I:%M%p")

DEFAULT_RESTRICTIONS = [
    lambda section: "ESG" in section["section_id"],
    lambda section: "FC" in section["section_id"],
    lambda section: section["open_seats"] == 0,
    # Restricts sections that have meetings before user wakes up
    lambda section: any(
        meeting["start_time"]
        and datetime.strptime(meeting["start_time"], "%I:%M%p") < EARLY_BIRD
        for meeting in section["meetings"]
    ),
]


class Course:
    def __init__(self, course_id: str, restrictions: list = DEFAULT_RESTRICTIONS):
        self.course_id = course_id
        self.hydrated = False
        self.sections = []
        self.url = f"https://api.umd.io/v1/courses/{self.course_id}/sections"
        self.restrictions = restrictions

    def hydrate_sections(self) -> list:
        try:
            response = requests.get(self.url)
            data = response.json()

            if not isinstance(data, list) and "error_code" in data:
                raise Exception(data["message"])

            self.sections = self.filter_sections(data)
            self.hydrated = True
        except Exception as e:
            print(f"Error hydrating sections for course {self.course_id}: {e}")
            raise e
        finally:
            return self.sections

    async def hydrate_sections_async(self, session: aiohttp.ClientSession) -> list:
        try:
            # print(f"Hydrating sections for course {self.course_id} at {datetime.now()}")
            async with session.get(self.url) as response:
                data = await response.json()

                if not isinstance(data, list) and "error_code" in data:
                    raise Exception(data["message"])

                self.sections = self.filter_sections(data)
                self.sections.reverse()
                self.hydrated = True
        except Exception as e:
            print(f"Error hydrating sections for course {self.course_id}: {e}")
            raise e

        # print(f"Hydrated sections for course {self.course_id} at {datetime.now()}")
        return self.sections

    # TODO: Scrape sections instead of using umd.io
    # This is because umd.io seems to have an internal queue/throttling that blocks us from requesting multiple courses at once
    # Even though we're doing it in parallel :(
    async def scrape_sections(self):
        pass

    def filter_sections(self, raw_sections) -> list:
        return [
            Section(self.course_id, section_data)
            for section_data in raw_sections
            if not any(restriction(section_data) for restriction in self.restrictions)
        ]

    def __repr__(self):
        return json.dumps(
            {
                "course_id": self.course_id,
                "sections": [json.loads(str(section)) for section in self.sections],
            },
            indent=2,
        )
