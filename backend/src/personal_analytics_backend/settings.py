import os
from dotenv import load_dotenv
import json

load_dotenv()   # load .env file in working directory if it exists



class PaBackendSettings:
    def __init__(self):
        # Backend-specific settings
        self.cache_timeout = 300

    # Environment-dependent settings as properties
    @property
    def database_url(self):
        db_url = os.getenv("PA_DATABASE_URL")
        if not db_url:
            raise ValueError("PA_DATABASE_URL environment variable is not set.")
        return db_url

    @property
    def allowed_origins(self):
        origins = json.loads(os.getenv("PA_ALLOWED_ORIGINS", "[]"))
        if not origins:
            raise ValueError("PA_ALLOWED_ORIGINS environment variable is not set. Please set a JSON array of allowed origins.")
        return origins


settings = PaBackendSettings()

