import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Prefer DATABASE_URL from environment; fall back to a local sqlite file for development
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
	base = Path(__file__).resolve().parent.parent
	DATABASE_URL = f"sqlite:///{base / 'dev.db'}"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
