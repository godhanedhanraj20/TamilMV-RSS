import pytest
from unittest.mock import patch, MagicMock
import search

@pytest.mark.asyncio
@patch('search.cloudscraper.create_scraper')
async def test_search_tamilmv(mock_create_scraper):
    mock_scraper = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <a href="https://www.1tamilmv.land/index.php?/forums/topic/123&do=findComment">Leo (2023) [2.4GB] WEB-DL</a>
        <a href="https://www.1tamilmv.land/index.php?/forums/topic/456&do=findComment">Avatar 2 1080p 3.5GB</a>
        <a href="https://www.1tamilmv.land/index.php?/forums/topic/789">Some other link not match do=findComment</a>
        <a href="https://www.1tamilmv.land/index.php?/forums/topic/123&do=findComment">Leo (2023) [2.4GB] WEB-DL</a> <!-- Duplicate -->
    </html>
    """
    mock_scraper.get.return_value = mock_response
    mock_create_scraper.return_value = mock_scraper

    results = await search.search_tamilmv("test query")

    assert len(results) == 2
    assert results[0]["title"] == "Leo (2023) [2.4GB] WEB-DL"
    assert results[0]["size"] == "2.4GB"
    assert results[0]["link"] == "https://www.1tamilmv.land/index.php?/forums/topic/123"

    assert results[1]["title"] == "Avatar 2 1080p 3.5GB"
    assert results[1]["size"] == "3.5GB"
    assert results[1]["link"] == "https://www.1tamilmv.land/index.php?/forums/topic/456"

@pytest.mark.asyncio
@patch('search.cloudscraper.create_scraper')
async def test_search_tamilmv_empty(mock_create_scraper):
    mock_scraper = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_scraper.get.return_value = mock_response
    mock_create_scraper.return_value = mock_scraper

    results = await search.search_tamilmv("not found")
    assert len(results) == 0
