from datetime import datetime
from plastron.schedule_generator import (
    ScheduleGenerator,
    str2bool,
    generate_time_blocks,
    visualize_schedule,
)


def test_str2bool():
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


def test_visualize_schedule():
    """Test that the visualize_schedule method resolves properly."""
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
