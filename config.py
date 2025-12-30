import os
from pathlib import Path

# Default to ./data/worklist.db relative to project root
# Can be overridden with environment variable
BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.environ.get('WORKLIST_DATA_DIR', BASE_DIR / 'data'))
DATA_DIR.mkdir(exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATA_DIR / 'worklist.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
