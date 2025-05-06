import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "db.json"
ACCOUNTS_FILE = BASE_DIR / "accounts.txt"
PROXIES_FILE = BASE_DIR / "proxies.txt"


# Initialize bot and dispatcher
TOKEN = os.getenv("BOT_TOKEN")  # Load token from .env
PARSING_INTERVAL_SEC = os.getenv("PARSING_INTERVAL_SEC")
