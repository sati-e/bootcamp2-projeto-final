from datetime import datetime, timezone

from . import config, deezer, storage
from .pdf import gerar_pdf


class ErroValidacao(ValueError):
    pass

def _texto(payload: dict, campo: str, maximo: int, obrigatorio: bool = False) -> str:
    valor = payload.get(campo)
    
    if valor is None:
        valor = ""
    
    if not isinstance(valor, str):
        raise ErroValidacao(f"O campo '{campo}' deve ser texto.")
    
    valor = valor.strip()
    if obrigatorio and not valor:
        raise ErroValidacao(f"O campo '{campo}' é obrigatório.")
    
    if len(valor) > maximo:
        raise ErroValidacao(f"O campo '{campo}' excede {maximo} caracteres.")
    
    return valor


def validar(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ErroValidacao("Corpo da requisição inválido.")
    
    musica_id = payload.get("musica_id")
    
    if musica_id in (None, ""):  # o input hidden do front vai vazio se não houver música
        musica_id = None
    else:
        try:
            musica_id = int(musica_id)
        except (TypeError, ValueError):
            raise ErroValidacao("O campo 'musica_id' deve ser um número.")
    
        if musica_id <= 0:
            raise ErroValidacao("O campo 'musica_id' é inválido.")
    
    return {
        "para": _texto(payload, "para", config.MAX_NOME, obrigatorio=True),
        "texto": _texto(payload, "texto", config.MAX_TEXTO, obrigatorio=True),
        "de": _texto(payload, "de", config.MAX_NOME),
        "musica_id": musica_id,
    }


def criar_carta(payload: dict, data_dir=None) -> dict:
    dados = validar(payload)
    musica = deezer.obter_musica(dados["musica_id"]) if dados["musica_id"] else None
    carta = {
        "para": dados["para"],
        "texto": dados["texto"],
        "de": dados["de"],
        "musica": musica,
        "criada_em": datetime.now(timezone.utc).isoformat(),
    }

    carta_id = storage.novo_id()
    storage.salvar_carta(carta_id, carta, gerar_pdf(carta), data_dir)

    return {"id": carta_id, **carta}


def buscar_carta(carta_id: str, data_dir=None) -> dict | None:
    carta = storage.carregar_carta(carta_id, data_dir)
    if carta is None:
        return None
    musica = carta.get("musica")

    if musica:
        try:
            atual = deezer.obter_musica(musica["id"])
            musica = {**musica, "preview": atual["preview"], "capa": atual["capa"] or musica["capa"]}
        except deezer.ErroDeezer:
            pass
        
        carta = {**carta, "musica": musica}

    return {"id": carta_id, **carta}
