# backend/src/personal_analytics/database.py
# backend/src/personal_analytics/database.py
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection. You should set DATABASE_URL in your environment or in a <repo>/backend/.env file, with a line like:
#    DATABASE_URL=postgresql://analytics_user:personal_analytics_password@localhost:5432/personal_analytics
# You will need to run the setup_db.sh script once to create the database and user.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://analytics_user:personal_analytics_password@localhost:5432/personal_analytics"
)

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session