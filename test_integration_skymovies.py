import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import skymovies
from pyrogram import Client

@pytest.mark.asyncio
async def test_skymovies_integration_flow():
    # 1. Mock the HTTP responses for different URLs
    def mock_fetch_html(url):
        if "skymovieshd" in url and url.endswith(".credit/"): # main page
            return """
            <html>
                <div class="Fmvideo" align="left">
                    <b><a href="movie_detail.html">Test Movie (2023) [2GB]</a></b>
                </div>
            </html>
            """
        elif "movie_detail.html" in url:
            return """
            <html>
                <head><title>Test Movie (2023) [2GB]</title></head>
                <body>
                    <div class="Let"><b>Size:</b> 2GB</div>
                    <a href="(https://gdrive.com/direct)">Google Drive Direct Links</a>
                    <a href="https://howblogs.xyz/link1">Download Link</a>
                </body>
            </html>
            """
        return ""

    # Mock the howblogs extraction (runs in executor so we mock the inner func)
    def mock_extract_host_links(url):
        if "howblogs.xyz/link1" in url:
            return {
                "gofile": ["https://gofile.io/d/123"],
                "vikingfile": [],
                "streamtape": [],
                "gdflix": [],
                "hubcloud": []
            }
        return {}

    # 2. Mock Pyrogram Client
    mock_client = MagicMock(spec=Client)
    mock_client.send_message = AsyncMock()

    # 3. Mock Database
    with patch('skymovies.fetch_html', side_effect=mock_fetch_html), \
         patch('skymovies.extract_host_links_from_howblogs', side_effect=mock_extract_host_links), \
         patch('skymovies.already_sent', new_callable=AsyncMock) as mock_already_sent, \
         patch('skymovies.mark_as_sent', new_callable=AsyncMock) as mock_mark_as_sent:

        # Assume movie not sent yet
        mock_already_sent.return_value = False

        # Run the flow using the mocked main page html
        main_html = mock_fetch_html("https://skymovieshd.credit/")

        # Override the SKYMOVIES_CHANNEL_ID in skymovies module for testing
        with patch('skymovies.SKYMOVIES_CHANNEL_ID', -100123):
            results = await skymovies.scrape_skymovies(main_html, mock_client, skip_already_sent=True)

        # Assertions
        assert len(results) == 1
        movie = results[0]
        assert movie["movie_title"] == "Test Movie (2023) [2GB]"
        assert movie["size"] == "2GB"
        assert "https://gdrive.com/direct" in movie["google_drive_links"]
        assert "https://howblogs.xyz/link1" in movie["all_server_links"]

        # Check that telegram message was sent
        mock_client.send_message.assert_called_once()
        args, kwargs = mock_client.send_message.call_args
        assert kwargs["chat_id"] == -100123
        assert "Test Movie (2023)" in kwargs["text"]
        assert "https://gofile.io/d/123" in kwargs["text"]

        # Check DB insert was called
        mock_mark_as_sent.assert_called_once()
        db_args, db_kwargs = mock_mark_as_sent.call_args
        assert db_args[0].endswith("movie_detail.html")  # detail_url
        assert db_args[1] == "Test Movie (2023) [2GB]"   # movie_title
        assert db_kwargs["size"] == "2GB"
