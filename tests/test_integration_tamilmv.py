import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import scrapers.tamilmv as tamilmv
from pyrogram import Client
import os

@pytest.mark.asyncio
async def test_tamilmv_integration_flow():
    # 1. Mock cloudscraper for HTTP
    mock_scraper = MagicMock()

    # We will track which URL is requested and return appropriate HTML
    def mock_get(url, **kwargs):
        resp = MagicMock()
        resp.status_code = 200

        if url == tamilmv.TMV_URL:
            resp.text = """
            <html>
                <a href="https://www.1tamilmv.land/index.php?/forums/topic/123-leo">topic/123-leo</a>
            </html>
            """
        elif "topic/123-leo" in url:
            resp.text = """
            <html>
                <div class="cPost_contentWrap">
                    <a href="https://download.com/leo.torrent">Leo (2023) [2GB].torrent</a>
                    <span>2 gb</span>
                </div>
            </html>
            """
        elif "leo.torrent" in url:
            # For the stream download request
            resp.iter_content.return_value = [b"torrent_data"]

        return resp

    mock_scraper.get.side_effect = mock_get

    # 2. Mock Pyrogram Client
    mock_client = MagicMock(spec=Client)
    # mock send_document
    mock_msg = MagicMock()
    mock_msg.id = 100
    mock_client.send_document = AsyncMock(return_value=mock_msg)
    mock_client.send_message = AsyncMock()

    # 3. Apply Patches
    with patch('scrapers.tamilmv.cloudscraper.create_scraper', return_value=mock_scraper), \
         patch('scrapers.tamilmv.tmv_collection.find_one', new_callable=AsyncMock) as mock_find_one, \
         patch('scrapers.tamilmv.tmv_collection.insert_one', new_callable=AsyncMock) as mock_insert_one, \
         patch('scrapers.tamilmv.asyncio.sleep', new_callable=AsyncMock): # disable sleep to run fast

        # Simulate db check: not exists
        mock_find_one.return_value = None

        # Execute
        with patch('scrapers.tamilmv.TMV_TORRENT', -1001), \
             patch('scrapers.tamilmv.TMV_LEECH_GRP', -1002), \
             patch('scrapers.tamilmv.TMV_MIRROR_GRP', -1003):
            await tamilmv.tmv_scraper(mock_client)

        # Assertions

        # Check that download happened (file created)
        # Expected clean filename based on logic: BOT_TAG - Leo (2023) [2GB].torrent
        filename = tamilmv.clean_filename("Leo (2023) [2GB].torrent")

        # Check telegram sends
        assert mock_client.send_document.call_count == 3
        # First call args
        args, kwargs = mock_client.send_document.call_args_list[0]
        assert kwargs["chat_id"] == -1001
        assert filename in kwargs["document"]
        assert "Movies" in kwargs["caption"]

        # Check DB insert was called
        mock_insert_one.assert_called_once()
        db_args, _ = mock_insert_one.call_args
        assert db_args[0]["file_name"] == "Leo (2023) [2GB].torrent"
        assert db_args[0]["file_url"] == "https://download.com/leo.torrent"
        assert db_args[0]["category"] == "Movies"

        # Cleanup file if it was created
        if os.path.exists(filename):
            os.remove(filename)
