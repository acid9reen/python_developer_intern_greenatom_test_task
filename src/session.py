from dotenv import load_dotenv
import os
import sys
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL", None)

if not DATABASE_URL:
    sys.exit(
        "There is no DATABASE_URL in .env file or .env file does not exist.\n"
        "Exiting..."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    Yield sqlalchemy session object to interact with database.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
