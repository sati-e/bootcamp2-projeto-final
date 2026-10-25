import json
import mimetypes
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from . import cartas, config, deezer, storage

CARTA_RE = re.compile(r"^/api/cartas/([^/]+)(/pdf)?$")


class Handler(BaseHTTPRequestHandler):
    server_version = "CartasComTrilha/1.0"

    def _enviar(self, status, corpo: bytes, tipo: str, cabecalhos: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("X-Content-Type-Options", "nosniff")

        for k, v in (cabecalhos or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, status, dados, cabecalhos: dict | None = None):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self._enviar(status, corpo, "application/json; charset=utf-8", cabecalhos)

    def _erro(self, status, mensagem):
        self._json(status, {"erro": mensagem})

    def _ler_json(self):
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            tamanho = -1

        if tamanho <= 0:
            raise cartas.ErroValidacao("Corpo vazio.")
        
        if tamanho > config.MAX_CORPO_BYTES:
            raise cartas.ErroValidacao("Corpo grande demais.")
        
        try:
            return json.loads(self.rfile.read(tamanho).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise cartas.ErroValidacao("JSON inválido.")

    def _url_base(self) -> str:
        if config.BASE_URL:
            return config.BASE_URL
        
        return f"http://{self.headers.get('Host') or f'localhost:{config.PORT}'}"

    def do_GET(self):
        url = urlparse(self.path)
        caminho = url.path

        if caminho == "/health":
            return self._json(HTTPStatus.OK, {"status": "ok"})

        if caminho == "/api/musicas":
            termo = parse_qs(url.query).get("q", [""])[0]
            
            try:
                return self._json(HTTPStatus.OK, {"resultados": deezer.buscar_musicas(termo)})
            except deezer.ErroDeezer as exc:
                return self._erro(HTTPStatus.BAD_GATEWAY, str(exc))

        m = CARTA_RE.match(caminho)
        
        if m:
            carta_id, quer_pdf = m.group(1), bool(m.group(2))
            
            if quer_pdf:
                baixar = parse_qs(url.query).get("download", ["0"])[0] == "1"
                return self._servir_pdf(carta_id, baixar)
            
            carta = cartas.buscar_carta(carta_id)
            if carta is None:
                return self._erro(HTTPStatus.NOT_FOUND, "Carta não encontrada.")
            
            return self._json(HTTPStatus.OK, carta, {"Cache-Control": "no-store"})

        return self._servir_estatico(caminho)

    def _servir_pdf(self, carta_id, baixar: bool):
        pdf = storage.carregar_pdf(carta_id)
        
        if pdf is None:
            return self._erro(HTTPStatus.NOT_FOUND, "Carta não encontrada.")
        
        modo = "attachment" if baixar else "inline"
        self._enviar(HTTPStatus.OK, pdf, "application/pdf",
                     {"Content-Disposition": f'{modo}; filename="carta-{carta_id}.pdf"'})

    def _servir_estatico(self, caminho):
        raiz = config.FRONTEND_DIR.resolve()
        relativo = unquote(caminho).lstrip("/") or "index.html"
        alvo = (raiz / relativo).resolve()
        
        if not alvo.is_relative_to(raiz) or not alvo.is_file():
            return self._erro(HTTPStatus.NOT_FOUND, "Não encontrado.")
        
        tipo = mimetypes.guess_type(alvo.name)[0] or "application/octet-stream"
        if tipo.startswith("text/") or tipo in ("application/javascript", "application/json"):
            tipo += "; charset=utf-8"
        
        self._enviar(HTTPStatus.OK, alvo.read_bytes(), tipo)

    def do_POST(self):
        if urlparse(self.path).path != "/api/cartas":
            return self._erro(HTTPStatus.NOT_FOUND, "Não encontrado.")
        
        try:
            carta = cartas.criar_carta(self._ler_json())
        
        except cartas.ErroValidacao as exc:
            return self._erro(HTTPStatus.BAD_REQUEST, str(exc))
        
        except deezer.ErroDeezer as exc:
            return self._erro(HTTPStatus.BAD_GATEWAY, str(exc))
        
        except Exception as exc:  # falha ao gerar o PDF, disco etc.
            self.log_error("erro ao criar carta: %r", exc)
            return self._erro(HTTPStatus.INTERNAL_SERVER_ERROR, "Erro ao gerar a carta.")
        
        base = self._url_base()
        self._json(HTTPStatus.CREATED, {
            "id": carta["id"],
            "link": f"{base}/carta.html?id={carta['id']}",
            "pdf": f"{base}/api/cartas/{carta['id']}/pdf?download=1",
        })


def criar_servidor(host=config.HOST, porta=config.PORT) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, porta), Handler)


def main():
    servidor = criar_servidor()
    print(f"Servidor em http://{config.HOST}:{config.PORT}  (dados em {config.DATA_DIR})")
    try:
        servidor.serve_forever()
   
    except KeyboardInterrupt:
        print("\nEncerrando...")
    
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
