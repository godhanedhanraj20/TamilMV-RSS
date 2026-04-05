import cloudscraper
import urllib.parse
from bs4 import BeautifulSoup

TMV_URL = "https://www.1tamilmv.land/"
scraper = cloudscraper.create_scraper()
query = "leo"
search_url = urllib.parse.urljoin(TMV_URL, f"index.php?/search/&q={urllib.parse.quote(query)}&type=forums_topic")

resp = scraper.get(search_url, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")

items = soup.find_all("h2", class_="ipsStreamItem_title")
if items:
    for item in items[:5]:
        a = item.find("a")
        if a:
            print(a.get_text(strip=True))
            print(a['href'])
else:
    print("No stream items found. Saving html.")
    with open("search.html", "w") as f:
        f.write(resp.text)
