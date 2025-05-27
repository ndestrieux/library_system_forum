from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conf import get_settings

DB_CHOICES = {
    "sqlite": f"sqlite:///./{get_settings().DB_NAME}",
    "postgresql": f"postgresql://{get_settings().DB_USERNAME}:{get_settings().DB_PASSWORD}@{get_settings().DB_HOST}/{get_settings().DB_NAME}",
}

DATABASE_URL = DB_CHOICES[get_settings().WHICH_DB]

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=0)

SessionLocal = sessionmaker(engine)
