import os
from pathlib import Path
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://root:mypassword@127.0.0.1:27017/?authSource=admin",
)

ALLOWED_EXTENSIONS = [".pdf", ".txt"]

MAX_FILE_SIZE_MB = 10

UPLOAD_DIR = "uploads"

GEMINI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')