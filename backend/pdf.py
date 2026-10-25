from urllib.parse import urlparse

from .template import renderizar_html

HOSTS_PERMITIDOS = (".dzcdn.net", ".deezer.com")
TIMEOUT_IMAGEM = 8


def _checar_url(url: str) -> None:
    partes = urlparse(url)
    host = partes.hostname or ""
    
    if partes.scheme != "https" or not host.endswith(HOSTS_PERMITIDOS):
        raise ValueError(f"URL bloqueada: {url}")


def _criar_fetcher():
    try:
        from weasyprint.urls import URLFetcher
    except ImportError:
        URLFetcher = None

    if URLFetcher is not None:
        class FetcherDeezer(URLFetcher):
            def fetch(self, url, headers=None):
                _checar_url(url)
                return super().fetch(url, headers)

        return FetcherDeezer(timeout=TIMEOUT_IMAGEM, allowed_protocols=("https",))

    from weasyprint import default_url_fetcher

    def fetcher(url, *args, **kwargs):
        _checar_url(url)
        return default_url_fetcher(url, *args, **kwargs)

    return fetcher


def gerar_pdf(carta: dict) -> bytes:
    from weasyprint import HTML  
    
    return HTML(string=renderizar_html(carta), url_fetcher=_criar_fetcher()).write_pdf()