import json
import urllib.error
import urllib.parse
import urllib.request

from . import config


class ErroDeezer(Exception):
    pass 

def _get(caminho: str, params: dict | None = None) -> dict:
    url = f"{config.DEEZER_API}{caminho}"
    
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "cartas-com-trilha/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=config.DEEZER_TIMEOUT) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ErroDeezer(f"Falha ao consultar o Deezer: {exc}") from exc
    
    if isinstance(dados, dict) and "error" in dados:
        raise ErroDeezer(str(dados["error"].get("message", "Erro do Deezer")))
    
    return dados


def _normalizar(faixa: dict) -> dict:
    album = faixa.get("album") or {}
    
    return {
        "id": faixa["id"],
        "titulo": faixa.get("title", ""),
        "artista": (faixa.get("artist") or {}).get("name", ""),
        "capa": album.get("cover_medium") or album.get("cover") or "",
        "preview": faixa.get("preview", ""),
        "link": faixa.get("link", ""),
    }


def buscar_musicas(termo: str, limite: int = config.LIMITE_RESULTADOS) -> list[dict]:
    termo = termo.strip()
    
    if not termo:
        return []
    
    dados = _get("/search", {"q": termo, "limit": limite})

    return [_normalizar(f) for f in dados.get("data", []) if "id" in f]


def obter_musica(musica_id: int) -> dict:
    return _normalizar(_get(f"/track/{int(musica_id)}"))
