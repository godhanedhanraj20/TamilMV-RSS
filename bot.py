import asyncio, threading, time, requests
from aiohttp import web

from pyrogram import Client, idle, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.configs import API_ID, API_HASH, USER_SESSION, PORT, URL, SCRAPE_INTERVAL, PING_INTERVAL
from scrapers.tamilmv import tmv_scraper
from scrapers.search import search_tamilmv
from scrapers.skymovies import start_skymovies_scraper


User = Client("User", api_id=API_ID, api_hash=API_HASH, session_string=USER_SESSION)

# ---------- Bot Handlers ----------
@User.on_message(filters.command("search"))
async def handle_search(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /search <movie or series name>")
        return

    query = " ".join(message.command[1:])
    msg = await message.reply_text(f"🔍 Searching for `{query}`...")

    try:
        results = await search_tamilmv(query)

        if not results:
            await msg.edit_text("No results found.")
            return

        text = "**Top Results:**\n\n"
        for i, res in enumerate(results, 1):
            title = res['title']
            if len(title) > 60:
                title = title[:57] + "..."
            text += f"**{i}.** {title}\n"
            text += f"Size: {res['size']}\n"
            text += f"Link: {res['link']}\n\n"

        # Optional: Add inline button for the first result just as an example,
        # or just a general button. But keeping it simple text as requested is safest.
        # The prompt asked for optional inline buttons to open link, we can do it for top results
        # but telegram limits inline keyboard to certain size. So let's add buttons for the first few.
        buttons = []
        for i, res in enumerate(results[:5], 1):
            buttons.append([InlineKeyboardButton(f"Open Result {i}", url=res['link'])])

        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

        await msg.edit_text(text, disable_web_page_preview=True, reply_markup=reply_markup)

    except Exception as e:
        print(f"Search handler error: {e}")
        await msg.edit_text("Search failed. Try again later.")

# ---------- Keep-alive Ping ----------

def ping_loop():
    while True:
        try:
            r = requests.get(URL, timeout=30)
            print("🍁 Ping successful" if r.status_code == 200 else f"👹 Ping failed: {r.status_code}")
        except Exception as e:
            print(f"❌ Ping exception: {e}")
        time.sleep(PING_INTERVAL)

threading.Thread(target=ping_loop, daemon=True).start()

# ---------- TamilMV Scraper Loop ----------
async def main_loop():
    while True:
        print("🌀 Starting TamilMV scraping...")
        await tmv_scraper(User)
        await start_skymovies_scraper(User)
        await asyncio.sleep(SCRAPE_INTERVAL)

# ---------- Web server ----------
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root(request):
    return web.json_response("TamilMV RSS running ✅")

async def start_server():
    app = web.Application(client_max_size=30_000_000)
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# ---------- Startup ----------
async def start_bot():
    await User.start()
    user = await User.get_me()
    print(f"✅ User logged in: @{user.username}")
    asyncio.create_task(main_loop())
    await start_server()
    await idle()
    await User.stop()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(start_bot())
    except KeyboardInterrupt:
        print("🛑 Bot stopped manually.")
