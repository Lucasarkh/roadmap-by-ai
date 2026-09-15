---
name: roadmap
description: Cria, expande e revisa roadmaps de estudo do zero ao avançado no contrato do ai-structure, com pesquisa primária, fases dependentes, nós práticos, glossário opcional e artefatos HTML gerados.
---

# Roadmap de estudos — processo portátil

Use esta skill sempre que a tarefa criar, expandir ou revisar conteúdo de um
roadmap. Antes de agir, leia integralmente `SPEC.md`; ela é o contrato global.

Esta skill não depende de um agente, IDE, conta, máquina ou projeto privado.
Use as capacidades de pesquisa web e de edição disponíveis no ambiente.

## 1. Calibre o ponto de partida

Determine público, conhecimento prévio, objetivo e contexto prático. Se houver
um projeto de referência, identifique o que já existe e as lacunas.

Calibração é opcional:

- `PROJ`: o assunto já está presente no projeto de referência;
- `GAP`: lacuna conhecida e prioritária.

`PF` é aceito apenas como alias legado de `PROJ`. Roadmaps públicos e neutros
não devem vir pré-calibrados.

## 2. Pesquise antes de escrever

Roadmaps novos e expansões exigem pesquisa web atual.

- Priorize documentação oficial, papers, posts originais e repositórios dos
  mantenedores.
- Leia as fontes primárias completas; snippets não bastam.
- Use roadmaps externos e agregadores apenas para checar cobertura.
- Faça leitura crítica de números e alegações de marketing.
- Evite rankings voláteis; ensine critérios de escolha.
- Registre links, data e o que cada fonte ancora no
  `Anexo B — Fontes (pesquisadas em AAAA-MM-DD)` do próprio roadmap. A data do
  Anexo B vale também como data de verificação dos materiais de aula dos nós.

### Material de aula de cada nó

Além da pesquisa geral, cada nó exige busca dedicada por artigos e vídeos do
YouTube sobre o tema exato do nó:

- Investigue a fundo: busque, abra e leia/assista o suficiente para garantir
  que o material trata do tópico do nó — não do tema geral do roadmap.
- Verifique cada link antes de incluí-lo: o artigo responde HTTP 200 e o
  conteúdo confere; o vídeo é validado pelo endpoint oEmbed do YouTube
  (`https://www.youtube.com/oembed?url=<url-do-vídeo>&format=json` — 200
  significa que existe e é público) e tem título/descrição compatíveis.
- Prefira documentação oficial, blogs de engenharia, artigos originais e
  canais oficiais de fornecedores ou conferências.
- Nunca invente URL, título ou ID de vídeo. Se não encontrar material bom e
  verificável, inclua menos itens — nunca preencha com qualquer coisa.
- Vídeos entram com a URL canônica `https://www.youtube.com/watch?v=VIDEO_ID`
  para o gerador embedar o player no painel lateral.

Não registre pesquisa específica de um roadmap na `SPEC.md` global.

## 3. Desenhe as fases

- Numere de `0` a `N`, conforme a cobertura necessária.
- Fase 0 cobre fundamentos; a última consolida aplicação avançada, operação ou
  capstone.
- Declare pré-requisitos e permita ramos paralelos depois da base.
- Desenhe primeiro o grafo Mermaid `flowchart TD`; depois escreva os nós.
- Cubra do primeiro contato até uso com critério em cenário real.

## 4. Escreva os nós

Formato obrigatório:

```markdown
### F.N Título do nó
- [ ] Concluído
- **Conceito:** 1 a 3 frases.
- **Prática:** exercício concreto.
- **Validação:** critério objetivo de aprendizagem.
- **Me teste:** 2 a 3 perguntas separadas por `·`.
- **Material de aula:**
  - Artigo: [Título real do artigo](https://url) — publicação/autor; o que ancora no nó.
  - Vídeo: [Título real do vídeo](https://www.youtube.com/watch?v=VIDEO_ID) — canal; o que cobre.
```

Regras:

- `F.N` é único, estável e imutável. Nunca renumere IDs existentes.
- Todo nó contém os cinco blocos; sem Prática e Validação ele não entra.
- Material de aula: 1 a 3 artigos e 1 a 2 vídeos, todos verificados na web e
  fiéis ao tema do nó, conforme a seção 2.
- Continuações usam dois espaços de indentação.
- Quando houver experiência prévia, use pontes explícitas entre tecnologias.
- Prefira exercícios em projetos mínimos reproduzíveis ou caminhos relativos
  de um projeto fornecido pelo usuário.
- Nunca publique caminhos absolutos, credenciais, contas ou nomes privados.
- Escreva em pt-BR e preserve nomes técnicos em inglês.

## 5. Monte a pasta

```text
roadmaps/<tema>/
├── <TEMA>-ROADMAP.md
├── <TEMA>-ROADMAP.html          # GERADO
├── GLOSSARIO.md                 # opcional
├── GLOSSARIO.html               # GERADO
├── CASE-*.md                    # opcional
└── exercicios/                  # opcional
```

O Markdown começa com:

1. `# ROADMAP — <tema> (do zero ao avançado)`;
2. introdução em blockquote;
3. `## Mapa geral` com Mermaid;
4. `## Fase N — Título` e `> Pré-requisito: ...`;
5. nós;
6. Anexo A opcional para calibração;
7. Anexo B obrigatório para fontes.

## 6. Crie o glossário quando necessário

Use `GLOSSARIO.md` para temas densos em jargão:

- `##` para categorias;
- `###` para termos;
- `####` para subtermos;
- definição curta em pt-BR;
- `→ nó F.N` e `→ termo` quando houver relação.

Termos precisam servir ao roadmap. O contrato de tutoria é “estuda comigo o
termo X”.

## 7. Gere os artefatos

Nunca edite HTML manualmente.

Para um roadmap:

```bash
python3 scripts/generate_html.py roadmaps/<tema>/<TEMA>-ROADMAP.md
python3 scripts/generate_glossary_html.py roadmaps/<tema>/GLOSSARIO.md  # se houver
python3 scripts/generate_index.py
```

Depois de uma mudança compartilhada:

```bash
for md in roadmaps/*/*-ROADMAP.md; do python3 scripts/generate_html.py "$md"; done
for md in roadmaps/*/GLOSSARIO.md; do python3 scripts/generate_glossary_html.py "$md"; done
python3 scripts/generate_index.py
```

Preserve a persistência central em `progresso.json`; não introduza
`localStorage`.

## 8. Preserve o sistema visual

O visual vive nos três geradores compartilhados. Roadmaps individuais não têm
CSS, JS, paleta ou layout próprios.

- mapa resumido e painel lateral único;
- hero educacional compacto;
- azul/índigo estrutural, amarelo de percurso, verde de conclusão e vermelho de
  lacuna;
- deep links `#nF.N`, histórico, teclado, foco acessível e mobile;
- `prefers-reduced-motion`;
- dashboard, roadmap e glossário reconhecíveis como o mesmo produto.

Referências externas orientam organização e hierarquia, não identidade visual.

## 9. Atualize contratos quando necessário

- Mudança global de formato, estrutura, visual ou geração: atualize `SPEC.md`,
  `AGENTS.md` e esta skill na mesma alteração.
- Conteúdo específico permanece no Markdown do roadmap.
- Um roadmap novo não precisa ser listado nominalmente nos contratos; o
  dashboard o descobre pela estrutura de pastas.

## 10. Checklist de entrega

1. Cobertura vai do fundamento à aplicação avançada.
2. Fases e Mermaid expressam dependências reais.
3. IDs existentes foram preservados.
4. Todos os nós cumprem o formato.
5. Todo nó tem Material de aula verificado (artigo abre, vídeo existe) e fiel
   ao tema do nó, e o HTML renderiza artigos como links e vídeos embedados.
6. Anexo B contém data, fontes primárias e âncoras.
7. Roadmap HTML foi regenerado.
8. Glossário HTML foi regenerado quando existir.
9. Dashboard foi regenerado quando aplicável.
10. Geradores compilam e `git diff --check` passa.
11. Mudanças visuais foram verificadas em pelo menos dois roadmaps.
12. Nenhum dado privado ou caminho absoluto entrou no conteúdo publicável.

## Fora de escopo

- teoria desconectada do objetivo do roadmap;
- rankings de ferramentas que envelhecem rapidamente;
- nós decorativos sem prática e validação;
- material de aula genérico, fora do tema exato do nó, ou com link não
  verificado na web;
- edição direta de artefatos gerados.
