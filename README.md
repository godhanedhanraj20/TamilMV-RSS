# Automated Media Distribution Pipeline

## 1. One-Line Summary

An asynchronous pipeline that scrapes torrents and streaming links from TamilMV and Skymovies, deduplicates records via MongoDB, and distributes files interactively using Pyrogram.

## 2. Project Overview

This system automates the ingestion and distribution of media content from multiple sources. Operating as a continuous pipeline, it extracts newly posted items from the TamilMV forum and Skymovies listing pages, processes metadata (size, category, hosts), filters out previously ingested items, and publishes them to designated Telegram destinations. An integrated HTTP keep-alive server ensures the application remains active on PaaS environments, and an interactive `/search` command allows users to query content directly from Telegram.

## 3. System Architecture

```text
       [TamilMV Forum]                 [Skymovies]
             |                              |
             v                              v
        (cloudscraper)                 (cloudscraper)
       [TMV Scraper]                  [Sky Scraper]
             |                              |
             v                              v
      [TMV Deduplication]<-------->[Sky Deduplication]
        (MongoDB)                      (MongoDB)
             |                              |
             v                              v
    [Torrent Downloader]              [Link Parser]
             |                              |
             +--------------+---------------+
                            |
                            v
                      (Pyrogram API)
                  [Telegram Distributor]
                            |
             +--------------+---------------+
             |              |               |
         [Channel]    [Leech Group]   [Mirror Group]

=======================================================
             [Interactive /search Command]
             |
        (bot.py Handler) -> (search.py Engine) -> TamilMV
```

### Component-Level Architecture

- `bot.py`: The orchestrator. Initializes the Pyrogram client session, manages the `aiohttp` web server, runs the periodic async scraping loops (`tamilmv` & `skymovies`), handles interactive commands like `/search`, and manages the keep-alive ping thread.
- `tamilmv.py`: The torrent pipeline engine. Parses DOM structures, downloads `.torrent` files, and dispatches them via Telegram.
- `skymovies.py`: The streaming pipeline engine. Extracts multi-host direct download links (GoFile, Streamtape, etc.), groups them logically, and constructs structured Telegram posts.
- `search.py`: The standalone query engine. Enables non-blocking, on-demand searches against TamilMV.
- `database.py`: The deduplication layer. Manages the connection pool to MongoDB and exposes primitives for tracking state across the `Tamilmv` and `Skymovies` collections.
- `configs.py`: The configuration layer. Maps process environment variables to typed Python constants utilized across the system.

## 4. Execution Timeline

### Startup Phase
1. Load config: `configs.py` parses variables from `.env` or the environment.
2. Connect MongoDB: `database.py` initializes the AsyncIOMotorClient connection.
3. Initialize Telegram client: `bot.py` creates the Pyrogram client using the provided V2 string session.
4. Start web server: `bot.py` binds the `aiohttp` application to the specified `$PORT`.

### Runtime Loop
1. Fetch Topics: The pipeline simultaneously queries the TamilMV base URL and Skymovies URLs.
2. Extract Metadata: HTML is parsed to locate `.torrent` references or streaming direct links.
3. Check Duplicates: The specific URLs are queried against the MongoDB `Tamilmv` and `Skymovies` collections. Existing items are skipped.
4. Download/Parse: Physical `.torrent` files are downloaded, or direct streaming URLs are parsed into categorized lists.
5. Upload to Telegram: Files and structured text blocks are dispatched to the configured Telegram targets.
6. Save to DB: The system inserts the processing metadata into MongoDB to prevent future duplication.
7. Repeat loop: The async context sleeps for `SCRAPE_INTERVAL` seconds before restarting.

## 5. Developer Onboarding Flow

### Prerequisites
- Python 3.9+
- Active MongoDB instance/cluster
- Telegram API Credentials (`API_ID`, `API_HASH`)

### Step 1: Clone Repository
```bash
git clone <repository_url>
cd <repository_directory>
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio # Optional: For running the test suite
```

### Step 3: Setup Environment Variables
Create a `.env` file in the project root:
```env
API_ID=1234567
API_HASH=your_api_hash_here
USER_SESSION=your_pyrogram_v2_string_session
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=Cluster0
TMV_TORRENT=-1001234567890
TMV_LEECH_GRP=-1009876543210
TMV_MIRROR_GRP=-1001122334455
SKYMOVIES_CHANNEL_ID=-1005544332211
```

### Step 4: Generate Pyrogram Session
You must generate a Pyrogram V2 String Session and assign it to the `USER_SESSION` variable.

### Step 5: Setup MongoDB
Ensure your MongoDB cluster is accessible from your development machine. The system will automatically create the database and required collections upon first insertion.

### Step 6: Test Suite Verification
Run the unit and integration tests to ensure your local environment is configured properly.
```bash
pytest -v
```

### Step 7: Run Bot
```bash
python bot.py
```

## 6. Environment Variables

### Required
| Variable | Description |
| :--- | :--- |
| `API_ID` | Telegram API ID for client authentication. |
| `API_HASH` | Telegram API Hash for client authentication. |
| `USER_SESSION` | Pyrogram V2 String Session token. |
| `DATABASE_URL` | Full MongoDB connection URI. |
| `DATABASE_NAME` | Target database name within the MongoDB cluster. |
| `TMV_TORRENT` | Telegram Chat ID for primary TamilMV channel uploads. |
| `TMV_LEECH_GRP` | Telegram Chat ID for TamilMV leech group uploads. |
| `TMV_MIRROR_GRP` | Telegram Chat ID for TamilMV mirror group uploads. |
| `SKYMOVIES_CHANNEL_ID` | Telegram Chat ID for Skymovies structured posts. |

### Optional
| Variable | Description |
| :--- | :--- |
| `PORT` | Bind port for the `aiohttp` server (Default: `8080`). |
| `URL` | Public URL for the deployment, utilized by the keep-alive ping. |
| `TMV_URL` | Base URL of the TamilMV forum (Default: `https://www.1tamilmv.land/`). |
| `SKYMOVIES_URL` | Base URL of the Skymovies site (Default: `https://skymovieshd.credit/`). |
| `TMV_TORRENT_THUMB` | URL to a thumbnail image embedded in Telegram posts. |
| `BOT_TAG` | Prefix string prepended to filenames. |

### Internal
| Variable | Description |
| :--- | :--- |
| `PING_INTERVAL` | Keep-alive loop duration in seconds (Default: `120`). |
| `SCRAPE_INTERVAL` | Main scraping loop duration in seconds (Default: `300`). |
| `SIZE_LIMIT_GB` | Maximum file size in GB; larger files are discarded early (Default: `50`). |

## 7. Data Flow & Storage

The system utilizes MongoDB as the source of truth for processed items across two distinct collections:

- `Tamilmv` Collection: Stores `file_name`, `file_url`, `magnet`, `size_mb`, `category`, and `upload_date`.
- `Skymovies` Collection: Stores `detail_url`, `movie_title`, `size`, `sent_time`, `google_drive_links`, `all_server_links`, `listing_title`, and `upload_date`.

Deduplication Rationale: Operating on a continuous loop means the scraper frequently encounters previously processed topics. Checking MongoDB before executing network IO operations prevents redundant bandwidth usage, prevents Telegram channel flooding, and mitigates API rate limits.

## 8. Testing Suite

The repository implements a robust `pytest` testing suite utilizing `unittest.mock` to validate code flows without triggering live external APIs.

- Unit Tests: Found in `test_skymovies.py`, `test_search_suite.py`, and `test_database.py`. These files validate HTML parsing logic, fallback behaviors, asynchronous database mocks, and message template generation.
- Integration Tests: Found in `test_integration_skymovies.py` and `test_integration_tamilmv.py`. These tests simulate end-to-end pipeline executions by mocking the HTTP request layer (`cloudscraper`), verifying that the Pyrogram client sends the expected payloads to the correct channels, and asserting that database insertion calls are constructed correctly.

## 9. Failure Scenarios

- DOM Structure Changes: If class names or DOM hierarchies alter on TamilMV or Skymovies, `BeautifulSoup` queries fail silently. The scraper yields zero results until the parser rules are updated. This is mitigated by unit tests which will break if the mock HTML models differ from reality.
- IO Failures: If `cloudscraper` times out or receives a non-200 response, the specific file is skipped. It is not recorded in the DB, meaning the system will attempt it again on the next loop.
- Telegram Upload Fails: Caught via generic exception handling. The script logs the error and moves on. Crucially, the DB insert occurs *after* upload attempts. If upload fails completely, the DB is not updated, allowing a retry on the next cycle.
- MongoDB Connectivity Issues: Connection timeouts will throw exceptions during `find_one` calls, immediately breaking the current iteration of the scraping loop and preventing unwanted duplication logic from proceeding.

## 10. Scaling Model

### Current Architecture Limitations
- Single-threaded loop: All parsing, downloading, and uploading occurs sequentially within the `asyncio` event loop. One slow upload blocks the entire pipeline.
- No queue system: State resides entirely in the HTML layout of the target sites and MongoDB.
- Tight coupling: Scraping logic and Telegram API distribution logic reside in the same function block for the main scripts.

### Proposed Architecture Improvements
- Introduce Redis Queue: Push discovered URLs to a Redis list or Celery task queue rather than processing them inline.
- Separate Workers: Decouple the system into a "Scraper Service" (produces URLs) and an "Uploader Service" (consumes URLs, downloads, and uploads). This allows multiple upload workers to run in parallel.
- Add Retry System: Implement exponential backoff for Telegram API calls.

## 11. Customization Guide

- Modify targets: Adjust `TMV_URL` or `SKYMOVIES_URL`. Note that significant domain changes will require rewrites in the respective parsers.
- Adjust logic: Update regex patterns in `categorize_content` (TamilMV) or the host link mapping dictionaries in `skymovies.py`.
- Alter Telegram styling: Modify the structured templates inside `skymovies_message_template` or the `/search` command loop in `bot.py`.

## 12. Limitations

- Fragile parsing: Completely dependent on a highly specific HTML structures.
- Blocking IO Risks: Wrapping synchronous requests inside `asyncio.to_thread` mitigates main loop blocking, but still incurs scaling limitations at high concurrency.
- Lacking centralized logging: Currently relies on raw console printing.

## 13. Example Outputs

**TamilMV Upload:**
```text
[BOT_TAG] - Leo_2023_1080p_WEB_DL.torrent

#Movies #TamilMV

Powered By ✨ [BOT_TAG]
```

**Skymovies Upload:**
```text
🎬 New Post Just Dropped! ✅

📌 Test Movie (2023) [2GB]

<blockquote><b>🔰GoFile Link🔰</b></blockquote>
• https://gofile.io/d/123

<blockquote><b>🐬Stream Tape Link🐬</b></blockquote>
• https://streamtape.com/v/123

<blockquote>Powered By Downloader Zone</blockquote>
```

**Interactive /search Command:**
```text
**Top Results:**

**1.** Leo (2023) 1080p WEB-DL
Size: 2.4GB
Link: https://www.1tamilmv.land/index.php?/forums/topic/...

[Open Result 1] (Inline Button)
```

## 14. Troubleshooting

- Telegram Auth Issues: Pyrogram throws a `SessionPasswordNeeded` or `AuthKeyUnregistered` exception. Solution: Regenerate the V2 string session and update the `.env`.
- No New Items Found: The logs show successful scraping but zero found items. Solution: The domain structure has likely changed. Verify the DOM classes (`Fmvideo`, `cPost_contentWrap`) manually.
- Upload Failures: Logs show "Send failed". Solution: Ensure the Pyrogram session user has administrative/write permissions in the target Channel and Groups.
