# bootcamp2-projeto-final

#### Grupo:  
Satie K. Chirico - 22301624 | https://github.com/sati-e  
Pedro Lucas R. Greco - 22308774 | https://github.com/GoGreco  
Eliza F. de Castro - 22302645 | https://github.com/Elizafc  

## Descrição
Cartas com trilha é um site simples para enviar cartas digitais acompanhadas de uma música. A pessoa escreve o texto numa página com visual de papel de carta, escolhe uma canção por meio de uma busca com API integrada e recebe um link único para compartilhar por WhatsApp, e-mail ou redes sociais. Quem abre o link consegue ver a carta e acessar o site.  

## Banco de dados
Devido a natureza da plataforma, onde um usuário escreve uma carta anexa uma música e salva o pdf, não existe na arquitetura uma necessidade de banco de dados.  
Arquivos gerados são armazenados pela memória da imagem onde a plataforma está disponível.

## Links
Repositório: https://github.com/sati-e/bootcamp2-projeto-final  
GitHub Pages: 

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
-  

#### Ler a carta
-  

### Planejadas para o futuro
-  

## Tecnologias utilizadas
-  
