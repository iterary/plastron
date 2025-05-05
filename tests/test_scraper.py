"""Tests for the scraper."""

import aiohttp
import pytest

from datetime import datetime
from plastron.scraper import get_closest_term_id, is_spring, scrape_course


def test_get_closest_term_id():
    """Test that the closest term ID is returned correctly."""
    christmas = datetime(2024, 12, 25)
    term_id = get_closest_term_id(christmas)
    assert term_id == "202501"

    april_fools = datetime(2025, 4, 1)
    term_id = get_closest_term_id(april_fools)
    assert term_id == "202508"


def test_is_spring():
    """Test that the term is identified as spring correctly."""
    christmas = datetime(2024, 12, 25)
    assert is_spring(christmas) == False

    april_fools = datetime(2025, 4, 1)
    assert is_spring(april_fools) == True


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_scrape_course():
    """Test that the course is scraped correctly."""
    # This is kinda brittle, but it's a decent sanity check
    course_id = "ANSC101"
    async with aiohttp.ClientSession() as session:
        sections = await scrape_course(course_id, session)
        assert len(sections) > 0


# Unit tests generally aren't suited for scraping, refer to README for E2E testing
