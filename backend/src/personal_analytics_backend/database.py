
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()   # load .env file in working directory if it exists

# PostgreSQL connection. You should set DATABASE_URL in your environment or in a <repo>/backend/.env file, with a line like:
#    DATABASE_URL=postgresql://analytics_user:personal_analytics_password@localhost:5432/personal_analytics
# You will need to run the setup_db.sh script once to create the database and user.
DATABASE_URL = os.getenv("DATABASE_URL")

# Fail fast if DATABASE_URL is not set
if not DATABASE_URL:
    raise ValueError(
        "The DATABASE_URL environment variable is not set. Please create a .env file with format like:\n"
        "  DATABASE_URL=postgresql://analytics_user:your_password@localhost:5432/personal_analytics\n"
        "Or set it in your environment."
    )

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session