import pytest
from bs4 import BeautifulSoup
import skymovies
from unittest.mock import patch, MagicMock, AsyncMock

def test_extract_movie_info():
    html = """
    <html>
        <head><title>The Matrix (1999) Full Movie Download</title></head>
        <body>
            <div class="Let"><b>Size:</b> 1.5GB</div>
        </body>
    </html>
    """
    title, size = skymovies.extract_movie_info(html)
    assert title == "The Matrix (1999)"
    assert size == "1.5GB"

def test_extract_movie_info_bracket_fallback():
    html = """
    <html>
        <head><title>Avatar [2.4GB] Full Movie Download</title></head>
        <body></body>
    </html>
    """
    title, size = skymovies.extract_movie_info(html)
    assert title == "Avatar [2.4GB]"
    assert size == "2.4GB"

def test_extract_google_drive_direct_links_from_html():
    html = """
    <html>
        <a href="https://gdrive.com/1">Google Drive Direct Links</a>
        <a href="https://gdrive.com/2">Other link</a>
        <a href="(https://gdrive.com/3)">Google Drive Direct Links</a>
    </html>
    """
    links = skymovies.extract_google_drive_direct_links_from_html(html)
    assert len(links) == 2
    assert "https://gdrive.com/1" in links
    assert "https://gdrive.com/3" in links

def test_extract_all_howblogs_links():
    html = """
    <html>
        <a href="https://howblogs.xyz/1">Download Here</a>
        <a href="https://howblogs.xyz/2">Watch Online</a>
        <a href="https://howblogs.xyz/3">1080p WEB-DL LINK</a>
        <a href="(https://howblogs.xyz/4)">Another Link</a>
    </html>
    """
    links = skymovies.extract_all_howblogs_links(html)
    assert len(links) == 2
    assert "https://howblogs.xyz/1" in links
    assert "https://howblogs.xyz/4" in links

@patch('skymovies.cloudscraper.create_scraper')
def test_extract_host_links_from_howblogs(mock_create_scraper):
    mock_scraper = MagicMock()
    mock_response = MagicMock()
    mock_response.text = """
    <html>
        <a href="https://gofile.io/d/123">GoFile</a>
        <a href="https://vikingfile.com/d/123">Viking</a>
        <a href="https://streamtape.com/v/123">StreamTape</a>
        <a href="https://gdflix.com/d/123">GDFlix</a>
    </html>
    """
    mock_scraper.get.return_value = mock_response
    mock_create_scraper.return_value = mock_scraper

    hosts = skymovies.extract_host_links_from_howblogs("http://test.com")
    assert "https://gofile.io/d/123" in hosts["gofile"]
    assert "https://vikingfile.com/d/123" in hosts["vikingfile"]
    assert "https://streamtape.com/v/123" in hosts["streamtape"]
    assert "https://gdflix.com/d/123" in hosts["gdflix"]
    assert len(hosts["hubcloud"]) == 0

def test_skymovies_message_template():
    movie_info = {
        "movie_title": "Test Movie",
    }
    host_links = {
        "gofile": ["http://gofile.io/1"],
        "streamtape": ["http://streamtape.com/1"],
        "hubcloud": ["http://hubcloud.com/1"]
    }
    msg = skymovies.skymovies_message_template(movie_info, host_links)

    assert "Test Movie" in msg
    assert "🔰GoFile Link🔰" in msg
    assert "http://gofile.io/1" in msg
    assert "🐬Stream Tape Link🐬" in msg
    assert "http://streamtape.com/1" in msg
    assert "♻️All Cloud Links♻️" in msg
    assert "http://hubcloud.com/1" in msg
