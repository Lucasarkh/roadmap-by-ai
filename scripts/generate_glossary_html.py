#!/usr/bin/env python3
"""Gera GLOSSARIO.html a partir do GLOSSARIO.md.

Categorias (##) viram seções; termos (###) viram <details>; subtermos (####)
viram <details> aninhados. Referências "→ nó X.Y" viram link para o nó no
*-ROADMAP.html irmão (mesma pasta do glossário). Regenerar após editar:

    python3 scripts/generate_glossary_html.py <entrada.md> [saida.html]

O arquivo Markdown é obrigatório; a saída opcional fica ao lado da entrada.
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if len(sys.argv) < 2:
    raise SystemExit("Uso: python3 scripts/generate_glossary_html.py <glossario.md> [saida.html]")
MD = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else MD.with_suffix(".html")

_siblings = sorted(MD.parent.glob("*-ROADMAP.html"))
ROADMAP_HTML = _siblings[0].name if _siblings else "ROADMAP.html"

HEADING_RE = re.compile(r"^(#{2,4}) (.+)$")
NODEREF_RE = re.compile(r"→ nós? ((?:\d+\.\d+(?:, )?)+)")
NODEREF_ONE = re.compile(r"(\d+\.\d+)")


def md_lite(text):
    out = html.escape(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                 r'<a href="\2" target="_blank" rel="noopener">\1</a>', out)

    def noderef(m):
        links = ", ".join(
            f'<a class="noderef" href="{ROADMAP_HTML}#n{n}">nó {n}</a>'
            for n in NODEREF_ONE.findall(m.group(1))
        )
        return f"→ {links}"

    return NODEREF_RE.sub(noderef, out)


lines = MD.read_text(encoding="utf-8").splitlines()
TITLE = re.sub(r"^#\s*", "", lines[0]).strip() if lines else "Glossário"
intro = []
body_parts = []
open_levels = []  # heading levels currently open
paragraph = []


def flush_paragraph():
    if paragraph:
        body_parts.append(f"<p>{md_lite(' '.join(paragraph))}</p>")
        paragraph.clear()


def close_to(level):
    while open_levels and open_levels[-1] >= level:
        body_parts.append("</details>")
        open_levels.pop()
    flush_paragraph() if False else None


for line in lines:
    if line.startswith("# "):
        continue
    m = HEADING_RE.match(line)
    if m:
        flush_paragraph()
        level = len(m.group(1))
        title = m.group(2)
        if level == 2:
            close_to(2)
            body_parts.append(f"<h2>{md_lite(title)}</h2>")
            continue
        close_to(level)
        body_parts.append(
            f'<details class="term t{level}"><summary>{md_lite(title)}</summary>'
        )
        open_levels.append(level)
        continue
    if line.startswith("---"):
        flush_paragraph()
        continue
    if not body_parts and not open_levels and line.startswith(">"):
        intro.append(line.lstrip("> ").rstrip())
        continue
    if line.strip():
        paragraph.append(line.strip())
    else:
        flush_paragraph()

flush_paragraph()
close_to(3)

term_count = sum(1 for p in body_parts if p.startswith('<details class="term t3"'))

intro_html = "".join(f"<p>{md_lite(p)}</p>" for p in " ".join(intro).split("  ") if p.strip())

page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<style>
  :root {{ --primary:#2563eb; --primary-dark:#172554; --ink:#172033; --muted:#64748b; --line:#e2e8f0; --canvas:#f8fafc; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:var(--canvas); color:var(--ink); margin:0; padding:0 1rem 6rem; }}
  header {{ margin:0 -1rem 2.5rem; padding:1.2rem max(1rem,calc((100vw - 900px)/2)); background:linear-gradient(135deg,#f8fbff,#fff 62%,#fffbeb); border-bottom:1px solid var(--line); }}
  header > * {{ max-width:900px; margin-left:auto; margin-right:auto; }}
  main, footer {{ max-width:900px; margin-left:auto; margin-right:auto; }}
  .back {{ display:inline-flex; align-items:center; gap:.45rem; color:var(--primary-dark); text-decoration:none; font-size:.86rem; font-weight:800; margin-top:.2rem; }}
  .eyebrow {{ color:var(--primary); font-size:.75rem; font-weight:850; letter-spacing:.12em; text-transform:uppercase; margin-top:3rem; }}
  h1 {{ font-size:clamp(2.35rem,6vw,3.85rem); line-height:1.02; letter-spacing:-.045em; margin:.5rem auto 1.2rem; }}
  h2 {{ margin-top:2.7rem; font-size:1.45rem; letter-spacing:-.025em; border-left:5px solid #facc15; padding-left:.8rem; }}
  .intro {{ color:var(--muted); line-height:1.6; max-width:760px; }}
  #search {{ width:100%; padding:1rem 1.1rem; font-size:1rem; border:1px solid var(--line); border-radius:14px; margin-top:1.4rem; background:#fff; box-shadow:0 12px 30px rgba(15,23,42,.07); outline:none; }}
  #search:focus {{ border-color:#60a5fa; box-shadow:0 0 0 4px #dbeafe; }}
  #count {{ font-size:.8rem; color:var(--muted); margin-top:.65rem; }}
  details.term {{ background:#fff; border:1px solid var(--line); border-radius:14px; margin:.65rem 0; box-shadow:0 4px 14px rgba(24,24,27,.045); overflow:hidden; }}
  details.term[open] {{ border-color:#93c5fd; box-shadow:0 10px 28px rgba(15,23,42,.08); }}
  details.t4 {{ background:#f8fbff; margin:.5rem .8rem .8rem 1.4rem; box-shadow:none; border-color:#bfdbfe; }}
  summary {{ cursor:pointer; padding:.8rem 1rem; font-weight:750; list-style:none; }}
  summary::-webkit-details-marker {{ display:none; }}
  summary::before {{ content:"+"; display:inline-grid; place-items:center; width:1.35rem; height:1.35rem; margin-right:.55rem; color:var(--primary); background:#dbeafe; border-radius:50%; }}
  details[open] > summary::before {{ content:"−"; }}
  details p {{ margin:.2rem 1rem 1rem 2.95rem; line-height:1.6; font-size:.94rem; color:#3f3f46; }}
  code {{ background:#f5f5f5; border:1px solid #d4d4d4; border-radius:4px; padding:.05em .3em; font-size:.85em; }}
  a {{ color:var(--primary); }}
  a.noderef {{ background:#dbeafe; border-radius:6px; padding:.08em .42em; text-decoration:none; font-weight:700; }}
  .hidden {{ display:none; }}
  footer {{ margin-top:4rem; padding-top:1.5rem; border-top:1px solid var(--line); text-align:center; color:var(--muted); font-size:.8rem; }}
</style>
</head>
<body>
<header>
  <a class="back" href="../../index.html">↗ Todos os roadmaps</a>
  <p class="eyebrow">Referência rápida</p>
  <h1>{html.escape(TITLE)}</h1>
  <div class="intro">{intro_html}</div>
  <input id="search" type="search" placeholder="Buscar termo… (ex.: zero-shot, compaction, HNSW)">
  <p id="count">{term_count} termos</p>
</header>
<main>
{chr(10).join(body_parts)}
</main>
<footer>Gerado de {MD.name} · Ver também <a href="{ROADMAP_HTML}">{ROADMAP_HTML}</a></footer>
<script>
  const input = document.getElementById('search');
  const details = [...document.querySelectorAll('details.term')];
  const count = document.getElementById('count');
  input.addEventListener('input', () => {{
    const q = input.value.trim().toLowerCase();
    let visible = 0;
    details.forEach(d => {{
      const hit = !q || d.textContent.toLowerCase().includes(q);
      d.classList.toggle('hidden', !hit);
      if (hit && d.classList.contains('t3')) visible++;
      if (q && hit) d.open = true;
    }});
    count.textContent = q ? visible + ' termos encontrados' : '{term_count} termos';
  }});
</script>
</body>
</html>
"""

OUT.write_text(page, encoding="utf-8")
print(f"{term_count} termos -> {OUT}")
