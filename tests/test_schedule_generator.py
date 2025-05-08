"""Tests for the schedule generator."""

from datetime import datetime
from plastron.schedule_generator import (
    ScheduleGenerator,
    str2bool,
    generate_time_blocks,
    visualize_schedule,
    get_color_map,
    pad_ansi_string,
)
from plastron.section import Section


def test_str2bool():
    """Test that the str2bool method converts strings to booleans correctly."""
    assert str2bool("true") == True
    assert str2bool("false") == False
    assert str2bool("True") == True
    assert str2bool("False") == False
    assert str2bool("1") == True
    assert str2bool("0") == False
    assert str2bool("yes") == True
    assert str2bool("no") == False
    assert str2bool("Y") == True
    assert str2bool("N") == False
    assert str2bool("y") == True
    assert str2bool("n") == False
    assert str2bool("t") == True
    assert str2bool("f") == False
    assert str2bool("T") == True
    assert str2bool("F") == False


def test_no_courses():
    """Test that the no courses case returns an empty list."""
    schedule_generator = ScheduleGenerator()
    assert schedule_generator.generate_schedules() == []


def test_generate_time_blocks():
    """Test that the generate_time_blocks method returns the correct list of datetime objects."""
    time_blocks = generate_time_blocks(
        start="10:00am", end="12:00pm", interval_minutes=30
    )
    assert len(time_blocks) == 4
    assert time_blocks[0] == datetime(1900, 1, 1, 10, 0)
    assert time_blocks[3] == datetime(1900, 1, 1, 11, 30)


def test_get_color_map():
    """Test that the get_color_map method returns a correct color map for a given list of sections."""
    sections = [
        Section("Mock1", {"section_id": "Mock1", "meetings": []}),
        Section("Mock2", {"section_id": "Mock2", "meetings": []}),
    ]
    color_map = get_color_map(sections)
    assert len(color_map) == 2
    assert color_map["Mock1"] == "\033[91m"
    assert color_map["Mock2"] == "\033[92m"


def test_pad_ansi_string():
    """Test that the pad_ansi_string method pads an ANSI string to a given width."""
    assert pad_ansi_string("Hello", 10) == "Hello     "
    # ANSI escape codes should not be counted towards the width
    assert pad_ansi_string("Hello\033[91m", 10) == "Hello\033[91m     "


def test_visualize_schedule():
    """Test that the visualize_schedule method resolves properly without raising an error."""
    schedule = {
        "cost": 0,
        "total_gap_minutes": 0,
        "num_days_with_meetings": 0,
        "sections": [],
    }
    time_blocks = generate_time_blocks(
        start="10:00am", end="12:00pm", interval_minutes=30
    )
    grid = {
        block: {day: "" for day in ["M", "Tu", "W", "Th", "F"]} for block in time_blocks
    }
    visualize_schedule(schedule, time_blocks, grid)
    assert True


# Rest covered in test_api.py
