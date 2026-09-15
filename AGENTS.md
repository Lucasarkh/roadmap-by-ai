# AGENTS.md — ai-structure

Repositório para criar roadmaps de estudo do zero ao avançado: fases com
dependências, nós com exercício e validação, tutoria por ID, progresso
persistente e HTMLs navegáveis gerados.

## Antes de trabalhar

- Leia `SPEC.md` antes de editar conteúdo, scripts ou convenções.
- Para criar, expandir ou revisar um roadmap, leia e siga integralmente
  `skills/roadmap/SKILL.md`.
- Trate os Markdown como fonte da verdade. Nunca edite HTML gerado.

## Fontes da verdade

- `roadmaps/<tema>/<TEMA>-ROADMAP.md`: conteúdo de um roadmap.
- `roadmaps/<tema>/GLOSSARIO.md`: glossário opcional.
- `SPEC.md`: contrato global de formato, pesquisa, visual e geração.
- `skills/roadmap/SKILL.md`: processo operacional para roadmaps.
- `scripts/`: geradores e persistência.

`index.html`, `*-ROADMAP.html` e `GLOSSARIO.html` são gerados. O
`progresso.json` é estado local do usuário e não deve ser editado manualmente.

## Estrutura

```text
ai-structure/
├── AGENTS.md
├── SPEC.md
├── index.html                         # GERADO
├── progresso.json                     # estado local, opcional
├── server.js                          # servidor local zero-dependência
├── package.json
├── skills/
│   └── roadmap/SKILL.md
├── scripts/
│   ├── generate_html.py
│   ├── generate_glossary_html.py
│   ├── generate_index.py
│   ├── progress_js.py
│   └── serve.py
└── roadmaps/
    └── <tema>/
        ├── <TEMA>-ROADMAP.md
        ├── <TEMA>-ROADMAP.html         # GERADO
        ├── GLOSSARIO.md/.html          # opcionais; HTML GERADO
        ├── CASE-*.md                   # opcional
        └── exercicios/                 # opcional
```

O repositório público pode começar sem roadmaps. Os geradores descobrem os
roadmaps presentes em `roadmaps/*/*-ROADMAP.md`.

## Uso diário

```bash
npm start
```

Abra `http://localhost:8000/`. O servidor (`server.js`, Node 18+, sem
dependências) salva o progresso automaticamente no `progresso.json` via
`/api/progresso`, vigia `roadmaps/**/*.md` e `scripts/*.py` para regenerar os
HTMLs e recarrega o navegador sozinho. Não use `localStorage`.

Sem servidor, abra `index.html` em Chrome ou Edge: na primeira utilização,
conecte ou crie o `progresso.json` pela interface (File System Access API) e o
handle fica salvo no navegador.

Fallback para navegadores sem File System Access API quando o Node não
estiver disponível:

```bash
python3 scripts/serve.py
```

## Editar conteúdo

1. Edite o Markdown correspondente.
2. Regenere o artefato aplicável.
3. Se mudou estrutura ou convenção, atualize `SPEC.md`, este arquivo e a skill
   na mesma alteração.

```bash
python3 scripts/generate_html.py roadmaps/<tema>/<TEMA>-ROADMAP.md
python3 scripts/generate_glossary_html.py roadmaps/<tema>/GLOSSARIO.md
python3 scripts/generate_index.py
```

Ao alterar layout, persistência ou contrato compartilhado, regenere tudo:

```bash
for md in roadmaps/*/*-ROADMAP.md; do python3 scripts/generate_html.py "$md"; done
for md in roadmaps/*/GLOSSARIO.md; do python3 scripts/generate_glossary_html.py "$md"; done
python3 scripts/generate_index.py
```

Valide pelo menos dois roadmaps, incluindo um com marcadores opcionais
`PROJ`/`GAP` ou seu alias legado `PF`, quando existirem.

## Convenções rápidas

- Idioma: pt-BR; termos, ferramentas e APIs em inglês.
- Fases vão de `0` a `N`; a cobertura define a quantidade.
- IDs `F.N` são únicos, estáveis e nunca renumerados.
- Todo nó contém Conceito, Prática, Validação e Me teste.
- O checkbox significa **Concluído**; domínio é demonstrado na Validação.
- `PROJ` e `GAP` são calibração opcional, nunca padrão de um roadmap público.
- Pesquisa web com fontes primárias e data no Anexo B é obrigatória para criar
  ou expandir conteúdo.
- Caminhos em conteúdo público são relativos ou placeholders; nunca inclua
  caminhos absolutos, credenciais, contas ou nomes privados.
- O HTML mantém o mapa resumido e abre o conteúdo no painel lateral. Preserve
  deep links, teclado, responsividade, acessibilidade e persistência.
- Dashboard, roadmap e glossário compartilham a linguagem visual definida em
  `SPEC.md`; CSS e JS não vivem nos arquivos de conteúdo.
