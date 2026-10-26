import base64
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

from backend import cartas, config, deezer, storage, template

MUSICA = {"id": 3135556, "titulo": "Harder <b>", "artista": "Daft Punk", "capa": "",
          "preview": "https://cdnt-preview.dzcdn.net/novo.mp3",
          "link": "https://www.deezer.com/track/3135556"}


class TemplateTests(unittest.TestCase):
    def test_escapa_html_do_usuario(self):
        html = template.renderizar_html({"para": "<script>x</script>", "texto": "oi & tchau",
                                         "de": "Ana", "musica": MUSICA})
        self.assertNotIn("<script>x</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("oi &amp; tchau", html)
        self.assertIn("Harder &lt;b&gt;", html)
        self.assertIn(MUSICA["link"], html)

    def test_sem_musica_nao_tem_bloco(self):
        html = template.renderizar_html({"para": "A", "texto": "m", "de": "B", "musica": None})
        self.assertNotIn('class="musica"', html)


class StorageTests(unittest.TestCase):
    def test_ida_e_volta_e_id_invalido(self):
        with tempfile.TemporaryDirectory() as d:
            cid = storage.novo_id()
            storage.salvar_carta(cid, {"a": 1}, b"%PDF-x", Path(d))
            self.assertEqual(storage.carregar_carta(cid, Path(d)), {"a": 1})
            self.assertEqual(storage.carregar_pdf(cid, Path(d)), b"%PDF-x")
            self.assertIsNone(storage.carregar_carta("../../etc/passwd", Path(d)))
            self.assertIsNone(storage.carregar_pdf("nao-existe-123456", Path(d)))


class ValidacaoTests(unittest.TestCase):
    def test_para_e_texto_obrigatorios(self):
        with self.assertRaises(cartas.ErroValidacao):
            cartas.validar({"texto": "oi"})
        with self.assertRaises(cartas.ErroValidacao):
            cartas.validar({"para": "Ana", "texto": "   "})

    def test_limites_e_tipos(self):
        base = {"para": "Ana", "texto": "oi"}
        with self.assertRaises(cartas.ErroValidacao):
            cartas.validar({**base, "texto": "x" * (config.MAX_TEXTO + 1)})
        with self.assertRaises(cartas.ErroValidacao):
            cartas.validar({**base, "de": 123})
        with self.assertRaises(cartas.ErroValidacao):
            cartas.validar({**base, "musica_id": "abc"})
        self.assertIsNone(cartas.validar({**base, "musica_id": ""})["musica_id"])
        self.assertEqual(cartas.validar({**base, "musica_id": "42"})["musica_id"], 42)


class DeezerTests(unittest.TestCase):
    def _resp(self, dados):
        m = mock.MagicMock()
        m.__enter__.return_value.read.return_value = json.dumps(dados).encode()
        return m

    def test_busca_normaliza(self):
        bruto = {"data": [{"id": 1, "title": "T", "link": "L", "preview": "P",
                           "artist": {"name": "A"}, "album": {"cover_medium": "C"}}]}
        with mock.patch("urllib.request.urlopen", return_value=self._resp(bruto)):
            self.assertEqual(deezer.buscar_musicas("x"),
                             [{"id": 1, "titulo": "T", "artista": "A", "capa": "C",
                               "preview": "P", "link": "L"}])

    def test_erro_do_deezer_vira_excecao(self):
        erro = {"error": {"type": "DataException", "message": "no data", "code": 800}}
        with mock.patch("urllib.request.urlopen", return_value=self._resp(erro)):
            with self.assertRaises(deezer.ErroDeezer):
                deezer.obter_musica(1)

    def test_busca_vazia_nao_chama_api(self):
        with mock.patch("urllib.request.urlopen") as m:
            self.assertEqual(deezer.buscar_musicas("  "), [])
            m.assert_not_called()


class BuscarCartaTests(unittest.TestCase):
    def test_renova_preview_e_cai_para_o_salvo_se_deezer_falhar(self):
        with tempfile.TemporaryDirectory() as d:
            antiga = {**MUSICA, "preview": "velho.mp3"}
            storage.salvar_carta("abcdefghij12", {"para": "A", "texto": "t", "de": "",
                                                  "musica": antiga}, b"%PDF", Path(d))
            with mock.patch("backend.deezer.obter_musica", return_value=MUSICA):
                self.assertEqual(cartas.buscar_carta("abcdefghij12", Path(d))["musica"]["preview"],
                                 MUSICA["preview"])
            with mock.patch("backend.deezer.obter_musica", side_effect=deezer.ErroDeezer("x")):
                self.assertEqual(cartas.buscar_carta("abcdefghij12", Path(d))["musica"]["preview"],
                                 "velho.mp3")
            self.assertIsNone(cartas.buscar_carta("naoexiste1234", Path(d)))


class ServidorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from backend import server
        cls.tmp = tempfile.TemporaryDirectory()
        cls.front = Path(cls.tmp.name) / "front"
        cls.front.mkdir()
        (cls.front / "index.html").write_text("<h1>home</h1>", encoding="utf-8")
        (cls.front / "carta.html").write_text("<h1>carta</h1>", encoding="utf-8")
        cls.patches = [
            mock.patch.object(config, "DATA_DIR", Path(cls.tmp.name) / "data"),
            mock.patch.object(config, "FRONTEND_DIR", cls.front),
            mock.patch("backend.cartas.gerar_pdf", return_value=b"%PDF-fake"),
            mock.patch("backend.deezer.obter_musica", return_value=MUSICA),
            mock.patch("backend.deezer.buscar_musicas", return_value=[MUSICA]),
        ]
        for p in cls.patches:
            p.start()
        cls.srv = server.criar_servidor("127.0.0.1", 0)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()
        for p in cls.patches:
            p.stop()
        cls.tmp.cleanup()

    def _post(self, corpo):
        req = urllib.request.Request(self.base + "/api/cartas", data=json.dumps(corpo).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_estaticos(self):
        with urllib.request.urlopen(self.base + "/") as r:
            self.assertIn(b"home", r.read())
        with urllib.request.urlopen(self.base + "/carta.html?id=abc") as r:
            self.assertIn(b"carta", r.read())

    def test_busca_devolve_resultados(self):
        with urllib.request.urlopen(self.base + "/api/musicas?q=daft") as r:
            self.assertEqual(json.loads(r.read())["resultados"][0]["artista"], "Daft Punk")

    def test_fluxo_completo(self):
        status, d = self._post({"para": "Ana", "texto": "Oi!", "de": "Bia", "musica_id": "3135556"})
        self.assertEqual(status, 201)
        self.assertEqual(d["link"], f"{self.base}/carta.html?id={d['id']}")
        with urllib.request.urlopen(self.base + f"/api/cartas/{d['id']}") as r:
            carta = json.loads(r.read())
            self.assertEqual(carta["para"], "Ana")
            self.assertEqual(carta["de"], "Bia")
            self.assertEqual(carta["musica"]["link"], MUSICA["link"])
            self.assertEqual(r.headers["Cache-Control"], "no-store")
        with urllib.request.urlopen(d["pdf"].replace("?download=1", "")) as r:
            self.assertEqual(r.headers["Content-Type"], "application/pdf")
            self.assertIn("inline", r.headers["Content-Disposition"])
        with urllib.request.urlopen(d["pdf"]) as r:
            self.assertIn("attachment", r.headers["Content-Disposition"])

    def test_sem_musica(self):
        status, d = self._post({"para": "Ana", "texto": "só texto", "musica_id": ""})
        self.assertEqual(status, 201)
        with urllib.request.urlopen(self.base + f"/api/cartas/{d['id']}") as r:
            self.assertIsNone(json.loads(r.read())["musica"])

    def test_validacao_400(self):
        status, d = self._post({"para": "", "texto": "x"})
        self.assertEqual(status, 400)
        self.assertIn("erro", d)

    def test_404_e_traversal(self):
        for caminho in ("/api/cartas/naoexiste12345", "/api/cartas/..%2f..%2fetc/pdf",
                        "/..%2f..%2fetc/passwd", "/nao-existe.html"):
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(self.base + caminho)
            self.assertEqual(ctx.exception.code, 404)


class PdfRealTests(unittest.TestCase):
    PNG = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
    CAPA_OK = "https://cdn-images.dzcdn.net/images/cover/x/250x250.jpg"

    def setUp(self):
        try:
            import weasyprint  # noqa: F401
            from weasyprint.urls import URLFetcher, URLFetcherResponse  # noqa: F401
        except Exception:
            self.skipTest("WeasyPrint (>=68) não instalado")
        self.carta = {"para": "Ana", "texto": "Olá, é um teste.\nLinha 2", "de": "Bia",
                      "musica": {**MUSICA, "capa": self.CAPA_OK}}

    def _resposta(self, url, *a, **k):
        from weasyprint.urls import URLFetcherResponse
        return URLFetcherResponse(url, body=self.PNG, headers={"Content-Type": "image/png"})

    def test_sem_capa(self):
        from backend.pdf import gerar_pdf
        pdf = gerar_pdf({**self.carta, "musica": {**MUSICA, "capa": ""}})
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_com_capa_do_deezer_baixa_e_embute_a_imagem(self):
        from backend.pdf import gerar_pdf
        with mock.patch("weasyprint.urls.URLFetcher.fetch", autospec=True,
                        side_effect=lambda self_, url, headers=None: self._resposta(url)) as m:
            pdf = gerar_pdf(self.carta)
        m.assert_called_once()
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn(b"/Subtype /Image", pdf)

    def test_capa_de_outro_host_e_bloqueada_mas_pdf_sai(self):
        from backend.pdf import gerar_pdf
        carta = {**self.carta, "musica": {**MUSICA, "capa": "https://evil.example/x.png"}}
        with mock.patch("weasyprint.urls.URLFetcher.fetch", autospec=True) as m:
            pdf = gerar_pdf(carta)
        m.assert_not_called()
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertNotIn(b"/Subtype /Image", pdf)

    def test_falha_de_rede_na_capa_nao_impede_o_pdf(self):
        from backend.pdf import gerar_pdf
        with mock.patch("weasyprint.urls.URLFetcher.fetch", autospec=True,
                        side_effect=OSError("sem rede")):
            pdf = gerar_pdf(self.carta)
        self.assertTrue(pdf.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()