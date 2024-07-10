import os
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
PORT = os.getenv("FASTAPI_PORT", 8000)
DEBUG = os.getenv("FASTAPI_DEBUG", True)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:example@db/mydatabase")
ROOT_DIRECTORY = os.getenv("ROOT_DIRECTORY", "/web_drive/data")
os.makedirs(ROOT_DIRECTORY, exist_ok=True)
os.chdir(ROOT_DIRECTORY)
