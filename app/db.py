from sqlmodel import create_engine
from load_env import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
