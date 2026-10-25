import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")

DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
FRONTEND_DIR = BASE_DIR / "frontend"

DEEZER_API = "https://api.deezer.com"
DEEZER_TIMEOUT = 8
LIMITE_RESULTADOS = 5

MAX_NOME = 80
MAX_TEXTO = 500
MAX_CORPO_BYTES = 64 * 1024
