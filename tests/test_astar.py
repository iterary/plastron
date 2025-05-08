"""Tests for the search algorithm."""

from plastron.astar import adjusted_gap, calculate_weight, optimize_schedule
from plastron.course import Course
from plastron.section import Section

MOCK_SECTION_1 = Section(
    "Course1-10AM",
    {
        "course": "MockCourse1",
        "section_id": "MockCourse1-10AM",
        "semester": "202508",
        "number": "10AM",
        "seats": "39",
        "meetings": [
            {
                "days": "M",
                "room": "0109",
                "building": "HBK",
                "classtype": "",
                "start_time": "10:00am",
                "end_time": "10:50am",
            },
        ],
        "open_seats": "10",
        "waitlist": "0",
        "instructors": ["John Smith"],
    },
)

MOCK_SECTION_2 = Section(
    "Course1-2PM",
    {
        "course": "MockCourse1",
        "section_id": "MockCourse1-2PM",
        "semester": "202508",
        "number": "2PM",
        "seats": "39",
        "meetings": [
            {
                "days": "M",
                "room": "0109",
                "building": "HBK",
                "classtype": "",
                "start_time": "2:00pm",
                "end_time": "2:50pm",
            },
        ],
        "open_seats": "10",
        "waitlist": "0",
        "instructors": ["Jane Doe"],
    },
)

MOCK_SECTION_3 = Section(
    "Course2-11AM",
    {
        "course": "MockCourse2",
        "section_id": "MockCourse2-11AM",
        "semester": "202508",
        "number": "11AM",
        "seats": "39",
        "meetings": [
            {
                "days": "M",
                "room": "0109",
                "building": "HBK",
                "classtype": "",
                "start_time": "11:00am",
                "end_time": "11:50am",
            },
        ],
        "open_seats": "10",
        "waitlist": "0",
        "instructors": ["Jane Doe"],
    },
)

MOCK_SECTION_4 = Section(
    "Course2-4PM",
    {
        "course": "MockCourse2",
        "section_id": "MockCourse2-4PM",
        "semester": "202508",
        "number": "4PM",
        "seats": "39",
        "meetings": [
            {
                "days": "M",
                "room": "0109",
                "building": "HBK",
                "classtype": "",
                "start_time": "4:00pm",
                "end_time": "4:50pm",
            },
        ],
        "open_seats": "10",
        "waitlist": "0",
        "instructors": ["John Smith"],
    },
)


def test_adjusted_gap():
    """Test that the adjusted gap is calculated correctly."""
    gap = 45
    # Within 0.1 of the expected value, to account for floating point imprecision
    assert abs(adjusted_gap(gap, 30, 50, 15) - 73.37) < 0.1


def test_calculate_weight():
    """Test that a schedule weight is calculated correctly."""
    path = [MOCK_SECTION_1]
    new_section = MOCK_SECTION_3
    weight, stats = calculate_weight(path, new_section)
    assert stats["total_gap"] == 10
    assert stats["num_days_with_meetings"] == 1


def test_optimize_schedule():
    """Test that a schedule is optimized correctly."""
    course1 = Course("MockCourse1")
    course2 = Course("MockCourse2")
    course1.sections = [MOCK_SECTION_1, MOCK_SECTION_2]
    course2.sections = [MOCK_SECTION_3, MOCK_SECTION_4]
    courses = [course1, course2]
    optimized_schedules = optimize_schedule(courses, 2)

    assert len(optimized_schedules) == 2
    assert optimized_schedules[0]["sections"][0].section_id == "MockCourse1-10AM"
    assert optimized_schedules[0]["sections"][1].section_id == "MockCourse2-11AM"


def test_optimize_schedule_with_conflict():
    """Test that schedules with conflicting sections are not returned."""
    course1 = Course("MockCourse1")
    course1.sections = [MOCK_SECTION_1]
    course2 = Course("MockCourse2")
    course2.sections = [MOCK_SECTION_1]
    courses = [course1, course2]
    optimized_schedules = optimize_schedule(courses)
    assert len(optimized_schedules) == 0


def test_optimize_empty_schedule():
    """Test that an empty schedule is returned if no courses are provided."""
    courses = []
    optimized_schedules = optimize_schedule(courses)
    assert len(optimized_schedules) == 0
