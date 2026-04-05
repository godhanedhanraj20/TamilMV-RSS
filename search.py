import re
import asyncio
import urllib.parse
import cloudscraper
from bs4 import BeautifulSoup
from configs import TMV_URL

def _sync_search(query: str) -> list:
    scraper = cloudscraper.create_scraper()
    search_url = urllib.parse.urljoin(TMV_URL, f"index.php?/search/&q={urllib.parse.quote(query)}&type=forums_topic")

    try:
        resp = scraper.get(search_url, timeout=15)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        seen_links = set()

        # Look for links containing "topic"
        for a in soup.find_all("a", href=True):
            href = a['href']
            # Basic validation to ensure it's a topic link
            if "topic/" in href and "&do=findComment" in href:
                # Clean up URL to point to topic, not the specific comment if possible
                topic_url = href.split("&do=findComment")[0]

                title = a.get_text(strip=True)
                # Skip short texts like "1 reply"
                if len(title) < 10 or title.lower().endswith("replies") or title.lower().endswith("reply"):
                    continue

                if topic_url in seen_links:
                    continue
                seen_links.add(topic_url)

                # Attempt to extract size from title if present
                size_match = re.search(r"(\d+(\.\d+)?)\s*(gb|mb)", title, re.I)
                size_str = size_match.group(0) if size_match else "N/A"

                # Clean title (optional, could just leave as is since it describes the post)
                clean_title = re.sub(r'\s+', ' ', title).strip()

                results.append({
                    "title": clean_title,
                    "size": size_str,
                    "link": topic_url
                })

                if len(results) >= 7:
                    break

        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

async def search_tamilmv(query: str) -> list:
    """
    Search TamilMV asynchronously.
    Returns a list of dictionaries with title, size, and link.
    """
    return await asyncio.to_thread(_sync_search, query)
