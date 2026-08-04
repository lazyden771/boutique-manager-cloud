"""
All environment-dependent settings live here. Locally this reads from a
.env file (see .env.example); in production (Railway) these come from
environment variables you set in the dashboard - same code, no changes needed.
"""

import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./boutique_cloud.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_SECRET_KEY_FILE = Path(__file__).resolve().parent.parent / ".generated_secret_key"


def _get_or_create_secret_key() -> str:
    """
    Zero-setup security: if SECRET_KEY isn't set as a real environment
    variable (e.g. on Railway, where you're expected to set one), a
    random key is generated once and cached in a local file, instead of
    falling back to a fixed insecure default. This means a forgotten
    setup step degrades to "a random key nobody chose", not "the same
    publicly-known key every install on earth shares" - the actual
    security-relevant difference. On Railway this file lives in ephemeral
    storage, so setting a real SECRET_KEY there is still the right move
    (a restart could otherwise invalidate everyone's login token) - but
    local development and a first run just work with no manual step.
    """
    env_value = os.getenv("SECRET_KEY")
    if env_value:
        return env_value

    if _SECRET_KEY_FILE.exists():
        return _SECRET_KEY_FILE.read_text().strip()

    key = secrets.token_hex(32)
    try:
        _SECRET_KEY_FILE.write_text(key)
    except OSError:
        pass  # read-only filesystem (some hosts) - key just won't persist across restarts
    return key


SECRET_KEY = _get_or_create_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days - a shop owner shouldn't
# have to log back in every day on their own phone/PC.

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
