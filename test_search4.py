import cloudscraper
import urllib.parse
from bs4 import BeautifulSoup

TMV_URL = "https://www.1tamilmv.land/"
scraper = cloudscraper.create_scraper()
query = "leo 2023"
search_url = urllib.parse.urljoin(TMV_URL, f"index.php?/search/&q={urllib.parse.quote(query)}&type=forums_topic")

resp = scraper.get(search_url, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")

items = soup.find_all("div", class_="ipsDataItem")
if items:
    for item in items[:5]:
        print(item.text.strip())
else:
    print("Checking 'a' tags with 'topic'")
    for a in soup.find_all("a", href=True):
        if "topic" in a["href"]:
            print(a.get_text(strip=True))
            print(a['href'])
            print("---")
