#!/usr/bin/env python3
"""Servidor local OPCIONAL — fallback para navegadores sem File System
Access API (Firefox, Safari). No dia a dia não é necessário: os HTMLs gravam
o progresso direto no progresso.json da raiz (ver scripts/progress_js.py).

Serve o index.html (dashboard) e os HTMLs dos roadmaps, e persiste o
progresso dos checkboxes em progresso.json via /api/progresso:

    python3 scripts/serve.py [--porta 8000]

Depois abra http://localhost:8000/. Formato do progresso.json:
{"AI-ROADMAP": {"0.1": true, ...}, ...} — só nós marcados entram no arquivo.
"""

import json
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRESS = ROOT / "progresso.json"

PORT = 8000
args = sys.argv[1:]
if "--porta" in args:
    PORT = int(args[args.index("--porta") + 1])

SLUG_RE = re.compile(r"^[A-Za-z0-9-]+$")
NODE_RE = re.compile(r"^\d+\.\d+$")


def load():
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    return {}


def save(data):
    tmp = PROGRESS.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(PROGRESS)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/progresso":
            self._json(load())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/progresso":
            self.send_error(404)
            return
        try:
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            roadmap, node, done = body["roadmap"], body["node"], bool(body["done"])
            assert SLUG_RE.match(roadmap) and NODE_RE.match(node)
        except Exception:
            self._json({"erro": "payload inválido"}, 400)
            return
        data = load()
        nodes = data.setdefault(roadmap, {})
        if done:
            nodes[node] = True
        else:
            nodes.pop(node, None)
            if not nodes:
                data.pop(roadmap)
        save(data)
        self._json({"ok": True})

    def log_message(self, fmt, *a):
        if "/api/" not in (a[0] if a else ""):
            super().log_message(fmt, *a)


if __name__ == "__main__":
    print(f"Servindo em http://localhost:{PORT}/ (index com abas)")
    for html_file in sorted(ROOT.glob("roadmaps/*/*-ROADMAP.html")):
        print(f"  http://localhost:{PORT}/{html_file.relative_to(ROOT)}")
    print(f"Progresso salvo em {PROGRESS}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
