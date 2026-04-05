with open("database.py", "a") as f:
    f.write("""

# ---------- Skymovies Entry Helper ----------
skymovies_collection = db["Skymovies"]

async def already_sent(detail_url: str):
    result = await skymovies_collection.find_one({"detail_url": detail_url})
    return True if result else False

async def mark_as_sent(detail_url, movie_title, size, sent_time, google_drive_links, all_server_links, listing_title):
    try:
        await skymovies_collection.insert_one({
            "detail_url": detail_url,
            "movie_title": movie_title,
            "size": size,
            "sent_time": sent_time,
            "google_drive_links": google_drive_links,
            "all_server_links": all_server_links,
            "listing_title": listing_title,
            "upload_date": datetime.date.today().isoformat()
        })
        print(f"💾 Added Skymovies to DB: {movie_title}")
    except Exception as e:
        print(f"⚠️ DB insert failed for Skymovies {movie_title}: {e}")
""")
