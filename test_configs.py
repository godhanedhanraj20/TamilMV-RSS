with open("configs.py", "a") as f:
    f.write("""

# Skymovies settings
SKYMOVIES_CHANNEL_ID = int(os.getenv("SKYMOVIES_CHANNEL_ID", "0"))
SKYMOVIES_URL = os.getenv("SKYMOVIES_URL", "https://skymovieshd.credit/")
""")
