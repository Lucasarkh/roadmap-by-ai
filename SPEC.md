# SPEC — Contrato global dos roadmaps

> Fonte normativa do formato, da geração e da experiência visual deste
> repositório. Vale para qualquer tema; decisões específicas pertencem ao
> Markdown do respectivo roadmap.

## 1. Objetivo

Produzir roadmaps de estudo do zero ao avançado, com fases dependentes, nós
práticos, validação objetiva, tutoria por ID estável e progresso persistente.

O projeto deve poder ser publicado e reutilizado sem depender de nomes,
caminhos, contas, ferramentas de agente ou projetos privados. Roadmaps locais
podem ser personalizados, mas essa personalização nunca vira regra global.

## 2. Fontes da verdade e artefatos

- `roadmaps/<tema>/<TEMA>-ROADMAP.md`: conteúdo do roadmap.
- `roadmaps/<tema>/GLOSSARIO.md`: conteúdo opcional do glossário.
- `SPEC.md`: contrato global.
- `AGENTS.md`: instruções operacionais para agentes.
- `skills/roadmap/SKILL.md`: processo para criar, revisar ou expandir roadmaps.
- `scripts/*.py`: implementação dos geradores e da persistência.

São artefatos derivados e nunca devem ser editados manualmente:

- `roadmaps/<tema>/<TEMA>-ROADMAP.html`;
- `roadmaps/<tema>/GLOSSARIO.html`;
- `index.html`.

O `progresso.json` é estado do usuário, criado e atualizado pela interface. Não
é conteúdo autoral nem arquivo para edição manual.

## 3. Estrutura de arquivos

Cada roadmap fica isolado em uma pasta própria:

```text
ai-structure/
├── AGENTS.md
├── SPEC.md
├── index.html                         # GERADO
├── progresso.json                     # estado local, opcional
├── server.js                          # servidor local zero-dependência
├── package.json
├── skills/
│   └── roadmap/
│       └── SKILL.md
├── scripts/
│   ├── generate_html.py
│   ├── generate_glossary_html.py
│   ├── generate_index.py
│   ├── progress_js.py
│   └── serve.py
└── roadmaps/
    └── <tema>/
        ├── <TEMA>-ROADMAP.md           # fonte da verdade
        ├── <TEMA>-ROADMAP.html         # GERADO
        ├── GLOSSARIO.md                # opcional
        ├── GLOSSARIO.html              # GERADO, se houver Markdown
        ├── CASE-*.md                   # opcional
        └── exercicios/                 # opcional
```

Regras:

- `<tema>` é curto, minúsculo e coerente com o prefixo do arquivo.
- Conteúdo de um roadmap não depende de arquivos privados ou de outro roadmap.
- Referências a um projeto real usam caminhos relativos ou placeholders
  documentados, nunca caminhos absolutos de uma máquina.
- Scripts e contratos compartilhados ficam na raiz; conteúdo fica em
  `roadmaps/<tema>/`.

## 4. Formato do roadmap

### 4.1 Estrutura geral

1. `# ROADMAP — <tema> (do zero ao avançado)`.
2. Introdução em blockquote: público, objetivo, uso e contrato de tutoria.
3. `## Mapa geral` com Mermaid `flowchart TD` e dependências reais.
4. Fases `## Fase N — Título`, numeradas de `0` a `N` conforme o tema.
5. Logo abaixo de cada fase: `> Pré-requisito: ...`.
6. Anexos opcionais de calibração e obrigatórios de fontes.

O número de fases é consequência da cobertura, não uma constante global.

### 4.2 Formato obrigatório do nó

```markdown
### F.N Título do nó
- [ ] Concluído
- **Conceito:** 1 a 3 frases.
- **Prática:** exercício concreto.
- **Validação:** critério objetivo de aprendizagem.
- **Me teste:** 2 a 3 perguntas separadas por `·`.
```

- `F.N` é único, estável e imutável.
- Todo nó contém Conceito, Prática, Validação e Me teste.
- Nó sem prática ou validação não entra.
- Continuações de uma seção usam dois espaços de indentação.
- Idioma: pt-BR; termos, ferramentas e APIs permanecem em inglês.
- O checkbox representa conclusão do nó. Domínio é verificado pela Validação e
  pelo bloco Me teste; a interface usa sempre o termo “concluído”.

### 4.3 Calibração opcional

Roadmaps personalizados podem marcar nós no título:

- `PROJ`: conteúdo já presente no projeto usado como referência;
- `GAP`: lacuna conhecida e prioritária.

O gerador também aceita `PF` como alias legado de `PROJ`, para preservar
roadmaps locais existentes. Roadmaps públicos e neutros não vêm pré-calibrados.

## 5. Pesquisa e fontes

Roadmaps novos ou expandidos exigem pesquisa web atual, com leitura das fontes
primárias completas sempre que possível.

- Use documentação oficial, artigos originais, papers e repositórios dos
  mantenedores.
- Use agregadores e roadmaps externos apenas para checar cobertura.
- Registre fontes e data em `Anexo B — Fontes (pesquisadas em AAAA-MM-DD)` no
  próprio `<TEMA>-ROADMAP.md`.
- Explique o que cada fonte ancora.
- Evite rankings e comparativos voláteis; ensine critérios de escolha.
- A `SPEC.md` não armazena pesquisa de um roadmap específico.

## 6. Glossário

Quando o tema tiver jargão relevante:

- categoria: heading `##`, preferencialmente espelhando fases;
- termo: heading `###`;
- subtermo: heading `####`;
- definição: 1 a 3 frases claras em pt-BR;
- ponteiros: `→ nó F.N` e `→ termo`, quando existirem;
- contrato de tutoria: “estuda comigo o termo X”.

Termos sem relação com o roadmap não entram.

## 7. Geração e persistência

Execute da raiz:

```bash
for md in roadmaps/*/*-ROADMAP.md; do python3 scripts/generate_html.py "$md"; done
for md in roadmaps/*/GLOSSARIO.md; do python3 scripts/generate_glossary_html.py "$md"; done
python3 scripts/generate_index.py
```

Os checkboxes gravam no `progresso.json`, chaveado pelo slug do roadmap e ID do
nó. Servido por http, a interface usa `/api/progresso` automaticamente — o
servidor local recomendado é:

```bash
npm start    # node server.js: serve, persiste, vigia os .md e regenera os HTMLs
```

Aberto via `file://` em Chrome/Edge, usa File System Access API e conserva o
handle no IndexedDB. O fallback sem Node é `python3 scripts/serve.py`.

Não use `localStorage` para progresso.

## 8. Contrato visual

A interação do mapa pode se inspirar no roadmap.sh; referências externas de
produto servem apenas para organização e hierarquia, nunca para copiar marca.
A linguagem é própria de um produto de estudo:

- tipografia legível e moderada;
- azul/índigo para estrutura e navegação;
- amarelo para percurso e atenção;
- verde para conclusão;
- vermelho para lacuna;
- superfícies claras, respiro e estados inequívocos.

O topo separa barra do produto, hero educacional compacto, progresso e
navegação sticky por fases. Instruções técnicas ficam nas docs ou no rodapé.

O mapa permanece resumido. Clicar num nó abre um painel lateral único com ID,
título e os quatro blocos pedagógicos. Concluir persiste o mesmo checkbox;
Próximo abre o próximo nó pendente.

Preserve:

- deep links `#nF.N` e histórico do navegador;
- fechamento por botão, backdrop e `Esc`;
- foco contido no diálogo e devolvido ao nó de origem;
- layout móvel;
- `prefers-reduced-motion`;
- contraste e foco visível.

Dashboard, roadmap e glossário devem parecer partes do mesmo produto. Mudanças
visuais são feitas nos geradores compartilhados e exigem regenerar todos os
artefatos aplicáveis.

## 9. Critério de conclusão

Antes de entregar uma criação ou alteração:

1. Fases cobrem do fundamento à aplicação avançada e declaram pré-requisitos.
2. IDs existentes não foram renumerados.
3. Todos os nós cumprem o formato obrigatório.
4. Mermaid representa as dependências reais.
5. Fontes primárias e data estão no Anexo B.
6. Roadmap HTML foi regenerado.
7. Glossário HTML foi regenerado quando houver glossário.
8. Dashboard foi regenerado quando roadmaps foram criados ou removidos, ou
   quando sua apresentação compartilhada mudou.
9. Geradores compilam, `git diff --check` passa e pelo menos dois roadmaps são
   verificados quando o layout compartilhado muda.
10. `SPEC.md`, `AGENTS.md` e `skills/roadmap/SKILL.md` continuam alinhados.
