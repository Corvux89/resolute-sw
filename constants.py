import os
import json

WEB_DEBUG = os.environ.get("DEBUG", False)
SECRET_KEY = os.environ.get("SECRET_KEY", "")
DB_URI = os.environ.get("DATABASE_URI", "")
LIMIT = os.environ.get("LIMIT", 1000)
CACHE_TIMEOUT = os.environ.get("CACHE_TIMEOUT", 300)

# Discord Setup
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "")
DISCORD_SECRET_KEY = os.environ.get("DISCORD_CLIENT_SECRET", "")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
DISCORD_ADMINS = json.loads(os.environ.get("DISCORD_ADMIN_USERS", []))
DISCORD_GUILD_ID = os.environ.get("DISCORD_GUILD_ID")

BOT_API_URL = os.environ.get("BOT_API_URL", "")
BOT_API_AUTH_TOKEN = os.environ.get("BOT_API_AUTH_TOKEN", "")

if WEB_DEBUG:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
