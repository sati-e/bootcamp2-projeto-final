# bootcamp2-projeto-final

## Equipe e divisão de funcionalidades

| Membro | RA | GitHub | Funcionalidade | Outros papéis |
|---|---|---|---|---|
| Satie K. Chirico | 22301624 | [@sati-e](https://github.com/sati-e) | **Frontend**: HTML e CSS, layout e responsividade | Documentação do README, Rulesets e Actions |
| Pedro Lucas R. Greco | 22308774 | [@GoGreco](https://github.com/GoGreco) | **Backend**: integração da API | Testes do backend e Docker |
| Eliza F. de Castro | 22302645 | [@Elizafc](https://github.com/Elizafc) | **Geração de PDF**: módulo que monta e exporta o PDF | Testes do módulo de PDF |

## Descrição
Cartas com trilha é um site simples para enviar cartas digitais acompanhadas de uma música. A pessoa escreve o texto numa página com visual de papel de carta, escolhe uma canção por meio de uma busca com API integrada e recebe um link único para compartilhar por WhatsApp, e-mail ou redes sociais. Quem abre o link consegue ver a carta e acessar o site.  

## Banco de dados
Devido a natureza da plataforma, onde um usuário escreve uma carta anexa uma música e salva o pdf, não existe na arquitetura uma necessidade de banco de dados.  
Arquivos gerados são armazenados pela memória da imagem onde a plataforma está disponível.

## Links
Repositório: https://github.com/sati-e/bootcamp2-projeto-final    
Docker Hub: https://hub.docker.com/r/grupocartas/cartas-plat  

## Executando com Docker

### Pré-requisitos
- Docker instalado;
- Conexão com a Internet.

### Execução
Execute o comando:

```bash
docker run --rm -p 8000:8000 -v cartas_data:/app/data grupocartas/cartas-plat:latest
```

A imagem será baixada do Docker Hub.

### Acesso
A aplicação estará funcionando no endereço: http://localhost:8000/

## API utilizada  
Nome: Deezer Public API  
Documentação: [https://pokeapi.co/docs/v2](https://developers.deezer.com/api)  
**Endpoints consumidos:**  

- `GET /search?q={termo}&limit={n}`: busca músicas pelo termo informado.
- `GET /track/{id}`: retorna os dados de uma música específica (título, artista, capa, preview de 30s e link).

API pública do Deezer, sem necessidade de autenticação.

## Funcionalidades
#### Escrever a carta
- Campo **Para** com o nome de quem vai receber
- Bloco de texto grande com estilo de papel pautado e letra manuscrita
- Campo **De** opcional, para enviar de forma anônima

#### Música
- Busca por título ou artista
- Lista de resultados com capa, nome da música e artista
- Prévia de 30 segundos

#### Compartilhar
-  Ao compartilhar é gerado um PDF para a pessoa baixar e compartilhar

## Tecnologias utilizadas
-  python com a biblioteca weasyprint
-  css
-  html
-  js

## PRs

| Membro | Funcionalidade (código) | PR |
|---|---|---|
| [Satie K. Chirico](https://github.com/sati-e) | Frontend (HTML/CSS) | [#3](https://github.com/sati-e/bootcamp2-projeto-final/pull/3) |
| [Pedro Lucas R. Greco](https://github.com/GoGreco) | Backend | [#2](https://github.com/sati-e/bootcamp2-projeto-final/pull/2) |
| [Eliza F. de Castro](https://github.com/Elizafc) | Geração de PDF | [#1](https://github.com/sati-e/bootcamp2-projeto-final/pull/1) |

## Integração contínua

O workflow `.github/workflows/ci.yml` roda os testes automaticamente a cada Pull Request para a `main`.  

O check `testes` é **obrigatório**: a branch `main` está protegida e não permite merge de PR com teste falhando.

### Evidência: PR com teste quebrado bloqueada

[PR #4: teste quebrado](https://github.com/sati-e/bootcamp2-projeto-final/pull/4)
