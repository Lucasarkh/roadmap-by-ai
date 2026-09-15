#!/usr/bin/env python3
"""Gera o index.html da raiz: dashboard com um card por roadmap.

Cada card mostra título, barra de progresso (n/total, lida do progresso.json)
e abre o HTML do roadmap — sem html único gigante e sem duplicar lógica. O
progresso vem do progresso.json — via /api/progresso quando servido (node
server.js) ou via File System Access API no file:// (ver scripts/progress_js.py).
Regenerar quando um roadmap for criado/removido:

    python3 scripts/generate_index.py
"""

import html
import json
import re
from pathlib import Path

from progress_js import BANNER_CSS, BANNER_HTML, PROGRESS_JS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "index.html"

NODE_RE = re.compile(r"^### \d+\.\d+ ")
PHASE_RE = re.compile(r"^## Fase \d+ — ")

roadmaps = []
for md in sorted(ROOT.glob("roadmaps/*/*-ROADMAP.md")):
    page = md.with_suffix(".html")
    if not page.exists():
        continue
    slug = page.stem
    raw = slug[: -len("-ROADMAP")]
    label = raw if len(raw) <= 3 else raw.capitalize()
    text = md.read_text(encoding="utf-8")
    title = re.sub(r"^#\s*(ROADMAP\s*—\s*)?", "", text.splitlines()[0]).strip()
    roadmaps.append({
        "slug": slug,
        "label": label,
        "title": title,
        "src": str(page.relative_to(ROOT)),
        "total": sum(1 for line in text.splitlines() if NODE_RE.match(line)),
        "phases": sum(1 for line in text.splitlines() if PHASE_RE.match(line)),
    })

cards = "".join(
    f'''<a class="card" href="{html.escape(r["src"])}">
      <span class="card-top"><span class="card-label">{html.escape(r["label"])}</span><span class="card-arrow">↗</span></span>
      <span class="card-title">{html.escape(r["title"])}</span>
      <span class="card-meta">{r["phases"]} fases · {r["total"]} nós</span>
      <span class="bar"><span class="fill" id="f-{r["slug"]}"></span></span>
      <span class="count" id="c-{r["slug"]}">–/{r["total"]} concluídos</span>
    </a>'''
    for r in roadmaps
)
if not cards:
    cards = '''<section class="empty">
      <span class="empty-icon">＋</span>
      <h2>Seu primeiro roadmap começa aqui</h2>
      <p>Crie <code>roadmaps/&lt;tema&gt;/&lt;TEMA&gt;-ROADMAP.md</code> seguindo a skill e gere os artefatos.</p>
    </section>'''
slugs_json = json.dumps([{"slug": r["slug"], "total": r["total"]} for r in roadmaps])

page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Roadmaps de estudo</title>
<style>
  :root {{ --primary:#2563eb; --primary-dark:#172554; --ink:#172033; --muted:#64748b; --line:#e2e8f0; --canvas:#f8fafc; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; margin:0; background:var(--canvas); color:var(--ink); min-height:100vh; }}
  header {{ padding:1.3rem 1.5rem 3.5rem; background:linear-gradient(135deg,#f8fbff,#fff 62%,#fffbeb); border-bottom:1px solid var(--line); }}
  .topbar,.hero,main,#savewarn {{ max-width:1120px; margin-left:auto; margin-right:auto; }}
  .topbar {{ color:var(--primary-dark); font-size:.9rem; font-weight:800; }}
  .hero {{ padding-top:3.25rem; }}
  .eyebrow {{ color:var(--primary); font-size:.76rem; font-weight:850; letter-spacing:.13em; text-transform:uppercase; margin:0 0 1rem; }}
  h1 {{ max-width:760px; font-size:clamp(2.6rem,6vw,4.45rem); line-height:1; letter-spacing:-.05em; margin:0; }}
  .sub {{ max-width:650px; color:var(--muted); line-height:1.65; font-size:1.05rem; margin:1.3rem 0 0; }}
  main {{ margin-top:-1.7rem; padding:0 1.5rem 5rem; display:grid; gap:1.1rem; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); position:relative; }}
  .card {{ display:flex; min-height:250px; flex-direction:column; gap:.55rem; background:#fff; border:1px solid var(--line); border-radius:18px; box-shadow:0 14px 36px rgba(15,23,42,.07); padding:1.35rem; text-decoration:none; color:inherit; transition:transform .18s,box-shadow .18s,border-color .18s; }}
  .card:hover {{ transform:translateY(-4px); box-shadow:0 20px 44px rgba(15,23,42,.12); border-color:#93c5fd; }}
  .card-top {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:auto; }}
  .card-label {{ display:inline-flex; align-items:center; min-height:2rem; padding:.35rem .65rem; border-radius:999px; background:#eff6ff; color:var(--primary); font-size:.72rem; font-weight:850; text-transform:uppercase; letter-spacing:.09em; }}
  .card-arrow {{ display:grid; place-items:center; width:2.2rem; height:2.2rem; color:#fff; background:var(--primary-dark); border-radius:50%; font-size:1.05rem; transition:transform .18s; }}
  .card:hover .card-arrow {{ transform:rotate(45deg); }}
  .card-title {{ font-weight:820; font-size:1.4rem; line-height:1.18; letter-spacing:-.025em; margin-top:1rem; }}
  .card-meta,.count {{ font-size:.8rem; color:var(--muted); }}
  .bar {{ background:#eeeaf2; border-radius:999px; height:.55rem; overflow:hidden; margin-top:.55rem; }}
  .fill {{ display:block; height:100%; width:0; border-radius:inherit; background:linear-gradient(90deg,#2563eb,#0ea5e9); transition:width .3s; }}
  .empty {{ grid-column:1/-1; text-align:center; background:#fff; border:1px dashed #93c5fd; border-radius:18px; padding:3rem 1.5rem; color:var(--muted); }}
  .empty-icon {{ display:grid; place-items:center; width:3rem; height:3rem; margin:0 auto 1rem; color:var(--primary); background:#eff6ff; border-radius:50%; font-size:1.4rem; }}
  .empty h2 {{ color:var(--ink); margin:.2rem 0 .5rem; font-size:1.3rem; }}
  .empty p {{ margin:0; }}
  #savewarn {{ margin-top:1rem; margin-bottom:3rem; }}
{BANNER_CSS}
  #savewarn {{ color:#7f1d1d; background:#fff; border-color:#fecaca; border-radius:14px; box-shadow:0 8px 24px rgba(127,29,29,.08); }}
  @media(max-width:600px) {{ header {{ padding:1rem 1rem 3rem; }} .hero {{ padding-top:3rem; }} main {{ padding-left:1rem; padding-right:1rem; grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
  <div class="topbar">↗ Trilhas de estudo</div>
  <div class="hero"><p class="eyebrow">Aprenda com direção</p><h1>Do primeiro passo ao domínio.</h1>
  <p class="sub">Roadmaps práticos, organizados em fases e com progresso real. Escolha uma trilha e avance um nó por vez.</p></div>
</header>
{BANNER_HTML}
<main>{cards}</main>
<script>
  {PROGRESS_JS}
  const ROADMAPS = {slugs_json};
  const banner = document.getElementById('savewarn');
  wireProgress(banner, state => {{
    ROADMAPS.forEach(r => {{
      const done = Object.keys(state[r.slug] || {{}}).length;
      document.getElementById('c-' + r.slug).textContent = done + '/' + r.total + ' concluídos';
      document.getElementById('f-' + r.slug).style.width = (r.total ? Math.round(done / r.total * 100) : 0) + '%';
    }});
  }});
</script>
</body>
</html>
"""

OUT.write_text(page, encoding="utf-8")
print(f"{len(roadmaps)} roadmaps -> {OUT}")
