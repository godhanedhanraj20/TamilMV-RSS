import asyncio, threading, time, requests
from aiohttp import web

from pyrogram import Client, idle, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.configs import API_ID, API_HASH, USER_SESSION, PORT, URL, SCRAPE_INTERVAL, PING_INTERVAL, ADMIN_ID
from scrapers.tamilmv import tmv_scraper
from scrapers.search import search_tamilmv
from scrapers.skymovies import start_skymovies_scraper



# Global State
bot_paused = False

def is_admin(user_id):
    return user_id == ADMIN_ID if ADMIN_ID else True  # If no ADMIN_ID set, allow anyone for now (or False, but True for easy testing)

User = Client("User", api_id=API_ID, api_hash=API_HASH, session_string=USER_SESSION)



# ---------- Bot Handlers ----------
@User.on_message(filters.command("start"))
async def start_cmd(client, message):
    text = (
        "🤖 **Bot is running**\n\n"
        "**Admin Commands**\n"
        "• `/on` — Resume bot scraping loop\n"
        "• `/off` — Pause bot scraping loop\n"
        "• `/process <url>` — Process a single URL manually\n"
        "• `/ping` — Quick check the bot is receiving commands\n\n"
        "**User Commands**\n"
        "• `/search <query>` — Search TamilMV titles"
    )
    await message.reply_text(text)

@User.on_message(filters.command("ping"))
async def ping_cmd(client, message):
    await message.reply_text("pong")

@User.on_message(filters.command("on"))
async def resume_bot(client, message):
    global bot_paused
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ You are not authorized to use this command.")
        return
    bot_paused = False
    await message.reply_text("▶️ Bot Resumed.")

@User.on_message(filters.command("off"))
async def pause_bot(client, message):
    global bot_paused
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ You are not authorized to use this command.")
        return
    bot_paused = True
    await message.reply_text("⛔ Bot Paused.")

@User.on_message(filters.command("process"))
async def process_cmd(client, message):
    if not is_admin(message.from_user.id):
        await message.reply_text("❌ You are not authorized to use this command.")
        return
    args = message.command
    if len(args) < 2:
        await message.reply_text("❌ Correct usage: `/process <details_url>`")
        return

    input_url = args[1].strip()
    if not input_url.lower().startswith(("http://", "https://")):
        input_url = f"https://{input_url}"

    msg = await message.reply_text("ℹ️ Processing, please wait...")

    try:
        if "skymovies" in input_url.lower():
            # fetch the page manually and pass to scraper
            from scrapers.skymovies import fetch_html, scrape_skymovies
            html_content = await asyncio.to_thread(fetch_html, input_url)
            if html_content:
                # false flag means do not skip if already sent (force process)
                movies = await scrape_skymovies(html_content, client, skip_already_sent=False)
                if movies:
                    await msg.edit_text(f"✅ Processed {len(movies)} Skymovies links manually.")
                else:
                    await msg.edit_text("❌ No Skymovies details found.")
            else:
                await msg.edit_text("❌ Failed to fetch Skymovies page.")

        elif "tamilmv" in input_url.lower():
            # For tamilmv we need to extract from topic page.
            # Using search logic or custom block. We'll leave it as a placeholder or basic implement:
            await msg.edit_text("❌ Manual processing for TamilMV specific topic URLs is not fully supported yet in this command.")

        else:
            await msg.edit_text("❌ Unsupported URL domain. Try Skymovies links.")
    except Exception as e:
        await msg.edit_text(f"❌ Error processing: {e}")

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
    global bot_paused
    while True:
        if not bot_paused:
            print("🌀 Starting scraping loops...")
            await tmv_scraper(User)
            await start_skymovies_scraper(User)
        else:
            print("⏸ Bot is paused. Skipping scrape cycle.")
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
