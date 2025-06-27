"""Tests for the API."""

from fastapi.testclient import TestClient
from dotenv import load_dotenv
import os

from plastron.api import app

client = TestClient(app)

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"
KEY_REQUIRED = os.getenv("KEY_REQUIRED", "false").lower() == "true"


def test_api_generate_schedules():
    """Test that the generate schedules endpoint returns a schedule with the correct number of sections."""
    response = client.post(
        "/schedules",
        json={
            "courses": ["ANSC101", "ANSC103"],
            "top": 1,
            "filters": {
                "no_esg": True,
                "no_fc": True,
                "open_seats": False,
                "earliest_start": "8:00am",
                "latest_end": "5:00pm",
            },
        },
    )
    assert response.status_code == 200
    assert len(response.json()[0]["sections"]) == 2


def test_api_visualize_schedules():
    """Test that the visualize schedules endpoint returns a valid response."""
    response = client.post(
        "/schedules/visualized",
        json={
            "courses": ["ANSC101", "ANSC103"],
            "top": 1,
            "filters": {
                "no_esg": True,
                "no_fc": True,
                "open_seats": False,
                "earliest_start": "8:00am",
                "latest_end": "5:00pm",
            },
        },
    )
    assert response.status_code == 200
    assert response.text is not None


def test_api_health():
    """Test that the health endpoint returns a valid response."""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "ok"
    assert "uptime" in data
    assert "response_time_ms" in data
    assert "system" in data


def test_api_root():
    """Test that the root endpoint returns a valid response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() is not None
