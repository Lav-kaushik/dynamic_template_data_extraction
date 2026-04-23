from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings , SettingsConfigDict

# __file__ is settings.py, parent is app_configs, parent is app, parent is root (workspace)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DOTENV = ROOT_DIR / ".env"

class AppSettings(BaseSettings):
    GROQ_API_KEY: str
    GOOGLE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=DOTENV)

def get_settings():
    return AppSettings()

