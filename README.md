## 1. Project Overview

This project is an automated, pipeline-driven scraping and distribution system. It acts as an intermediary pipeline that extracts newly posted torrent files from a specific source (TamilMV), processes and categorizes the data, filters out duplicates and oversized files, and finally distributes the content across multiple designated Telegram destinations. The system operates autonomously on a continuous loop while maintaining an active web server to ensure constant uptime on cloud platforms.

## 2. Core Features

- Scraping Automation: Utilizes `cloudscraper` and `BeautifulSoup` to bypass simple bot protections and extract DOM elements reliably.
- Duplicate Prevention (MongoDB): Maintains a persistent state to ensure torrents are processed and uploaded exactly once.
- Telegram Multi-Destination Upload: Interfaces with the Telegram API via Pyrogram to distribute files to a channel, a leech group, and a mirror group simultaneously with distinct commands.
- Size Filtering: Implements logic to skip files exceeding a configurable gigabyte threshold before initiating downloads.
- Category Detection: Uses regex-based parsing to automatically classify content as Movies, Series, or Dubbed content based on filenames.
- Keep-Alive Server: Runs a lightweight `aiohttp` web server and a self-pinging background thread to prevent idle state sleep on PaaS providers like Heroku or Render.

## 3. Architecture Breakdown

- `bot.py`: The main orchestration layer. It initializes the Pyrogram client, starts the `aiohttp` web server, runs the periodic scraping event loop, and handles the keep-alive ping thread.
- `tamilmv.py`: Contains the core scraping logic, HTML parsing strategies, file downloading logic, filename sanitization, categorization rules, and Telegram upload procedures.
- `database.py`: The data persistence layer handling MongoDB connection pooling and defining the database operations (insert/check) for duplicate prevention.
- `configs.py`: The environment configuration module that loads and exposes variables from the execution environment or a `.env` file.

## 4. Execution Flow (Step-by-Step)

1. Bot Starts: The main script is executed, initializing the asynchronous event loop.
2. Telegram Client Logs In: The Pyrogram client authenticates using a string session.
3. Web Server Starts: The `aiohttp` server binds to the designated port and a background thread begins pinging the application URL.
4. Scraper Loop Runs: The periodic extraction loop activates.
5. Topics Fetched: The scraper retrieves the recent topics from the main site index.
6. Torrent Links Extracted: The scraper parses topic pages to find actual `.torrent` file links and metadata.
7. Duplicate Check: The system queries MongoDB to verify if the file URL has been processed previously.
8. File Download: If new, the torrent file is downloaded to the local filesystem.
9. Telegram Upload: The file is uploaded to the target Telegram channel and groups with relevant captions and commands.
10. DB Insert: A record containing metadata is inserted into MongoDB to prevent future duplication.
11. Loop Repeats: The process sleeps for a configurable interval before restarting from step 4.

## 5. Environment Variables

| Variable | Type | Description |
| :--- | :--- | :--- |
| **Required Variables** |
| `API_ID` | Integer | Telegram API ID from my.telegram.org. |
| `API_HASH` | String | Telegram API Hash from my.telegram.org. |
| `USER_SESSION` | String | Pyrogram V2 string session for Telegram authentication. |
| `DATABASE_URL` | String | MongoDB connection URI. |
| `DATABASE_NAME` | String | The specific database name within MongoDB to use. |
| `TMV_TORRENT` | Integer | Target Telegram chat/channel ID for torrent file uploads. |
| `TMV_LEECH_GRP` | Integer | Target Telegram chat/group ID for leech commands. |
| `TMV_MIRROR_GRP` | Integer | Target Telegram chat/group ID for mirror commands. |
| **Optional Variables** |
| `PORT` | Integer | Port for the web server to bind to (Default: `8080`). Required for cloud PaaS. |
| `URL` | String | The public URL of the deployed application. Used by the ping mechanism. |
| `TMV_URL` | String | Base URL for the scraping target (Default: `https://www.1tamilmv.land/`). |
| `TMV_TORRENT_THUMB` | String | Direct URL to an image file used as the thumbnail for uploads. |
| `BOT_TAG` | String | Prefix string added to generated filenames and captions. |
| **Internal Configs** |
| `PING_INTERVAL` | Integer | Time in seconds between keep-alive pings (Default: `120`). |
| `SCRAPE_INTERVAL` | Integer | Time in seconds between scraping execution loops (Default: `300`). |
| `SIZE_LIMIT_GB` | Integer | Maximum file size in Gigabytes allowed for processing (Default: `50`). |

## 6. Deployment Guide

### Local Run

1. Clone the repository to your local machine.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and populate it with your environment variables.
4. Run the main orchestration script:
   ```bash
   python bot.py
   ```

### Cloud Deployment

This application is designed to be compatible with PaaS providers like Heroku, Render, and Koyeb.

1. Ensure the `Procfile` is present in the repository root. It should typically contain:
   ```text
   web: python bot.py
   ```
2. In your cloud provider dashboard, define all required environment variables.
3. The platform will automatically inject a `$PORT` environment variable. The `aiohttp` server will bind to this port to satisfy health checks.
4. Set the `URL` environment variable to your deployment's public web address so the keep-alive ping loop functions correctly.

## 7. Data Flow & Storage

The system relies on MongoDB primarily as a deduplication layer. Without this state management, the bot would repeatedly upload the same files to Telegram on every loop iteration, leading to API rate limits and channel flooding.

When a new torrent is successfully distributed, a document is inserted into the `Tamilmv` collection with the following structure:
- `file_name`: Sanitized string name of the file.
- `file_url`: The direct source URL of the file.
- `magnet`: Currently maps to the file URL.
- `size_mb`: Estimated size of the target content in megabytes.
- `category`: Parsed category (Movies, Series, or Dubbed).
- `upload_date`: ISO formatted string of the processing date.

## 8. Customization Guide

- Change scrape source: To point the scraper to a different base domain, update the `TMV_URL` environment variable. If the HTML structure is different, you must completely rewrite the `tmv_scraper` function logic in `tamilmv.py`.
- Adjust size limits: Modify the `SIZE_LIMIT_GB` environment variable to filter out large torrents early in the pipeline.
- Modify categories: Update the `categorize_content` function inside `tamilmv.py`. Adjust the regex rules and strings to match your desired classification logic.
- Change Telegram behavior: Edit the `send_torrent` async function in `tamilmv.py`. Here you can alter caption formatting, disable thumbnail usage, or modify the target chats and auto-reply commands.

## 9. Limitations

- Site Structure Dependency: The entire extraction logic is highly coupled to the specific DOM structure of TamilMV. Any layout, class name, or domain routing changes will cause the parser to fail silently.
- Single-Threaded Processing: Torrents are processed sequentially within the async loop. Large batches of new files will take time to process, without parallel download optimizations.
- No Retry Queue: Network timeouts during download or Telegram upload failures are caught and ignored. The script does not retry failed attempts, though they won't be marked as duplicates in the database.

## 10. Future Improvements

- Implementation of a robust message queue system (e.g., RabbitMQ, Redis) for handling job retries and failure backoffs.
- Refactoring the HTML parser to utilize a more flexible, schema-based engine to handle minor site updates gracefully.
- Enhancing logging functionality by replacing standard `print` statements with Python's `logging` module to allow for structured logs and level-based filtering.
- Development of a web-based UI dashboard over the existing `aiohttp` server for runtime monitoring and configuration overrides.
