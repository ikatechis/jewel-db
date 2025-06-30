# app/config.py
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = "sqlite:///./app.db"
SECRET_KEY = "your-secret-key"
DEBUG = True
