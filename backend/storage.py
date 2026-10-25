import json
import re
import secrets
from pathlib import Path

from . import config

ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,32}$")


def _pastas(data_dir: Path | None = None) -> tuple[Path, Path]:
    raiz = Path(data_dir or config.DATA_DIR)
    cartas, pdfs = raiz / "cartas", raiz / "pdfs"
    cartas.mkdir(parents=True, exist_ok=True)
    pdfs.mkdir(parents=True, exist_ok=True)
    return cartas, pdfs


def novo_id() -> str:
    return secrets.token_urlsafe(12)


def id_valido(carta_id: str) -> bool:
    return bool(ID_RE.match(carta_id))


def salvar_carta(carta_id: str, carta: dict, pdf: bytes, data_dir: Path | None = None) -> None:
    cartas, pdfs = _pastas(data_dir)
    (pdfs / f"{carta_id}.pdf").write_bytes(pdf)
    (cartas / f"{carta_id}.json").write_text(
        json.dumps(carta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def carregar_carta(carta_id: str, data_dir: Path | None = None) -> dict | None:
    if not id_valido(carta_id):
        return None
    
    caminho = _pastas(data_dir)[0] / f"{carta_id}.json"
    
    if not caminho.exists():
        return None
    
    return json.loads(caminho.read_text(encoding="utf-8"))


def carregar_pdf(carta_id: str, data_dir: Path | None = None) -> bytes | None:
    if not id_valido(carta_id):
        return None
    
    caminho = _pastas(data_dir)[1] / f"{carta_id}.pdf"
    
    return caminho.read_bytes() if caminho.exists() else None
