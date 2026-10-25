(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);

  const form = $("form-carta");
  const busca = $("busca-musica");
  const lista = $("resultados");
  const musicaId = $("musica-id");
  const escolhida = $("musica-escolhida");
  const capa = $("escolhida-capa");
  const titulo = $("escolhida-titulo");
  const artista = $("escolhida-artista");
  const audio = $("preview");
  const barra = $("progresso");
  const btnPlay = $("btn-play");
  const botaoGerar = form.querySelector(".btn-gerar");
  const blocoLink = $("resultado-link");
  const campoLink = $("link");
  const btnCopiar = $("btn-copiar");

  function mostrar(el, visivel) {
    el.hidden = !visivel;
    el.style.display = visivel ? "" : "none";
  }

  function definirImagem(img, url, alt) {
    if (url) {
      img.src = url;
      img.alt = alt || "";
    } 
    else {
      img.removeAttribute("src");
      img.alt = "";
    }
  }

  const erro = document.createElement("p");
  erro.className = "erro";
  erro.setAttribute("role", "alert");
  erro.style.cssText = "color:#7a2433;margin:.6rem 0 0;font-size:.9rem";
  mostrar(erro, false);
  botaoGerar.after(erro);

  function mostrarErro(msg) {
    erro.textContent = msg;
    mostrar(erro, true);
  }

  function limparErro() {
    erro.textContent = "";
    mostrar(erro, false);
  }

  const MSG_ARQUIVO = "Abra o site pelo servidor (python -m backend.server → http://localhost:8000), não direto pelo arquivo.";

  function rotular(tocando) {
    btnPlay.textContent = tocando ? "Pausar" : "Tocar";
    btnPlay.setAttribute("aria-label", btnPlay.textContent);
  }

  btnPlay.addEventListener("click", () => {
    if (!audio.getAttribute("src")) return;
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

  function limparEscolha() {
    musicaId.value = "";
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    barra.value = 0;
    definirImagem(capa, "");
    mostrar(escolhida, false);
  }

  function escolher(musica, botao) {
    musicaId.value = musica.id;
    definirImagem(capa, musica.capa, `Capa de ${musica.titulo}`);
    titulo.textContent = musica.titulo;
    artista.textContent = musica.artista;
    barra.value = 0;
    mostrar(escolhida, true);

    if (musica.preview) {
      audio.src = musica.preview;
      mostrar(barra, true);
      mostrar(btnPlay, true);
      audio.play().catch(() => rotular(false));
    } 
    else {
      audio.removeAttribute("src");
      mostrar(barra, false);
      mostrar(btnPlay, false);
    }

    lista.querySelectorAll(".resultado").forEach((b) => {
      const ativo = b === botao;
      b.classList.toggle("selecionado", ativo);
      b.setAttribute("aria-pressed", String(ativo));
    });
  }

  function mensagemNaLista(texto) {
    lista.replaceChildren();

    const li = document.createElement("li");

    li.className = "mensagem";
    li.textContent = texto;

    lista.append(li);
  }

  function renderizar(resultados) {
    lista.replaceChildren();
    if (!resultados.length) return mensagemNaLista("Nenhuma música encontrada.");

    for (const m of resultados) {
      const li = document.createElement("li");
      const botao = document.createElement("button");
      botao.type = "button";
      botao.className = "resultado";
      botao.setAttribute("aria-pressed", String(String(m.id) === musicaId.value));
      if (String(m.id) === musicaId.value) botao.classList.add("selecionado");

      const img = document.createElement("img");
      img.className = "capa";
      img.width = 40;
      img.height = 40;
      definirImagem(img, m.capa, "");

      const info = document.createElement("span");
      info.className = "info";

      const t = document.createElement("strong");
      t.className = "titulo";
      t.textContent = m.titulo;

      const a = document.createElement("span");
      a.className = "artista";
      a.textContent = m.artista;
      info.append(t, a);

      botao.append(img, info);
      botao.addEventListener("click", () => escolher(m, botao));

      li.append(botao);
      lista.append(li);
    }
  }

  let temporizador;
  let buscaAtual = 0;

  async function buscar(termo) {
    const minhaBusca = ++buscaAtual;
    mensagemNaLista("Buscando…");
    try {
      const resp = await fetch(`/api/musicas?q=${encodeURIComponent(termo)}`);
      const dados = await resp.json();
      if (minhaBusca !== buscaAtual) return;
      if (!resp.ok) throw new Error(dados.erro || "Erro ao buscar músicas.");
      renderizar(dados.resultados);
    } 
    catch (e) {
      if (minhaBusca !== buscaAtual) return;
      mensagemNaLista(
        location.protocol === "file:" ? MSG_ARQUIVO : e instanceof TypeError
          ? "Não consegui falar com o servidor." : e.message
      );
    }
  }

  busca.addEventListener("input", () => {
    clearTimeout(temporizador);
    const termo = busca.value.trim();
    if (!termo) {
      buscaAtual++;
      lista.replaceChildren();
      return;
    }
    temporizador = setTimeout(() => buscar(termo), 400);
  });

  let linkPdf = null;

  function mostrarLink(dados) {
    campoLink.value = dados.link;
    if (!linkPdf) {
      linkPdf = document.createElement("a");
      linkPdf.id = "link-pdf";
      linkPdf.textContent = "Baixar PDF";
      blocoLink.append(linkPdf);
    }
    linkPdf.href = dados.pdf;
    mostrar(blocoLink, true);
    blocoLink.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    limparErro();

    if (location.protocol === "file:") return mostrarErro(MSG_ARQUIVO);

    const corpo = {
      para: $("para").value,
      texto: $("texto").value,
      de: $("de").value,
      musica_id: musicaId.value,
    };

    const rotuloOriginal = botaoGerar.textContent;
    botaoGerar.disabled = true;
    botaoGerar.textContent = "Gerando…";
    try {
      const resp = await fetch("/api/cartas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(corpo),
      });
      const dados = await resp.json().catch(() => ({}));
      if (!resp.ok) throw new Error(dados.erro || "Não foi possível gerar a carta.");
      mostrarLink(dados);
    } 
    catch (e) {
      mostrarErro(e instanceof TypeError ? "Não consegui falar com o servidor." : e.message);
    } 
    finally {
      botaoGerar.disabled = false;
      botaoGerar.textContent = rotuloOriginal;
    }
  });

  btnCopiar.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(campoLink.value);
    } 
    catch {
      campoLink.select();
      document.execCommand("copy");
    }
    const original = btnCopiar.textContent;
    btnCopiar.textContent = "Copiado!";
    setTimeout(() => (btnCopiar.textContent = original), 1500);
  });

  lista.replaceChildren();
  mostrar(blocoLink, false);
  limparEscolha();
  rotular(false);
})();