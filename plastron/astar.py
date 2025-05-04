"""A module for the A* algorithm (but not really bc no heuristic).

Attributes:
    adjusted_gap (function): a function for adjusting the gap cost based on a bell curve.
    calculate_weight (function): a function for calculating the weight of a schedule.
    optimize_schedule (function): a function for optimizing a schedule.
"""

import heapq
import math

from collections import defaultdict
from itertools import count
from typing import Any

from plastron.course import Course, Section

DAY_WEIGHT = 15


def adjusted_gap(
    gap: float,
    penalty_multiplier: float = 30,
    penalty_midpoint: float = 50,
    penalty_range: float = 15,
) -> float:
    """
    Adjusts the gap cost to penalize less usable gaps (e.g. 45 minute gap might be too short to do anything between classes, but still a long time to wait)

    Args:
        gap (float): The gap in minutes.
        penalty_multiplier (float, optional): The multiplier for the penalty. Defaults to 30.
        penalty_midpoint (float, optional): The midpoint of the penalty, where the penalty is at its maximum. Defaults to 50.
        penalty_range (float, optional): The range of the penalty. Defaults to 15.

    Returns:
        float: The adjusted gap cost.
    """
    cost = gap

    penalty = penalty_multiplier * math.exp(
        -((gap - penalty_midpoint) ** 2) / (2 * penalty_range**2)
    )

    return cost + penalty


# Does an insert, sort, and then a full scan
# Slightly slower than binary search insertion, but more readable
def calculate_weight(
    path: list[Section], new_section: Section, gap_exponent: float = 0.75
) -> tuple[float, dict]:
    """Estimate the total weight after inserting new_section into an existing path.

    Args:
        path (list[Section]): List of sections already in the schedule.
        new_section (Section): Section to be added.
        gap_exponent (float, optional): The exponent for the gap cost. Defaults to 0.75.

    Returns:
        tuple[float, dict]: Total weight, and stats.
    """
    day_meetings = defaultdict(list)

    for section in path:
        for meeting in section.meetings:
            day_meetings[meeting.days].append((meeting.start_time, meeting.end_time))

    for meeting in new_section.meetings:
        day_meetings[meeting.days].append((meeting.start_time, meeting.end_time))

    cost = 0
    total_gap = 0
    num_days_with_meetings = 0

    for day in day_meetings:
        day_meetings[day].sort()

        if len(day_meetings[day]) > 0:
            num_days_with_meetings += 1

        for i in range(len(day_meetings[day]) - 1):
            new_gap = 0
            start, end = day_meetings[day][i]
            next_start, next_end = day_meetings[day][i + 1]

            if end > next_start:
                return (float("inf"), 1)

            new_gap = (next_start - end).total_seconds() / 60

            if new_gap > 0:
                total_gap += new_gap
                # Exponentiation is used to make the cost function more/less sensitive to large gaps
                cost += adjusted_gap(new_gap) ** gap_exponent

    cost += num_days_with_meetings * DAY_WEIGHT

    return (
        cost,
        {
            "total_gap": total_gap,
            "num_days_with_meetings": num_days_with_meetings,
        },
    )


def optimize_schedule(
    courses: list[Course], top: int = 1, gap_exponent: float = 0.75
) -> list:
    """Uniform cost search for the top k optimal schedules.

    Args:
        courses (list[Course]): List of courses with sections and meetings.
        top (int, optional): How many schedules to return. Defaults to 3.

    Returns:
        list[dict]: List of top k optimal schedules.
    """

    # Tiebreakers for heapq
    counter = count()
    result_counter = count()

    start_state = (
        0,
        next(counter),
        [],
        0,
        {},
    )  # (cost, counter, path, course_index, stats)
    queue = [start_state]

    results = []
    visited = set()
    best_complete_cost = float("inf")

    if len(courses) == 0:
        return []

    # While we still have stuff to explore
    while queue:
        # Python's heapq implementation is pretty helpful, we can mooch off of it
        cost, _, path, course_idx, stats = heapq.heappop(queue)

        # If we've completed the current path
        if course_idx == len(courses):
            best_complete_cost = min(best_complete_cost, cost)

            result = {
                "cost": cost,
                "total_gap_minutes": stats["total_gap"],
                "num_days_with_meetings": stats["num_days_with_meetings"],
                "sections": path,
            }

            heapq.heappush(results, (cost, next(result_counter), result))

            continue

        # Generate next states by choosing sections from the next course
        for section in courses[course_idx].sections:
            new_path = path + [section]

            cost, stats = calculate_weight(path, section, gap_exponent)

            if cost == float("inf") or cost > best_complete_cost + 60:
                continue  # Prune conflicts or paths that are worse than the best complete schedule

            new_state = (
                cost,
                next(counter),
                new_path,
                course_idx + 1,
                stats,
            )
            state_id = (course_idx + 1, tuple(s.section_id for s in new_path))

            if state_id not in visited:
                visited.add(state_id)
                heapq.heappush(queue, new_state)

    # print(len(results))
    return [result for _, _, result in heapq.nsmallest(top, results)]
