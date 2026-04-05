# TamilMV Telegram Distribution Pipeline

## 1. One-Line Summary

An asynchronous, single-threaded pipeline that scrapes torrents from TamilMV, deduplicates records via MongoDB, and distributes files to multiple Telegram destinations using Pyrogram.

## 2. Project Overview

This system automates the ingestion and distribution of media torrents. Operating as a continuous pipeline, it extracts newly posted torrent files from the TamilMV forum, processes metadata (size, category), filters out previously ingested or oversized files, and publishes the remaining files to designated Telegram channels and groups. An integrated HTTP keep-alive server ensures the application remains active when deployed on PaaS environments.

## 3. System Architecture

```text
       [TamilMV Forum]
             |
             v
        (cloudscraper)
       [Scraping Engine]
             |
             v
       (BeautifulSoup)
       [Metadata Parser] ---> [MongoDB Deduplication]
             |                        |
        [New File] <------------------+
             |
             v
    [Torrent Downloader]
             |
             v
       (Pyrogram API)
   [Telegram Distributor] ---> [Channel] / [Leech Group] / [Mirror Group]
             |
             v
     [MongoDB Updater]
```

### Component-Level Architecture

- `bot.py`: The orchestrator. Initializes the Pyrogram client session, manages the `aiohttp` web server, runs the periodic async scraping loop, and handles the keep-alive ping thread.
- `tamilmv.py`: The pipeline engine. Executes the HTTP requests, parses DOM structures to extract links, sanitizes filenames, categorizes content, downloads physical `.torrent` files, and dispatches them via Telegram.
- `database.py`: The deduplication layer. Manages the connection pool to MongoDB and exposes primitives for checking existing records and inserting new metadata.
- `configs.py`: The configuration layer. Maps process environment variables to typed Python constants utilized across the system.

## 4. Execution Timeline

### Startup Phase
1. Load config: `configs.py` parses variables from `.env` or the environment.
2. Connect MongoDB: `database.py` initializes the AsyncIOMotorClient connection.
3. Initialize Telegram client: `bot.py` creates the Pyrogram client using the provided V2 string session.
4. Start web server: `bot.py` binds the `aiohttp` application to the specified `$PORT`.

### Runtime Loop
1. Fetch topics: The pipeline queries the TamilMV base URL for recent forum topic links.
2. Extract torrent links: Topic HTML is parsed to locate anchor tags containing `.torrent` references.
3. Check duplicates: The `file_url` is queried against the MongoDB `Tamilmv` collection. If a match exists, the entry is skipped.
4. Download torrent: The system downloads the physical `.torrent` file to the local filesystem.
5. Upload to Telegram: The file is sequentially dispatched to the configured Channel, Leech Group, and Mirror Group.
6. Save to DB: The system inserts the torrent metadata into MongoDB to prevent future duplication.
7. Repeat loop: The async context sleeps for `SCRAPE_INTERVAL` seconds before restarting the runtime loop.

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
```

### Step 4: Generate Pyrogram Session
You must generate a Pyrogram V2 String Session and assign it to the `USER_SESSION` variable.

### Step 5: Setup MongoDB
Ensure your MongoDB cluster is accessible from your development machine. The system will automatically create the database and the `Tamilmv` collection upon first insertion.

### Step 6: Run Bot
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
| `TMV_TORRENT` | Telegram Chat ID for primary channel uploads. |
| `TMV_LEECH_GRP` | Telegram Chat ID for leech group uploads. |
| `TMV_MIRROR_GRP` | Telegram Chat ID for mirror group uploads. |

### Optional
| Variable | Description |
| :--- | :--- |
| `PORT` | Bind port for the `aiohttp` server (Default: `8080`). |
| `URL` | Public URL for the deployment, utilized by the keep-alive ping. |
| `TMV_URL` | Base URL of the TamilMV forum (Default: `https://www.1tamilmv.land/`). |
| `TMV_TORRENT_THUMB` | URL to a thumbnail image embedded in Telegram posts. |
| `BOT_TAG` | Prefix string prepended to filenames. |

### Internal
| Variable | Description |
| :--- | :--- |
| `PING_INTERVAL` | Keep-alive loop duration in seconds (Default: `120`). |
| `SCRAPE_INTERVAL` | Main scraping loop duration in seconds (Default: `300`). |
| `SIZE_LIMIT_GB` | Maximum file size in GB; larger files are discarded early (Default: `50`). |

## 7. Data Flow & Storage

The system utilizes MongoDB as the source of truth for processed items.

- Storage Model: The `Tamilmv` collection stores documents containing `file_name`, `file_url`, `magnet`, `size_mb`, `category`, and `upload_date`.
- Deduplication Rationale: Operating on a continuous loop means the scraper frequently encounters previously processed topics. Checking MongoDB before executing network IO operations (downloading and uploading) prevents redundant bandwidth usage and Telegram channel flooding.
- Failure Impact: If MongoDB is unreachable, the system may crash or skip operations. If the database is wiped, the system loses its state and will re-upload all torrents currently visible on the target site's first page.

## 8. Failure Scenarios

- TamilMV structure changes: If class names or DOM hierarchies alter, `BeautifulSoup` queries fail silently. The scraper yields zero results until the parser rules are updated.
- Torrent download fails: If `cloudscraper` times out or receives a non-200 response, the specific file is skipped. It is not recorded in the DB, meaning the system will attempt it again on the next loop.
- Telegram upload fails: Caught via generic exception handling. The script logs the error and moves on. Crucially, the DB insert occurs *after* upload attempts. If upload fails completely, the DB is not updated, allowing a retry on the next cycle.
- MongoDB failure: The pipeline relies heavily on DB checks. Connection timeouts will throw exceptions during the `find_one` calls, breaking the current iteration of the scraping loop.
- Network issues: A dropped connection halts the current async flow. The loop will attempt to restart operations after the configured `SCRAPE_INTERVAL`.

## 9. Scaling Model

### Current Architecture Limitations
- Single-threaded loop: All parsing, downloading, and uploading occurs sequentially within the `asyncio` event loop. One slow upload blocks the entire pipeline.
- No queue system: State resides entirely in the HTML layout of the target site and MongoDB. There is no transient state management for jobs.
- No retry mechanism: Ephemeral failures (e.g., brief Telegram API timeouts) simply fail the current job, which must wait for the next full 5-minute loop cycle.
- Tight coupling: Scraping logic and Telegram API distribution logic reside in the same function block, making testing and horizontal scaling impossible.

### Proposed Architecture Improvements
- Introduce Redis Queue: Push discovered URLs to a Redis list or Celery task queue rather than processing them inline.
- Separate Workers: Decouple the system into a "Scraper Service" (produces URLs) and an "Uploader Service" (consumes URLs, downloads, and uploads). This allows multiple upload workers to run in parallel.
- Add Retry System: Implement exponential backoff for Telegram API calls.
- Add Rate Limiting: Introduce active throttling to prevent Pyrogram `FloodWait` exceptions when processing large batches of new files.
- Add Proxy Rotation: Integrate a proxy pool into `cloudscraper` to mitigate IP bans from the target forum.

## 10. Customization Guide

- Change scrape source: Update `TMV_URL`. Because parsing is hardcoded to TamilMV's DOM, you must rewrite the `tmv_scraper` function in `tamilmv.py` to extract topics and anchor tags specific to the new domain.
- Modify filters: To alter file size thresholds, change `SIZE_LIMIT_GB`. To change categorical mapping, adjust the regex patterns in the `categorize_content` function inside `tamilmv.py`.
- Adjust Telegram behavior: Modify the `send_torrent` function in `tamilmv.py`. You can change destination chats, remove thumbnail logic, or alter the static caption structure and auto-reply commands (`/qbleech`).
- Extend pipeline: Add new functions inside the `tmv_scraper` loop between the download and upload steps (e.g., file renaming, metadata extraction via `torrentool`).

## 11. Limitations

- Fragile parsing: Completely dependent on a highly specific HTML structure.
- Blocking IO: Using `requests` via `cloudscraper` inside an `asyncio` loop without thread pools technically blocks the event loop during file downloads.
- Missing logging infrastructure: Relies on `print` statements, making production monitoring via ELK or Datadog difficult.
- In-memory state risk: Relying strictly on MongoDB for duplicate checks without localized caching increases DB roundtrips.

## 12. Future Improvements

- Refactor `cloudscraper` calls to execute in an `asyncio.to_thread` executor to prevent blocking the async event loop.
- Implement standard Python `logging` with structured JSON output.
- Add command-line argument parsing to manually trigger scraping outside the standard timer.
- Build a lightweight `aiohttp` dashboard to view recent DB insertions and manual retry controls.

## 13. Example Output

A standard message published to the primary channel looks like this:

```text
[BOT_TAG] - Leo_2023_1080p_WEB_DL.torrent

#Movies #TamilMV

Powered By ✨ [BOT_TAG]
```
*(The post includes the .torrent file as an attachment and optionally embeds the thumbnail defined in `TMV_TORRENT_THUMB`)*

## 14. Troubleshooting

- Telegram Auth Issues: Pyrogram throws a `SessionPasswordNeeded` or `AuthKeyUnregistered` exception. Solution: Regenerate the V2 string session and update the `.env`.
- No Torrents Found: The logs show successful scraping but zero found items. Solution: The domain structure has likely changed. Verify the DOM classes (`cPost_contentWrap`) manually.
- Upload Failures: Logs show "Send failed". Solution: Ensure the Pyrogram session user has administrative/write permissions in the target Channel and Groups.
- MongoDB Connection Issues: `ServerSelectionTimeoutError` occurs. Solution: Verify your IP is whitelisted in the MongoDB Atlas network access panel, or check the connection string formatting.
