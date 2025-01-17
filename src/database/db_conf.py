from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conf import get_settings

DB_CHOICES = {
    "sqlite": f"sqlite:///./{get_settings().db_name}",
    "postgresql": f"postgresql://{get_settings().db_username}:{get_settings().db_password}@{get_settings().db_name}/db",
}

DATABASE_URL = DB_CHOICES[get_settings().which_db]

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=0)

SessionLocal = sessionmaker(engine)
