"""Tests for the Course class."""

from datetime import datetime
from plastron.course import Course, get_filter_function
from plastron.section import Section, expand_days, parse_time

RAW_SECTIONS = [
    {
        "course": "INST314",
        "section_id": "INST314-0101",
        "semester": "202508",
        "number": "0101",
        "seats": "44",
        "meetings": [
            {
                "days": "MW",
                "room": "0226",
                "building": "HJP",
                "classtype": "",
                "start_time": "11:00am",
                "end_time": "11:50am",
            },
            {
                "days": "F",
                "room": "0103",
                "building": "HBK",
                "classtype": "Discussion",
                "start_time": "8:00am",
                "end_time": "8:50am",
            },
        ],
        "open_seats": "37",
        "waitlist": "0",
        "instructors": ["Samantha Kemper"],
    },
    {
        "course": "INST314",
        "section_id": "INST314-0102",
        "semester": "202508",
        "number": "0102",
        "seats": "44",
        "meetings": [
            {
                "days": "MW",
                "room": "0226",
                "building": "HJP",
                "classtype": "",
                "start_time": "11:00am",
                "end_time": "11:50am",
            },
            {
                "days": "F",
                "room": "0103",
                "building": "HBK",
                "classtype": "Discussion",
                "start_time": "9:00am",
                "end_time": "9:50am",
            },
        ],
        "open_seats": "20",
        "waitlist": "0",
        "instructors": ["Samantha Kemper"],
    },
    {
        "course": "INST314",
        "section_id": "INST314-0103",
        "semester": "202508",
        "number": "0103",
        "seats": "44",
        "meetings": [
            {
                "days": "MW",
                "room": "0226",
                "building": "HJP",
                "classtype": "",
                "start_time": "11:00am",
                "end_time": "11:50am",
            },
            {
                "days": "F",
                "room": "0103",
                "building": "HBK",
                "classtype": "Discussion",
                "start_time": "10:00am",
                "end_time": "10:50am",
            },
        ],
        "open_seats": "0",
        "waitlist": "2",
        "instructors": ["Samantha Kemper"],
    },
    {
        "course": "INST314",
        "section_id": "INST314-0104",
        "semester": "202508",
        "number": "0104",
        "seats": "44",
        "meetings": [
            {
                "days": "MW",
                "room": "0226",
                "building": "HJP",
                "classtype": "",
                "start_time": "11:00am",
                "end_time": "11:50am",
            },
            {
                "days": "F",
                "room": "0103",
                "building": "HBK",
                "classtype": "Discussion",
                "start_time": "11:00am",
                "end_time": "11:50am",
            },
        ],
        "open_seats": "0",
        "waitlist": "4",
        "instructors": ["Samantha Kemper"],
    },
    {
        "course": "INST314",
        "section_id": "INST314-0201",
        "semester": "202508",
        "number": "0201",
        "seats": "44",
        "meetings": [
            {
                "days": "MW",
                "room": "0200",
                "building": "SKN",
                "classtype": "",
                "start_time": "2:00pm",
                "end_time": "2:50pm",
            },
            {
                "days": "Th",
                "room": "0103",
                "building": "HBK",
                "classtype": "Discussion",
                "start_time": "2:00pm",
                "end_time": "2:50pm",
            },
        ],
        "open_seats": "0",
        "waitlist": "1",
        "instructors": ["Samantha Kemper"],
    },
    {
        "course": "INST314",
        "section_id": "INST314-0202",
        "semester": "202508",
        "number": "0202",
        "seats": "44",
        "meetings": [
            {
                "days": "MW",
                "room": "0200",
                "building": "SKN",
                "classtype": "",
                "start_time": "2:00pm",
                "end_time": "2:50pm",
            },
            {
                "days": "Th",
                "room": "0103",
                "building": "HBK",
                "classtype": "Discussion",
                "start_time": "3:00pm",
                "end_time": "3:50pm",
            },
        ],
        "open_seats": "0",
        "waitlist": "0",
        "instructors": ["Samantha Kemper"],
    },
    {
        "course": "INST314",
        "section_id": "INST314-0203",
        "semester": "202508",
        "number": "0203",
        "seats": "44",
        "meetings": [
            {
                "days": "MW",
                "room": "0200",
                "building": "SKN",
                "classtype": "",
                "start_time": "2:00pm",
                "end_time": "2:50pm",
            },
            {
                "days": "Th",
                "room": "0103",
                "building": "HBK",
                "classtype": "Discussion",
                "start_time": "4:00pm",
                "end_time": "4:50pm",
            },
        ],
        "open_seats": "19",
        "waitlist": "0",
        "instructors": ["Samantha Kemper"],
    },
    {
        "course": "INST314",
        "section_id": "INST314-0204",
        "semester": "202508",
        "number": "0204",
        "seats": "44",
        "meetings": [
            {
                "days": "MW",
                "room": "0200",
                "building": "SKN",
                "classtype": "",
                "start_time": "2:00pm",
                "end_time": "2:50pm",
            },
            {
                "days": "Th",
                "room": "0103",
                "building": "HBK",
                "classtype": "Discussion",
                "start_time": "5:00pm",
                "end_time": "5:50pm",
            },
        ],
        "open_seats": "37",
        "waitlist": "0",
        "instructors": ["Samantha Kemper"],
    },
    {
        "course": "INST314",
        "section_id": "INST314-ESG1",
        "semester": "202508",
        "number": "ESG1",
        "seats": "60",
        "meetings": [
            {
                "days": "Tu",
                "room": "5332",
                "building": "BLD4",
                "classtype": "",
                "start_time": "9:00am",
                "end_time": "10:30am",
            },
            {
                "days": "",
                "room": "ONLINE",
                "building": "",
                "classtype": "",
                "start_time": "",
                "end_time": "",
            },
        ],
        "open_seats": "54",
        "waitlist": "0",
        "instructors": ["Faisal Quader"],
    },
]


def test_nonexistent_filter_function():
    """Test that a nonexistent filter function always passes the section."""
    filter_function = get_filter_function(("nonexistent", True))
    assert filter_function(RAW_SECTIONS[0]) == True


def test_get_filter_function():
    """Test that the get_filter_function function returns the correct filter function."""
    filter_function = get_filter_function(("no_esg", True))
    assert filter_function(RAW_SECTIONS[8]) == False


def test_filter_sections():
    """Test that the filter_sections method reduces the number of sections to 1."""
    course = Course(
        "ANSC101",
        {
            "no_esg": True,
            "no_fc": True,
            "open_seats": True,
            "earliest_start": "9:00am",
            "latest_end": "2:00pm",
        },
    )
    course.sections = course.filter_sections(RAW_SECTIONS)
    assert len(course.sections) == 1
    assert course.sections[0].section_id == "INST314-0102"


def test_expand_days():
    """Test that the expand_days method returns the correct list of days."""
    assert expand_days("MW") == ["M", "W"]
    assert expand_days("M") == ["M"]
    assert expand_days("TTh") == ["T", "Th"]
    assert expand_days("") == []


def test_parse_time():
    """Test that the parse_time method returns the correct time."""
    assert parse_time("11:00am") == datetime(1900, 1, 1, 11, 0)
    assert parse_time("11:00pm") == datetime(1900, 1, 1, 23, 0)
    assert parse_time("") is None


def test_section_init():
    """Test that the section init method properly constructs a section object and that it can be represented as a string."""
    section = Section("INST314", RAW_SECTIONS[0])
    assert section.section_id == "INST314-0101"
    assert section.course_id == "INST314"
    assert section.raw_data == RAW_SECTIONS[0]
    assert (
        str(section)
        == """{
  "section_id": "INST314-0101",
  "meetings": [
    "M 11:00AM - 11:50AM HJP0226",
    "W 11:00AM - 11:50AM HJP0226",
    "F 08:00AM - 08:50AM HBK0103"
  ]
}"""
    )


def test_course_init():
    """Test that the course init method properly constructs a course object and that it can be represented as a string."""
    course = Course("INST314")
    assert course.course_id == "INST314"
    assert (
        str(course)
        == """{
  "course_id": "INST314",
  "sections": []
}"""
    )
