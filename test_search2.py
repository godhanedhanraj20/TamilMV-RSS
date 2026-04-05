import cloudscraper
import urllib.parse
from bs4 import BeautifulSoup

TMV_URL = "https://www.1tamilmv.land/"
scraper = cloudscraper.create_scraper()
query = "leo"
search_url = urllib.parse.urljoin(TMV_URL, f"index.php?/search/&q={urllib.parse.quote(query)}&quick=1")

resp = scraper.get(search_url, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")

# Find search results. Usually they have class something like cStreamItem or ipsDataItem
items = soup.find_all("li", class_="ipsStreamItem")
if not items:
    items = soup.find_all("li", class_="ipsDataItem")
if not items:
    # let's look at a tags directly
    print("Looking at links")
    for a in soup.find_all("a", href=True)[:15]:
        print(a.get_text(strip=True), a['href'])
else:
    for item in items[:5]:
        print(item.text[:100])
