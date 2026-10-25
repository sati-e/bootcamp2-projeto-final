(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const destinatario = $("destinatario");
  const remetente = $("remetente");
  const textoCarta = $("texto-carta");
  const escolhida = $("musica-escolhida");
  const capa = $("escolhida-capa");
  const titulo = $("escolhida-titulo");
  const artista = $("escolhida-artista");
  const audio = $("preview");
  const barra = $("progresso");
  const btnPlay = $("btn-play");

  function mostrar(el, visivel) {
    el.hidden = !visivel;
    el.style.display = visivel ? "" : "none";
  }

  function mostrarTexto(linhas) {
    textoCarta.replaceChildren();
    for (const linha of linhas) {
      const p = document.createElement("p");
      p.textContent = linha || "\u00a0";
      textoCarta.append(p);
    }
  }

  function falhar(mensagem) {
    destinatario.textContent = "";
    remetente.textContent = "";
    mostrarTexto([mensagem]);
    mostrar(escolhida, false);
  }

  function rotular(tocando) {
    btnPlay.textContent = tocando ? "Pausar" : "Tocar";
    btnPlay.setAttribute("aria-label", btnPlay.textContent);
  }

  btnPlay.addEventListener("click", () => {
    if (audio.paused) audio.play().catch(() => rotular(false));
    else audio.pause();
  });
  audio.addEventListener("play", () => rotular(true));
  audio.addEventListener("pause", () => rotular(false));
  audio.addEventListener("ended", () => {
    barra.value = 0;
    rotular(false);
  });
  audio.addEventListener("timeupdate", () => {
    if (audio.duration) barra.value = (audio.currentTime / audio.duration) * 100;
  });
  barra.addEventListener("input", () => {
    if (audio.duration) audio.currentTime = (barra.value / 100) * audio.duration;
  });

  function mostrarMusica(musica) {
    if (!musica) return mostrar(escolhida, false);

    titulo.textContent = musica.titulo;
    artista.textContent = musica.artista;
    if (musica.capa) {
      capa.src = musica.capa;
      capa.alt = `Capa de ${musica.titulo}`;
    } else {
      capa.removeAttribute("src");
    }
    mostrar(escolhida, true);

    if (musica.preview) {
      audio.src = musica.preview;
      rotular(false);
      
      audio.play().catch(() => rotular(false));
    } else {
      mostrar(barra, false);
      mostrar(btnPlay, false);
    }
  }

  async function carregar() {
    const id = new URLSearchParams(location.search).get("id");
    if (!id) return falhar("Link inválido: faltou o código da carta.");
    if (location.protocol === "file:") {
      return falhar("Abra o site pelo servidor (http://localhost:8000), não direto pelo arquivo.");
    }

    try {
      const resp = await fetch(`/api/cartas/${encodeURIComponent(id)}`);
      const carta = await resp.json().catch(() => ({}));
      if (resp.status === 404) return falhar("Carta não encontrada.");
      if (!resp.ok) return falhar(carta.erro || "Não foi possível abrir a carta.");

      destinatario.textContent = carta.para;
      remetente.textContent = carta.de;
      mostrarTexto(carta.texto.split(/\r?\n/));
      document.title = `Uma carta para ${carta.para}`;
      mostrarMusica(carta.musica);
    } catch {
      falhar("Não consegui falar com o servidor.");
    }
  }

  carregar();
})();