#!/usr/bin/env python3
"""Gera o HTML (mapa visual standalone) de um roadmap a partir do .md.

Visual de estudo inspirado na organização do roadmap.sh: espinha azul de
fases e tópicos ramificando à direita. Cada tópico abre um painel
lateral com Conceito · Prática · Validação · Me teste. O progresso é
gravado direto no progresso.json da raiz via File System Access API
(Chrome/Edge) — basta abrir o arquivo, sem servidor nem localStorage. O
index.html da raiz (scripts/generate_index.py) é o dashboard com um card por
roadmap. Regenerar após editar o .md:

    python3 scripts/generate_html.py <entrada.md> [saida.html]

O arquivo Markdown é obrigatório; a saída opcional fica ao lado da entrada.
"""

import html
import re
import sys
from pathlib import Path

from progress_js import BANNER_CSS, BANNER_HTML, PROGRESS_JS

ROOT = Path(__file__).resolve().parent.parent
if len(sys.argv) < 2:
    raise SystemExit("Uso: python3 scripts/generate_html.py <roadmap.md> [saida.html]")
MD = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else MD.with_suffix(".html")

PHASE_RE = re.compile(r"^## Fase (\d+) — (.+)$")
PHASE_SUB_RE = re.compile(r"^> Pré-requisito: (.+)$")
NODE_RE = re.compile(r"^### (\d+\.\d+) (.+)$")
SECTION_RE = re.compile(r"^- \*\*(\w[\w ]*):\*\*\s*(.*)$")

phases = []
current_phase = None
current_node = None
current_section = None


def close_section():
    global current_section
    current_section = None


for line in MD.read_text(encoding="utf-8").splitlines():
    m = PHASE_RE.match(line)
    if m:
        current_phase = {"num": m.group(1), "title": m.group(2), "prereq": "", "nodes": []}
        phases.append(current_phase)
        current_node = None
        close_section()
        continue
    m = PHASE_SUB_RE.match(line)
    if m and current_phase is not None and current_node is None:
        current_phase["prereq"] = m.group(1)
        continue
    m = NODE_RE.match(line)
    if m and current_phase is not None:
        title = m.group(2)
        flags = set(re.findall(r"`(PROJ|PF|GAP)`", title))
        title = re.sub(r"\s*`(PROJ|PF|GAP)`", "", title).strip()
        current_node = {"id": m.group(1), "title": title, "flags": flags, "sections": []}
        current_phase["nodes"].append(current_node)
        close_section()
        continue
    if current_node is not None:
        m = SECTION_RE.match(line)
        if m:
            current_section = {"label": m.group(1), "text": m.group(2)}
            current_node["sections"].append(current_section)
            continue
        if current_section is not None and line.startswith("  ") and line.strip():
            current_section["text"] += "\n" + line.strip()


def md_lite(text):
    out = html.escape(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                 r'<a href="\2" target="_blank" rel="noopener">\1</a>', out)
    return "<br>".join(out.split("\n"))


SECTION_CLASS = {"Conceito": "conceito", "Prática": "pratica", "Validação": "validacao", "Me teste": "meteste"}


def render_node(node):
    flags = node["flags"]
    cls = "topic"
    badges = ""
    if "PROJ" in flags or "PF" in flags:
        cls += " proj"
        badges += '<span class="badge proj">✓ No projeto</span>'
    if "GAP" in flags:
        cls += " gap"
        badges += '<span class="badge gap">⚠️ GAP</span>'
    body = "".join(
        f'<div class="sec {SECTION_CLASS.get(s["label"], "")}">'
        f'<span class="sec-label">{html.escape(s["label"])}</span>'
        f'<p>{md_lite(s["text"])}</p></div>'
        for s in node["sections"]
    )
    return f'''
    <div class="topic-row" id="n{node['id']}" data-node-row="{node['id']}">
      <input type="checkbox" class="done" data-node="{node['id']}" aria-label="Marcar {node['id']} como concluído">
      <button class="{cls}" type="button" data-open-node="{node['id']}"
        data-title="{html.escape(node['title'], quote=True)}" aria-haspopup="dialog">
        <span class="topic-title"><span class="nid">{node['id']}</span> {md_lite(node['title'])}</span>
        <span class="topic-meta">{badges}<span class="open-label">Abrir <span aria-hidden="true">→</span></span></span>
      </button>
      <template data-node-content="{node['id']}"><div class="topic-body">{body}
        <p class="hint">Travou? Peça no chat: <em>"estuda comigo o nó {node['id']}"</em></p></div></template>
    </div>'''


def render_phase(phase):
    topics = "".join(render_node(n) for n in phase["nodes"])
    prereq = f'<div class="prereq">Pré-requisito: {md_lite(phase["prereq"])}</div>' if phase["prereq"] else ""
    return f'''
  <section class="phase" id="fase{phase['num']}">
    <div class="spine"><div class="spine-card"><span class="fnum">Fase {phase['num']}</span>{md_lite(phase['title'])}</div>{prereq}</div>
    <div class="connector"></div>
    <div class="topics">{topics}</div>
  </section>'''


total = sum(len(p["nodes"]) for p in phases)
phases_html = "".join(render_phase(p) for p in phases)
nav = "".join(f'<a href="#fase{p["num"]}">Fase {p["num"]}</a>' for p in phases)

first_line = MD.read_text(encoding="utf-8").splitlines()[0]
TITLE = re.sub(r"^#\s*(ROADMAP\s*—\s*)?", "", first_line).strip()
has_proj = any({"PROJ", "PF"} & n["flags"] for p in phases for n in p["nodes"])
has_gap = any("GAP" in n["flags"] for p in phases for n in p["nodes"])
legend_flags = ""
if has_proj:
    legend_flags += "\n    <span>🟩 PROJ — já existe no projeto de referência</span>"
if has_gap:
    legend_flags += "\n    <span>🟥 GAP — lacuna conhecida, prioridade</span>"
roadmap_slug = OUT.stem
progress_js = PROGRESS_JS

page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<style>
  :root {{ --primary:#2563eb; --primary-dark:#172554; --primary-soft:#eff6ff; --yellow:#fffbeb; --yellow-strong:#fbbf24; --green:#16a34a; --green-soft:#dcfce7; --ink:#172033; --muted:#64748b; --surface:#fff; --canvas:#f8fafc; --line:#e2e8f0; --shadow:0 14px 36px rgba(15,23,42,.08); }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:var(--canvas); color:var(--ink); margin:0; padding:0 0 6rem; }}
  body.panel-open {{ overflow:hidden; }}
  .site-header {{ background:linear-gradient(135deg,#f8fbff 0%,#fff 62%,#fffbeb 100%); border-bottom:1px solid var(--line); }}
  .topbar {{ max-width:1180px; margin:0 auto; padding:1.15rem 1.5rem; display:flex; align-items:center; justify-content:space-between; }}
  .brand {{ display:flex; align-items:center; gap:.65rem; color:var(--primary-dark); text-decoration:none; font-size:.9rem; font-weight:750; }}
  .brand-mark {{ display:grid; place-items:center; width:2rem; height:2rem; border-radius:9px; color:#fff; background:var(--primary); box-shadow:0 5px 12px rgba(37,99,235,.2); }}
  .source-chip {{ color:var(--muted); font-size:.78rem; border:1px solid var(--line); background:rgba(255,255,255,.72); border-radius:999px; padding:.4rem .7rem; }}
  .hero {{ max-width:1180px; margin:0 auto; padding:2.35rem 1.5rem 2.5rem; display:grid; grid-template-columns:minmax(0,1.35fr) minmax(320px,.65fr); gap:3rem; align-items:center; }}
  .eyebrow {{ margin:0 0 .85rem; color:var(--primary); font-size:.76rem; line-height:1; font-weight:850; letter-spacing:.13em; text-transform:uppercase; }}
  h1 {{ max-width:820px; font-size:clamp(2.15rem,4vw,3.55rem); line-height:1.04; letter-spacing:-.04em; margin:0; }}
  .sub {{ color:var(--muted); max-width:680px; margin:1.25rem 0 0; font-size:1.02rem; line-height:1.65; }}
  .progress-card {{ background:rgba(255,255,255,.94); border:1px solid #dbeafe; border-radius:18px; padding:1.15rem; box-shadow:var(--shadow); }}
  .progress-top {{ display:flex; justify-content:space-between; gap:1rem; align-items:end; }}
  .progress-label {{ display:block; color:var(--muted); font-size:.75rem; font-weight:750; text-transform:uppercase; letter-spacing:.08em; margin-bottom:.25rem; }}
  #progress {{ display:block; font-size:1.25rem; font-weight:850; letter-spacing:-.03em; }}
  #progressPercent {{ color:var(--primary); font-size:1.8rem; line-height:1; font-weight:850; }}
  .progress-rail {{ height:.55rem; margin:.9rem 0 1rem; border-radius:999px; overflow:hidden; background:#eeeaf2; }}
  #progressFill {{ display:block; width:0; height:100%; border-radius:inherit; background:linear-gradient(90deg,#2563eb,#0ea5e9); transition:width .3s ease; }}
  .legend {{ display:flex; gap:.45rem; flex-wrap:wrap; font-size:.73rem; color:#4b4750; }}
  .legend span {{ display:inline-flex; align-items:center; background:#fafafa; border:1px solid var(--line); border-radius:999px; padding:.32rem .55rem; }}
  #savewarn {{ max-width:1150px; margin:0 auto 1rem; }}
{BANNER_CSS}
  #savewarn {{ color:#7f1d1d; background:#fff; border-color:#fecaca; border-radius:14px; box-shadow:0 8px 24px rgba(127,29,29,.08); }}
  .phase-nav {{ position:sticky; top:0; z-index:10; display:flex; align-items:center; gap:.7rem; overflow-x:auto; padding:.75rem max(1.5rem,calc((100vw - 1180px)/2 + 1.5rem)); background:rgba(255,255,255,.88); border-bottom:1px solid var(--line); box-shadow:0 8px 24px rgba(24,24,27,.04); backdrop-filter:blur(16px); scrollbar-width:none; }}
  .phase-nav::-webkit-scrollbar {{ display:none; }}
  .nav-label {{ color:var(--muted); font-size:.72rem; font-weight:800; text-transform:uppercase; letter-spacing:.09em; white-space:nowrap; margin-right:.2rem; }}
  .phase-nav a {{ color:#4b4750; text-decoration:none; white-space:nowrap; font-size:.78rem; font-weight:700; padding:.42rem .68rem; border-radius:999px; transition:background .15s,color .15s; }}
  .phase-nav a:hover {{ color:var(--primary); background:var(--primary-soft); }}
  .roadmap {{ padding:2.5rem 1.5rem 0; }}
  .phase {{ display:grid; grid-template-columns:310px 64px 1fr; max-width:1120px; margin:0 auto; position:relative; }}
  .spine {{ position:relative; padding:1.2rem 0; }}
  .spine::before {{ content:""; position:absolute; left:50%; top:0; bottom:0; border-left:2px solid #bfdbfe; }}
  .phase:first-child .spine::before {{ top:2.2rem; }}
  .phase:last-child .spine::before {{ bottom:auto; height:2.2rem; }}
  .spine-card {{ position:relative; color:#fff; background:linear-gradient(135deg,#172554,#1d4ed8); border:0; border-radius:14px; padding:.9rem 1rem; font-weight:750; box-shadow:0 10px 24px rgba(30,64,175,.16); margin:0 1rem; z-index:1; }}
  .fnum {{ display:block; font-size:.7rem; text-transform:uppercase; letter-spacing:.11em; color:#bfdbfe; margin-bottom:.3rem; }}
  .prereq {{ font-size:.73rem; line-height:1.45; color:var(--muted); margin:.6rem 1rem 0; position:relative; z-index:1; }}
  .connector {{ align-self:flex-start; margin-top:3.1rem; border-top:2px dashed #bfdbfe; }}
  .topics {{ display:flex; flex-direction:column; gap:.55rem; padding:1.2rem 0; }}
  .topic-row {{ display:flex; align-items:flex-start; gap:.5rem; }}
  .done {{ appearance:none; -webkit-appearance:none; display:grid; place-content:center; flex:none; width:1.35rem; height:1.35rem; margin:.65rem .05rem 0 0; cursor:pointer; border:2px solid #71717a; border-radius:50%; background:#fff; box-shadow:0 1px 0 rgba(0,0,0,.08); transition:background .15s,border-color .15s,transform .15s; }}
  .done::before {{ content:"✓"; color:#fff; font-size:.9rem; font-weight:900; line-height:1; transform:scale(0); transition:transform .12s; }}
  .done:hover {{ border-color:#16a34a; transform:scale(1.06); }}
  .done:focus-visible {{ outline:3px solid #86efac; outline-offset:3px; }}
  .done:checked {{ background:#16a34a; border-color:#15803d; }}
  .done:checked::before {{ transform:scale(1); }}
  .topic {{ flex:1; display:flex; align-items:center; justify-content:space-between; gap:.8rem; width:100%; text-align:left; color:inherit; font:inherit; cursor:pointer; background:var(--surface); border:1px solid var(--line); border-left:4px solid var(--yellow-strong); border-radius:12px; box-shadow:0 4px 14px rgba(24,24,27,.05); padding:.72rem .8rem; transition:transform .15s,box-shadow .15s,border-color .15s; }}
  .topic:hover {{ transform:translateY(-2px); box-shadow:0 10px 24px rgba(15,23,42,.1); border-color:#93c5fd; }}
  .topic:focus-visible {{ outline:3px solid #2563eb; outline-offset:3px; }}
  .topic.proj {{ background:#f0fdf4; border-left-color:#4ade80; }}
  .topic.gap {{ background:#fff1f2; border-left-color:#fb7185; }}
  .done:checked + .topic {{ background:#dcfce7; border-color:#86efac; border-left-color:#16a34a; box-shadow:0 6px 18px rgba(22,163,74,.11); }}
  .done:checked + .topic:hover {{ box-shadow:0 10px 24px rgba(22,163,74,.16); }}
  .done:checked + .topic .nid {{ background:#166534; }}
  .done:checked + .topic .open-label {{ color:#166534; font-size:0; font-weight:750; }}
  .done:checked + .topic .open-label::before {{ content:"Concluído"; font-size:.76rem; }}
  .topic-title {{ font-weight:650; }}
  .topic-meta {{ display:flex; align-items:center; justify-content:flex-end; gap:.35rem; flex-wrap:wrap; }}
  .open-label {{ color:#525252; font-size:.76rem; white-space:nowrap; }}
  .nid {{ background:var(--primary-dark); color:#fff; border-radius:6px; padding:.12em .45em; font-size:.78em; }}
  .badge {{ font-size:.68rem; font-weight:700; border-radius:999px; padding:.18em .55em; margin-left:.2em; border:1px solid rgba(24,24,27,.12); background:rgba(255,255,255,.8); }}
  .topic-body {{ font-weight:400; }}
  .sec {{ margin-top:.75rem; border:1px solid var(--line); border-radius:14px; padding:.95rem; background:#fff; }}
  .sec-label {{ display:inline-block; font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em; border-radius:4px; padding:.1em .5em; background:var(--ink); color:#fff; }}
  .sec p {{ margin:.35rem 0 0; font-size:.92rem; line-height:1.5; }}
  .sec.pratica .sec-label {{ background:#0369a1; }}
  .sec.validacao .sec-label {{ background:#16a34a; }}
  .sec.meteste .sec-label {{ background:#9333ea; }}
  code {{ background:#fff; border:1px solid #d4d4d4; border-radius:4px; padding:.05em .3em; font-size:.85em; }}
  a {{ color:#0369a1; }}
  .hint {{ font-size:.8rem; color:var(--primary); margin-top:.7rem; }}
  .panel-backdrop {{ position:fixed; inset:0; z-index:20; background:rgba(15,23,42,.5); opacity:0; visibility:hidden; transition:opacity .2s, visibility .2s; backdrop-filter:blur(2px); }}
  body.panel-open .panel-backdrop {{ opacity:1; visibility:visible; }}
  .resource-panel {{ position:fixed; z-index:21; inset:0 0 0 auto; width:min(640px,50vw); background:#fff; border-left:1px solid var(--line); box-shadow:-24px 0 60px rgba(15,23,42,.18); transform:translateX(102%); transition:transform .24s ease; display:flex; flex-direction:column; }}
  body.panel-open .resource-panel {{ transform:translateX(0); }}
  .panel-toolbar {{ display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:1rem 1.25rem; border-bottom:1px solid var(--line); background:#fcfbff; }}
  .panel-kicker {{ font-size:.78rem; font-weight:750; letter-spacing:.06em; text-transform:uppercase; color:var(--primary); }}
  .panel-actions {{ display:flex; align-items:center; gap:.35rem; }}
  .panel-actions button {{ font:inherit; font-size:.8rem; font-weight:650; background:#fff; border:1px solid #d4d4d8; border-radius:7px; padding:.42rem .65rem; cursor:pointer; }}
  .panel-actions button:hover {{ background:#f4f4f5; }}
  .panel-actions .is-done {{ color:#15803d; border-color:#86efac; background:#f0fdf4; }}
  .panel-actions .close-panel {{ border:0; background:#e4e4e7; width:2rem; height:2rem; padding:0; border-radius:50%; font-size:1.2rem; }}
  .panel-scroll {{ overflow:auto; padding:1.55rem 1.5rem 3rem; }}
  .panel-node-id {{ display:inline-flex; background:#18181b; color:#fff; border-radius:6px; padding:.15rem .5rem; font-size:.78rem; font-weight:750; }}
  .panel-scroll h2 {{ font-size:clamp(1.65rem,3vw,2.35rem); line-height:1.12; margin:.65rem 0 .35rem; letter-spacing:-.03em; }}
  .panel-intro {{ color:#52525b; margin:0 0 1.2rem; line-height:1.55; }}
  .resource-panel .sec {{ padding:1rem; margin-top:.75rem; }}
  .resource-panel .sec p {{ font-size:.95rem; line-height:1.6; }}
  .resource-panel .hint {{ border-top:1px solid #e4e4e7; padding-top:1rem; margin-top:1rem; }}
  footer {{ max-width:1120px; margin:4rem auto 0; padding:1.5rem; border-top:1px solid var(--line); text-align:center; color:var(--muted); font-size:.8rem; }}
  @media (max-width:860px) {{
    .topbar {{ padding:.9rem 1rem; }}
    .source-chip {{ display:none; }}
    .hero {{ grid-template-columns:1fr; gap:1.5rem; padding:1.8rem 1rem 2rem; }}
    h1 {{ font-size:clamp(2rem,10vw,3rem); }}
    .roadmap {{ padding:1.2rem 1rem 0; }}
    .phase {{ grid-template-columns:1fr; }}
    .spine::before, .connector {{ display:none; }}
    .prereq {{ margin-bottom:.5rem; }}
    .spine-card {{ margin:0; }}
    .prereq {{ margin:.6rem 0 0; }}
    .topics {{ padding:.75rem 0 1.5rem; }}
    .resource-panel {{ width:100%; top:2rem; border-left:0; border-top:1px solid var(--line); border-radius:22px 22px 0 0; }}
    .panel-toolbar {{ padding:.75rem 1rem; }}
    .panel-scroll {{ padding:1.25rem 1rem 2rem; }}
    .panel-actions .action-label {{ display:none; }}
  }}
  @media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} .resource-panel,.panel-backdrop,.topic,#progressFill {{ transition:none; }} }}
</style>
</head>
<body>
<header class="site-header">
  <div class="topbar">
    <a class="brand" href="../../index.html"><span class="brand-mark">↗</span><span>Todos os roadmaps</span></a>
    <span class="source-chip">Fonte: <code>{MD.name}</code></span>
  </div>
  <div class="hero">
    <div>
      <p class="eyebrow">Trilha de aprendizado · {len(phases)} fases</p>
      <h1>{html.escape(TITLE)}</h1>
      <p class="sub">Avance no seu ritmo. Abra um tópico para estudar o conceito, praticar e validar o que aprendeu.</p>
    </div>
    <div class="progress-card">
      <div class="progress-top"><div><span class="progress-label">Seu progresso</span><strong id="progress">0 de {total} concluídos</strong></div><strong id="progressPercent">0%</strong></div>
      <div class="progress-rail" aria-hidden="true"><span id="progressFill"></span></div>
      <div class="legend">{legend_flags}
        <span>🟡 para estudar</span><span>🟢 concluído</span>
      </div>
    </div>
  </div>
  {BANNER_HTML}
</header>
<nav class="phase-nav" aria-label="Navegação por fases"><span class="nav-label">Ir para</span>{nav}</nav>
<main class="roadmap">{phases_html}</main>
<div class="panel-backdrop" data-close-panel aria-hidden="true"></div>
<aside class="resource-panel" id="resource-panel" role="dialog" aria-modal="true" aria-labelledby="panel-title" aria-hidden="true" inert>
  <div class="panel-toolbar">
    <span class="panel-kicker">Conteúdo do nó</span>
    <div class="panel-actions">
      <button type="button" data-panel-done>✓ <span class="action-label">Concluir</span></button>
      <button type="button" data-panel-skip><span class="action-label">Próximo</span> →</button>
      <button type="button" class="close-panel" data-close-panel aria-label="Fechar painel">×</button>
    </div>
  </div>
  <div class="panel-scroll">
    <span class="panel-node-id"></span>
    <h2 id="panel-title"></h2>
    <p class="panel-intro">Estude o conceito, faça a prática e confirme a validação antes de concluir.</p>
    <div class="panel-content"></div>
  </div>
</aside>
<footer>Gerado de {MD.name} · Dúvida em qualquer nó: peça <em>"estuda comigo o nó F.N"</em></footer>
<script>
  {progress_js}
  const SLUG = '{roadmap_slug}';
  const boxes = document.querySelectorAll('.done');
  const banner = document.getElementById('savewarn');
  const nodeButtons = [...document.querySelectorAll('[data-open-node]')];
  const panel = document.getElementById('resource-panel');
  const panelTitle = document.getElementById('panel-title');
  const panelId = panel.querySelector('.panel-node-id');
  const panelContent = panel.querySelector('.panel-content');
  const panelDone = panel.querySelector('[data-panel-done]');
  let activeNode = null;
  let returnFocus = null;
  function update() {{
    const done = [...boxes].filter(b => b.checked).length;
    const percent = boxes.length ? Math.round(done / boxes.length * 100) : 0;
    document.getElementById('progress').textContent = done + ' de ' + boxes.length + ' concluídos';
    document.getElementById('progressPercent').textContent = percent + '%';
    document.getElementById('progressFill').style.width = percent + '%';
  }}
  function apply(state) {{
    const mine = state[SLUG] || {{}};
    boxes.forEach(b => {{ b.checked = !!mine[b.dataset.node]; }});
    update();
  }}
  function syncPanelState() {{
    if (!activeNode) return;
    const box = document.querySelector('.done[data-node="' + activeNode + '"]');
    panelDone.classList.toggle('is-done', box.checked);
    panelDone.innerHTML = box.checked ? '✓ <span class="action-label">Concluído</span>' : '✓ <span class="action-label">Concluir</span>';
  }}
  function openPanel(id, pushHash = true) {{
    const button = document.querySelector('[data-open-node="' + id + '"]');
    const template = document.querySelector('template[data-node-content="' + id + '"]');
    if (!button || !template) return;
    if (!activeNode) returnFocus = document.activeElement;
    activeNode = id;
    panelId.textContent = id;
    panelTitle.textContent = button.dataset.title;
    panelContent.replaceChildren(template.content.cloneNode(true));
    document.body.classList.add('panel-open');
    panel.setAttribute('aria-hidden', 'false');
    panel.removeAttribute('inert');
    syncPanelState();
    panel.querySelector('.panel-scroll').scrollTop = 0;
    panel.querySelector('[data-close-panel]').focus();
    if (pushHash && location.hash !== '#n' + id) history.pushState(null, '', '#n' + id);
  }}
  function closePanel(clearHash = true) {{
    if (!activeNode) return;
    document.body.classList.remove('panel-open');
    panel.setAttribute('aria-hidden', 'true');
    panel.setAttribute('inert', '');
    activeNode = null;
    if (clearHash && location.hash.startsWith('#n')) history.pushState(null, '', location.pathname + location.search);
    if (returnFocus && returnFocus.focus) returnFocus.focus();
  }}
  wireProgress(banner, apply);
  boxes.forEach(b => b.addEventListener('change', async () => {{
    try {{ await ProgressStore.setNode(SLUG, b.dataset.node, b.checked); }}
    catch {{ wireProgress(banner, apply); }}
    update();
    syncPanelState();
  }}));
  nodeButtons.forEach(b => b.addEventListener('click', () => openPanel(b.dataset.openNode)));
  document.querySelectorAll('[data-close-panel]').forEach(b => b.addEventListener('click', () => closePanel()));
  panelDone.addEventListener('click', () => {{
    const box = document.querySelector('.done[data-node="' + activeNode + '"]');
    if (box) {{ box.checked = !box.checked; box.dispatchEvent(new Event('change')); }}
  }});
  panel.querySelector('[data-panel-skip]').addEventListener('click', () => {{
    const index = nodeButtons.findIndex(b => b.dataset.openNode === activeNode);
    const next = nodeButtons.slice(index + 1).find(b => !document.querySelector('.done[data-node="' + b.dataset.openNode + '"]').checked)
      || nodeButtons.find(b => !document.querySelector('.done[data-node="' + b.dataset.openNode + '"]').checked);
    if (next) openPanel(next.dataset.openNode);
    else closePanel();
  }});
  document.addEventListener('keydown', e => {{
    if (e.key === 'Escape' && activeNode) closePanel();
    if (e.key === 'Tab' && activeNode) {{
      const focusable = [...panel.querySelectorAll('button,a[href],input,[tabindex]:not([tabindex="-1"])')];
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {{ e.preventDefault(); last.focus(); }}
      else if (!e.shiftKey && document.activeElement === last) {{ e.preventDefault(); first.focus(); }}
    }}
  }});
  window.addEventListener('popstate', () => {{
    if (location.hash.startsWith('#n')) openPanel(location.hash.slice(2), false);
    else closePanel(false);
  }});
  update();
  if (location.hash) {{
    if (location.hash.startsWith('#n')) openPanel(location.hash.slice(2), false);
  }}
</script>
</body>
</html>
"""

OUT.write_text(page, encoding="utf-8")
print(f"{len(phases)} fases, {total} tópicos -> {OUT}")
