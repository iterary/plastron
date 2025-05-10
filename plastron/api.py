"""A module for the Plastron API.

Attributes:
    app_start_time (float): The start time of the API.
    app (fastapi.FastAPI): The FastAPI app.
    ScheduleFilters (pydantic.BaseModel): A model for the filters that can be applied to the schedule generation.
    ScheduleRequest (pydantic.BaseModel): A model for the request to the schedule generation.
    visualize_schedules (function): A function for visualizing schedules, served at /schedules/visualized.
    generate_schedules (function): A function for generating schedules, served at /schedules.
    read_root (function): A function for the root endpoint, served at /.
    health (function): A function for the health endpoint, served at /health.
"""

import io
import platform
import psutil
import re
import sys
import time
import uvicorn

from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse
from plastron.schedule_generator import ScheduleGenerator
from pydantic import BaseModel, Field
from typing import List, Optional

app_start_time = time.time()
app = FastAPI(
    title="Plastron API",
    description="A teensy-weensy microservice that generates optimal schedules for UMD classes.",
    version="0.1.0",
)


class ScheduleFilters(BaseModel):
    """A model for the filters that can be applied to the schedule generation.

    Args:
        BaseModel (pydantic.BaseModel): The base model for the filters.
    """

    no_esg: Optional[bool] = True
    no_fc: Optional[bool] = True
    open_seats: Optional[bool] = False
    earliest_start: Optional[str] = "8:00am"
    latest_end: Optional[str] = "5:00pm"


class ScheduleRequest(BaseModel):
    """A model for the request to the schedule generation.

    Args:
        BaseModel (pydantic.BaseModel): The base model for the request.
    """

    courses: List[str] = Field(
        ..., json_schema_extra={"example": ["ANSC101", "ANSC103"]}
    )
    top: Optional[int] = Field(1, json_schema_extra={"example": 1})
    filters: Optional[ScheduleFilters] = Field(default_factory=ScheduleFilters)


@app.post("/schedules/visualized")
async def visualize_schedules(
    data: ScheduleRequest,
    colored: bool = Query(
        False, description="Whether to color the schedules. Only applies in terminal."
    ),
) -> str:
    """Generate and visualize schedules.

    Args:
        data (ScheduleRequest): The request data.
        colored (bool): Whether to color the schedules. Only applies in terminal.

    Returns:
        str: The visualized schedules.
    """
    # Enforce max of 10 courses
    if len(data.courses) > 10:
        raise HTTPException(status_code=422, detail="Maximum of 10 courses allowed.")

    schedule_generator = ScheduleGenerator(data.courses, data.filters.model_dump())

    await schedule_generator.hydrate_courses_async()
    schedule_generator.generate_schedules(data.top)

    # Capture the output of the visualize_schedules method
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer

    schedule_generator.visualize_schedules()

    sys.stdout = sys_stdout

    printed_output = buffer.getvalue()
    return PlainTextResponse(
        re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", printed_output)
        if not colored
        else printed_output
    )


@app.post("/schedules")
async def generate_schedules(data: ScheduleRequest):
    """Generate schedules.

    Args:
        data (ScheduleRequest): The request data.

    Returns:
        list: A list of schedules.
    """
    if len(data.courses) > 10:
        raise HTTPException(status_code=422, detail="Maximum of 10 courses allowed.")

    schedule_generator = ScheduleGenerator(data.courses, data.filters.model_dump())

    await schedule_generator.hydrate_courses_async()
    return schedule_generator.generate_schedules(data.top)


@app.get("/")
def read_root() -> dict:
    """The root endpoint.

    Returns:
        dict: A dictionary containing the message and version of the API.
    """
    return {
        "message": "Plastron API. See /docs for more information.",
        "version": "0.1.0",
    }


@app.get("/health")
async def health() -> dict:
    """Check the health of the API.

    Returns:
        dict: A dictionary containing the health status of the API.
    """
    start = time.time()

    # Calculate uptime
    uptime_seconds = time.time() - app_start_time
    uptime_str = str(timedelta(seconds=int(uptime_seconds)))

    # System diagnostics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()

    end = time.time()
    duration = round((end - start) * 1000, 2)  # in ms

    return {
        "status": "ok",
        "uptime": uptime_str,
        "response_time_ms": duration,
        "system": {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "cpu_usage_percent": cpu_percent,
            "memory_percent": mem.percent,
        },
        "timestamp": datetime.now().isoformat() + "Z",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
