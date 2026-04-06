import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import database.database as database

@pytest.mark.asyncio
async def test_already_sent():
    # Mock skymovies_collection
    with patch('database.database.skymovies_collection.find_one', new_callable=AsyncMock) as mock_find_one:
        mock_find_one.return_value = {"detail_url": "test_url"}

        result = await database.already_sent("test_url")
        assert result is True
        mock_find_one.assert_called_once_with({"detail_url": "test_url"})

        mock_find_one.return_value = None
        result2 = await database.already_sent("new_url")
        assert result2 is False

@pytest.mark.asyncio
async def test_mark_as_sent():
    with patch('database.database.skymovies_collection.insert_one', new_callable=AsyncMock) as mock_insert_one:
        await database.mark_as_sent("url", "title", "size", 12345, [], [], "list_title")
        mock_insert_one.assert_called_once()
        args, _ = mock_insert_one.call_args
        doc = args[0]
        assert doc["detail_url"] == "url"
        assert doc["movie_title"] == "title"
        assert doc["size"] == "size"
        assert doc["sent_time"] == 12345
        assert doc["google_drive_links"] == []
        assert doc["all_server_links"] == []
        assert doc["listing_title"] == "list_title"
        assert "upload_date" in doc

@pytest.mark.asyncio
async def test_is_tmv_exist():
    with patch('database.database.tmv_collection.find_one', new_callable=AsyncMock) as mock_find_one:
        mock_find_one.return_value = {"file_url": "test_url"}

        result = await database.is_tmv_exist("test_url")
        assert result is True
        mock_find_one.assert_called_once_with({"file_url": "test_url"})

@pytest.mark.asyncio
async def test_add_tmv_new():
    with patch('database.database.tmv_collection.find_one', new_callable=AsyncMock) as mock_find_one, \
         patch('database.database.tmv_collection.insert_one', new_callable=AsyncMock) as mock_insert_one:

        mock_find_one.return_value = None

        await database.add_tmv("file.txt", "http://file", "magnet:?", 100, "Movies")

        mock_find_one.assert_called_once_with({"file_url": "http://file"})
        mock_insert_one.assert_called_once()

        args, _ = mock_insert_one.call_args
        doc = args[0]
        assert doc["file_name"] == "file.txt"
        assert doc["file_url"] == "http://file"
        assert doc["size_mb"] == 100
        assert doc["category"] == "Movies"

@pytest.mark.asyncio
async def test_add_tmv_existing():
    with patch('database.database.tmv_collection.find_one', new_callable=AsyncMock) as mock_find_one, \
         patch('database.database.tmv_collection.insert_one', new_callable=AsyncMock) as mock_insert_one:

        mock_find_one.return_value = {"file_url": "http://file"}

        await database.add_tmv("file.txt", "http://file", "magnet:?", 100, "Movies")

        mock_find_one.assert_called_once_with({"file_url": "http://file"})
        mock_insert_one.assert_not_called()
