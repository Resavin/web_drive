from config import settings
from sqlmodel import create_engine

engine = create_engine(settings.database_url, echo=True)
