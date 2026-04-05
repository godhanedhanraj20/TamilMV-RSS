with open("bot.py", "r") as f:
    content = f.read()

import_patch = """from pyrogram import Client, idle, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configs import API_ID, API_HASH, USER_SESSION, PORT, URL, SCRAPE_INTERVAL, PING_INTERVAL
from tamilmv import tmv_scraper
from search import search_tamilmv"""

content = content.replace("from pyrogram import Client, idle", "")
content = content.replace("from configs import API_ID, API_HASH, USER_SESSION, PORT, URL, SCRAPE_INTERVAL, PING_INTERVAL\nfrom tamilmv import tmv_scraper", import_patch)

handler_patch = """
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
"""

content = content.replace('User = Client("User", api_id=API_ID, api_hash=API_HASH, session_string=USER_SESSION)\n\n# ---------- Keep-alive Ping ----------', handler_patch)

with open("bot.py", "w") as f:
    f.write(content)
