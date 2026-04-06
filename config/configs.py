# Coded by @SMDxTG - if Any Query Ask him Directly 

import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

# Telegram
API_ID = int(os.getenv("API_ID") or "0")
API_HASH = os.getenv("API_HASH", "")
USER_SESSION = os.getenv("USER_SESSION", "") # Use Pyrogram V2 String Session 
#if you don't have string Gen bot - use it my bot @SMD_StringBot

# Web
PORT = int(os.getenv("PORT") or "8080")
URL = os.getenv("URL", "") # Heroku or Koyeb Or Render Base Url 

# MongoDB
DATABASE_URL = os.getenv("DATABASE_URL", "") #Mongodb Url 
DATABASE_NAME = os.getenv("DATABASE_NAME", "") # example Cluster0

# TamilMV settings
TMV_URL = os.getenv("TMV_URL", "https://www.1tamilmv.land/")
TMV_TORRENT = int(os.getenv("TMV_TORRENT") or "0")
TMV_LEECH_GRP = int(os.getenv("TMV_LEECH_GRP") or "0")
TMV_MIRROR_GRP = int(os.getenv("TMV_MIRROR_GRP") or "0")
TMV_TORRENT_THUMB = os.getenv("TMV_TORRENT_THUMB", "https://i.ibb.co/7dq7mMLp/photo-2025-10-18-16-42-28-7562603128038621216.jpg") #torrant Pic
BOT_TAG = os.getenv("BOT_TAG", "@SMD_BOTz") # File Prefix

# Internal
PING_INTERVAL = int(os.getenv("PING_INTERVAL") or "120")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL") or "300")  # 5 min
SIZE_LIMIT_GB = int(os.getenv("SIZE_LIMIT_GB") or 50)  # Default: 50 GB

# Skymovies settings
SKYMOVIES_CHANNEL_ID = int(os.getenv("SKYMOVIES_CHANNEL_ID") or "0")
SKYMOVIES_URL = os.getenv("SKYMOVIES_URL", "https://skymovieshd.credit/")

# Admin settings
ADMIN_ID = int(os.getenv("ADMIN_ID") or "0")
