# roadmap-by-ai

Estrutura para criar roadmaps de estudo do zero ao avançado, com fases,
dependências, exercícios, validação, tutoria por ID e progresso persistente.

O conteúdo vive em Markdown. Os scripts geram um dashboard, mapas navegáveis e
glossários em HTML, sem framework ou etapa de build.

## Requisitos

- Node 18 ou superior, para o servidor local (recomendado);
- Python 3.9 ou superior, para os geradores;
- Chrome ou Edge para persistência direta em arquivo, sem servidor.

Não há dependências externas: `npm install` não é necessário.

## Rodar local

```bash
npm start
```

Depois abra `http://localhost:8000/`. O servidor (`server.js`) usa só módulos
nativos do Node e cuida de três coisas:

- **progresso automático**: os checkboxes gravam no `progresso.json` via
  `/api/progresso`, sem banner nem configuração;
- **watcher**: editar `roadmaps/**/*.md` regenera o HTML correspondente e
  recarrega a página aberta; editar `scripts/*.py` regenera tudo;
- **live reload**: o navegador recarrega sozinho a cada geração ou reinício
  do servidor.

Sem Node, abra `index.html` direto no Chrome/Edge (persistência via File
System Access API) ou use o fallback `python3 scripts/serve.py`.

## Começar

1. Leia [SPEC.md](SPEC.md).
2. Para criar ou expandir um roadmap, siga
   [skills/roadmap/SKILL.md](skills/roadmap/SKILL.md).
3. Crie `roadmaps/<tema>/<TEMA>-ROADMAP.md`.
4. Gere os artefatos:

```bash
python3 scripts/generate_html.py roadmaps/<tema>/<TEMA>-ROADMAP.md
python3 scripts/generate_glossary_html.py roadmaps/<tema>/GLOSSARIO.md  # opcional
python3 scripts/generate_index.py
```

Abra `index.html` no navegador ou rode `npm start` e acesse
`http://localhost:8000/`.

## Formato mínimo de um nó

```markdown
### 0.1 Primeiro conceito
- [ ] Concluído
- **Conceito:** o que precisa ser compreendido.
- **Prática:** uma tarefa concreta.
- **Validação:** uma evidência objetiva de aprendizagem.
- **Me teste:** pergunta 1 · pergunta 2
```

IDs são estáveis: depois de publicado, um nó não deve ser renumerado.

## Gerar tudo

Use este comando após alterar scripts ou o sistema visual:

```bash
for md in roadmaps/*/*-ROADMAP.md; do python3 scripts/generate_html.py "$md"; done
for md in roadmaps/*/GLOSSARIO.md; do python3 scripts/generate_glossary_html.py "$md"; done
python3 scripts/generate_index.py
```

O dashboard funciona também sem roadmaps e apresenta a orientação para criar a
primeira trilha.

## Progresso

Servido por `npm start` (ou `python3 scripts/serve.py`), a interface grava o
progresso automaticamente no `progresso.json` via `/api/progresso`, em
qualquer navegador. Aberto via `file://` em Chrome/Edge, usa File System
Access API e o navegador conserva apenas o handle do arquivo no IndexedDB. O
progresso nunca usa `localStorage`.

## Estrutura

```text
server.js                     servidor local zero-dependência (npm start)
package.json                  scripts do Node
skills/roadmap/SKILL.md       processo de criação e revisão
scripts/generate_html.py      Markdown de roadmap → HTML
scripts/generate_glossary_html.py
scripts/generate_index.py     dashboard
scripts/progress_js.py        persistência compartilhada
scripts/serve.py              servidor fallback em Python
roadmaps/<tema>/              conteúdo de cada trilha
```

## Publicação segura

- não publique caminhos absolutos da sua máquina;
- não inclua credenciais, contas ou nomes privados;
- prefira exemplos reproduzíveis e caminhos relativos;
- roadmaps personalizados podem permanecer fora da distribuição pública;
- nunca edite os HTMLs gerados manualmente.

Consulte [AGENTS.md](AGENTS.md) para instruções destinadas a agentes e
[SPEC.md](SPEC.md) para o contrato completo.

## Licença

Este projeto é distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
