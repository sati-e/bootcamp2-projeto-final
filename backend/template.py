"""Monta o HTML/CSS da carta (mesmo layout da página) que vira PDF."""
from html import escape

CSS = """
@page { size: 200mm 170mm; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  width: 200mm; height: 170mm; background: #e6d8c1;
  font-family: "Montserrat", "Helvetica", "Arial", sans-serif; color: #4a3b2a;
}
.papel {
  position: absolute; left: 8mm; top: 8mm; right: 8mm; bottom: 8mm;
  background: #f7efdf; padding: 9mm 10mm;
}
.rotulo { font-family: "Great Vibes", "Snell Roundhand", "URW Chancery L", cursive;
          font-style: italic; font-size: 24pt; color: #3a2f22; }
.linha { display: flex; align-items: baseline; border-bottom: 0.3mm solid #b9ad98; }
.valor { flex: 1; font-family: "Caveat", "Comic Sans MS", cursive;
         font-size: 13pt; padding-left: 4mm; color: #6b5a44; }
.texto {
  height: 74mm; overflow: hidden;
  font-family: "Caveat", "Comic Sans MS", cursive; font-size: 12pt; color: #6b5a44;
  line-height: 8.2mm; white-space: pre-wrap; overflow-wrap: anywhere;
  background-image: repeating-linear-gradient(
    to bottom, transparent 0, transparent 7.9mm, #b9ad98 7.9mm, #b9ad98 8.2mm);
}
.rodape { position: absolute; left: 10mm; right: 10mm; bottom: 9mm; height: 26mm; }
.musica { position: absolute; left: 0; top: 0; width: 95mm; }
.capa { width: 24mm; height: 24mm; background: #d9d9d9; float: left; margin-right: 6mm; }
.capa img { width: 100%; height: 100%; display: block; }
.musica .titulo { font-weight: bold; font-size: 11pt; margin-top: 2mm; }
.musica .artista { font-size: 8pt; margin-top: 1mm; }
.musica a { display: inline-block; margin-top: 2.5mm; font-size: 7.5pt; color: #7a2433;
            text-decoration: none; border-bottom: 0.2mm solid #7a2433; }
.de { position: absolute; right: 0; bottom: 0; width: 70mm; display: flex; align-items: baseline; }
.de .valor { border-bottom: 0.3mm solid #b9ad98; padding-left: 3mm; }
"""


def _bloco_musica(musica: dict | None) -> str:
    if not musica:
        return ""
    if musica.get("capa"):
        capa = f'<div class="capa"><img src="{escape(musica["capa"], quote=True)}"></div>'
    else:
        capa = '<div class="capa"></div>'
    link = escape(musica.get("link", ""), quote=True)
    return (
        '<div class="musica">' + capa +
        f'<div class="titulo">{escape(musica.get("titulo", ""))}</div>'
        f'<div class="artista">{escape(musica.get("artista", ""))}</div>'
        f'<a href="{link}">Ouvir no Deezer</a></div>'
    )


def renderizar_html(carta: dict) -> str:
    """carta: {para, texto, de, musica|None}. Todo texto do usuário é escapado."""
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Carta com trilha</title>
<style>{CSS}</style></head>
<body><div class="papel">
  <div class="linha"><span class="rotulo">Para</span>
    <span class="valor">{escape(carta.get("para", ""))}</span></div>
  <div class="texto">{escape(carta.get("texto", ""))}</div>
  <div class="rodape">
    {_bloco_musica(carta.get("musica"))}
    <div class="de"><span class="rotulo">De</span>
      <span class="valor">{escape(carta.get("de", ""))}</span></div>
  </div>
</div></body></html>"""
