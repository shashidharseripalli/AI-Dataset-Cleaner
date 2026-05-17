import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Prefer DATABASE_URL from environment; fall back to a local sqlite file for development
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
	base = Path(__file__).resolve().parent.parent
	DATABASE_URL = f"sqlite:///{base / 'dev.db'}"