with open("bot.py", "r") as f:
    content = f.read()

from_import = "from skymovies import start_skymovies_scraper"
if from_import not in content:
    content = content.replace("from search import search_tamilmv", f"from search import search_tamilmv\n{from_import}")

skymovies_task = "await start_skymovies_scraper(User)"
if skymovies_task not in content:
    content = content.replace("await tmv_scraper(User)", f"await tmv_scraper(User)\n        {skymovies_task}")

with open("bot.py", "w") as f:
    f.write(content)
