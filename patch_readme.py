with open("README.md", "r") as f:
    content = f.read()

new_components = """### Component-Level Architecture

The project follows a modular, package-based directory structure:

- `bot.py` (Root): The orchestrator. Initializes the Pyrogram client session, manages the `aiohttp` web server, runs the periodic async scraping loops (`tamilmv` & `skymovies`), handles interactive commands like `/search`, and manages the keep-alive ping thread.
- `scrapers/tamilmv.py`: The torrent pipeline engine. Parses DOM structures, downloads `.torrent` files, and dispatches them via Telegram.
- `scrapers/skymovies.py`: The streaming pipeline engine. Extracts multi-host direct download links (GoFile, Streamtape, etc.), groups them logically, and constructs structured Telegram posts.
- `scrapers/search.py`: The standalone query engine. Enables non-blocking, on-demand searches against TamilMV.
- `database/database.py`: The deduplication layer. Manages the connection pool to MongoDB and exposes primitives for tracking state across the `Tamilmv` and `Skymovies` collections.
- `config/configs.py`: The configuration layer. Maps process environment variables to typed Python constants utilized across the system.
- `tests/`: Contains the complete `pytest` suite for unit and integration testing."""

content = content.replace("### Component-Level Architecture\n\n- `bot.py`: The orchestrator. Initializes the Pyrogram client session, manages the `aiohttp` web server, runs the periodic async scraping loops (`tamilmv` & `skymovies`), handles interactive commands like `/search`, and manages the keep-alive ping thread.\n- `tamilmv.py`: The torrent pipeline engine. Parses DOM structures, downloads `.torrent` files, and dispatches them via Telegram.\n- `skymovies.py`: The streaming pipeline engine. Extracts multi-host direct download links (GoFile, Streamtape, etc.), groups them logically, and constructs structured Telegram posts.\n- `search.py`: The standalone query engine. Enables non-blocking, on-demand searches against TamilMV.\n- `database.py`: The deduplication layer. Manages the connection pool to MongoDB and exposes primitives for tracking state across the `Tamilmv` and `Skymovies` collections.\n- `configs.py`: The configuration layer. Maps process environment variables to typed Python constants utilized across the system.", new_components)

# Also update the startup phase steps to reflect new paths
content = content.replace("1. Load config: `configs.py`", "1. Load config: `config/configs.py`")
content = content.replace("2. Connect MongoDB: `database.py`", "2. Connect MongoDB: `database/database.py`")

with open("README.md", "w") as f:
    f.write(content)
