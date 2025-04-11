import heapq

from bisect import bisect_right
from collections import defaultdict
from itertools import count

from plastron.section import Section


def calculate_weight(path: list, new_section: Section) -> float:
    """Estimate the gap cost of inserting new_section into an existing path.

    Compares only closest meetings in time per overlapping day.

    Args:
        path (list): List of sections already in the schedule.
        new_section (Section): Section to be added.

    Returns:
        float: Estimated added cost in minutes^2, or inf if overlap.
    """
    # Build a per-day timeline of meetings from the existing path
    day_meetings = defaultdict(list)

    for section in path:
        for meeting in section.meetings:
            day_meetings[meeting.days].append((meeting.start_time, meeting.end_time))

    # Sort the timelines so we can binary search by start time
    for day in day_meetings:
        day_meetings[day].sort()  # sorted by start_time

    total_gap = 0

    for meeting in new_section.meetings:
        day = meeting.days
        new_start = meeting.start_time
        new_end = meeting.end_time

        if day not in day_meetings:
            continue  # No overlap on this day, so no gap penalty needed

        day_schedule = day_meetings[day]

        # Binary search to find where new_start would be inserted
        idx = bisect_right(day_schedule, (new_start, new_end))

        # Check previous and next neighbor only
        neighbors = []
        if idx > 0:
            neighbors.append(day_schedule[idx - 1])
        if idx < len(day_schedule):
            neighbors.append(day_schedule[idx])

        for exist_start, exist_end in neighbors:
            # Check for overlap
            if (exist_start <= new_start < exist_end) or (
                new_start <= exist_start < new_end
            ):
                return float("inf")

            # Compute positive gap
            if new_end <= exist_start:
                gap = (exist_start - new_end).total_seconds() / 60
            elif exist_end <= new_start:
                gap = (new_start - exist_end).total_seconds() / 60
            else:
                gap = 0

            if gap > 0:
                total_gap += gap

    return total_gap


def optimize_schedule(courses: list, top: int = 1) -> list:
    """Uniform cost search for the top k optimal schedules.

    Args:
        courses_data (list): List of courses with sections and meetings.
        top (int, optional): How many schedules to return. Defaults to 3.

    Returns:
        List of top k optimal schedules.
    """
    counter = count()
    start_state = (0, next(counter), [], 0)  # (cost, counter, path, course_index)
    queue = [start_state]

    results = []
    visited = set()

    # While we still have stuff to explore AND we haven't found the top k results
    while queue and len(results) < top:
        # Python's heapq implementation is pretty helpful, we can mooch off of it
        cost, _, path, course_idx = heapq.heappop(queue)

        # If we've reached the end (selected a section for each course)
        if course_idx == len(courses):
            results.append(
                {
                    "total_gap_minutes": cost,
                    "sections": path,
                }
            )
            continue

        # Generate next states by choosing sections from the next course
        for section in courses[course_idx].sections:
            new_path = path + [section]

            gap = calculate_weight(path, section)

            if gap == float("inf"):
                continue  # Skip invalid combinations

            new_cost = cost + gap
            new_state = (new_cost, next(counter), new_path, course_idx + 1)
            state_id = (course_idx + 1, tuple(s.section_id for s in new_path))

            if state_id not in visited:
                visited.add(state_id)
                heapq.heappush(queue, new_state)

    return results
