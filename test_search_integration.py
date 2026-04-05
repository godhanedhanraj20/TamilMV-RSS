import asyncio
from search import search_tamilmv

async def main():
    results = await search_tamilmv("leo 2023")
    for r in results:
        print(f"Title: {r['title'][:50]}...\nSize: {r['size']}\nLink: {r['link']}\n")

asyncio.run(main())
