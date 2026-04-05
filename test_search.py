import cloudscraper
import urllib.parse
from bs4 import BeautifulSoup
from configs import TMV_URL

scraper = cloudscraper.create_scraper()
query = "leo"
search_url = urllib.parse.urljoin(TMV_URL, f"index.php?/search/&q={urllib.parse.quote(query)}&quick=1")

try:
    print(f"Searching: {search_url}")
    resp = scraper.get(search_url, timeout=15)
    print(f"Status Code: {resp.status_code}")
    # print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")
