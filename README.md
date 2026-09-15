# roadmap-by-ai

Estrutura para criar roadmaps de estudo do zero ao avançado, com fases,
dependências, exercícios, validação, tutoria por ID e progresso persistente.

O conteúdo vive em Markdown. Os scripts geram um dashboard, mapas navegáveis e
glossários em HTML, sem framework ou etapa de build.

## Requisitos

- Python 3.9 ou superior;
- Chrome ou Edge para persistência direta em arquivo;
- qualquer navegador moderno usando o servidor fallback.

Não há dependências Python externas.

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

Abra `index.html` no navegador.

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

Em Chrome e Edge, a interface usa File System Access API para gravar diretamente
no `progresso.json`. O navegador conserva apenas o handle do arquivo no
IndexedDB; o progresso não usa `localStorage`.

Fallback para outros navegadores:

```bash
python3 scripts/serve.py
```

Depois acesse `http://localhost:8000/`.

## Estrutura

```text
skills/roadmap/SKILL.md       processo de criação e revisão
scripts/generate_html.py      Markdown de roadmap → HTML
scripts/generate_glossary_html.py
scripts/generate_index.py     dashboard
scripts/progress_js.py        persistência compartilhada
scripts/serve.py              servidor fallback
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
