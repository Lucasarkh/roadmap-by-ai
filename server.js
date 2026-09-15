#!/usr/bin/env node
/**
 * Servidor de desenvolvimento zero-dependência (Node 18+). Não exige npm
 * install — usa apenas módulos nativos do Node.
 *
 *   node server.js [--porta 8000]     # ou: npm start
 *
 * Depois abra http://localhost:8000/. O que ele faz:
 *
 *   1. Serve o index.html (dashboard) e os HTMLs gerados em roadmaps/.
 *   2. Persiste o progresso dos checkboxes em progresso.json via
 *      /api/progresso — mesmo contrato do scripts/serve.py, então as
 *      páginas geradas salvam automaticamente, sem banner nem clique.
 *   3. Watcher: editar roadmaps/** /*-ROADMAP.md ou GLOSSARIO.md regenera o
 *      HTML correspondente (chamando os geradores Python) e recarrega o
 *      navegador; alterar scripts/*.py regenera tudo.
 *   4. Live reload via Server-Sent Events (/api/livereload), com um snippet
 *      injetado nos HTMLs servidos. Também recarrega se o servidor reiniciar.
 *
 * Formato do progresso.json: {"AI-ROADMAP": {"0.1": true, ...}, ...} —
 * só nós marcados entram no arquivo.
 */

'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = __dirname;
const ROADMAPS = path.join(ROOT, 'roadmaps');
const SCRIPTS = path.join(ROOT, 'scripts');
const PROGRESS = path.join(ROOT, 'progresso.json');
const BOOT = Date.now().toString(36);

let PORT = 8000;
const args = process.argv.slice(2);
for (const flag of ['--porta', '--port']) {
  if (args.includes(flag)) PORT = Number(args[args.indexOf(flag) + 1]);
}

const SLUG_RE = /^[A-Za-z0-9-]+$/;
const NODE_RE = /^\d+\.\d+$/;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.md': 'text/markdown; charset=utf-8',
  '.py': 'text/plain; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
};

/* ---------------- progresso.json ---------------- */

function loadProgress() {
  try {
    return JSON.parse(fs.readFileSync(PROGRESS, 'utf-8'));
  } catch {
    return {};
  }
}

function sorted(data) {
  const out = {};
  for (const slug of Object.keys(data).sort()) {
    const nodes = {};
    for (const node of Object.keys(data[slug]).sort()) nodes[node] = data[slug][node];
    out[slug] = nodes;
  }
  return out;
}

function saveProgress(data) {
  const tmp = PROGRESS + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(sorted(data), null, 2) + '\n', 'utf-8');
  fs.renameSync(tmp, PROGRESS);
}

/* ---------------- live reload (SSE) ---------------- */

const clients = new Set();

const RELOAD_SNIPPET =
  '<script>(()=>{let b=null;const es=new EventSource("/api/livereload");' +
  'es.onmessage=e=>{let d;try{d=JSON.parse(e.data)}catch(_){return}' +
  'if(b===null){b=d.boot;return}if(d.boot!==b||d.reload)location.reload()};})();</script>';

function serveSSE(req, res) {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });
  res.write(`data: ${JSON.stringify({ boot: BOOT })}\n\n`);
  clients.add(res);
  req.on('close', () => clients.delete(res));
}

function broadcast(payload) {
  const msg = `data: ${JSON.stringify({ boot: BOOT, ...payload })}\n\n`;
  for (const res of clients) res.write(msg);
}

setInterval(() => {
  for (const res of clients) res.write(': hb\n\n');
}, 30000).unref();

/* ---------------- watcher + geração ---------------- */

const timers = new Map();
function debounce(key, ms, fn) {
  clearTimeout(timers.get(key));
  timers.set(key, setTimeout(fn, ms));
}

let chain = Promise.resolve();
function enqueue(cmds) {
  chain = chain
    .then(() => runSeq(cmds))
    .then((ok) => {
      if (ok) broadcast({ reload: 1 });
    });
}

function runSeq(cmds) {
  return cmds.reduce(
    (p, cmd) =>
      p.then(
        (ok) =>
          new Promise((res) => {
            if (!ok) return res(false);
            console.log(`[watcher] python3 ${cmd.join(' ')}`);
            const child = spawn('python3', cmd, { cwd: ROOT, stdio: 'inherit' });
            child.on('close', (code) => res(code === 0));
            child.on('error', (err) => {
              console.error(`[watcher] falha ao rodar python3: ${err.message}`);
              res(false);
            });
          })
      ),
    Promise.resolve(true)
  );
}

function genFor(mdAbs) {
  const rel = path.relative(ROOT, mdAbs);
  if (rel.endsWith('-ROADMAP.md')) {
    return [
      ['scripts/generate_html.py', rel],
      ['scripts/generate_index.py'],
    ];
  }
  if (rel.endsWith('GLOSSARIO.md')) {
    return [['scripts/generate_glossary_html.py', rel]];
  }
  return null;
}

function regenAll() {
  const cmds = [];
  for (const dir of fs.readdirSync(ROADMAPS)) {
    const sub = path.join(ROADMAPS, dir);
    try {
      if (!fs.statSync(sub).isDirectory()) continue;
    } catch {
      continue;
    }
    for (const f of fs.readdirSync(sub)) {
      const rel = path.join('roadmaps', dir, f);
      if (f.endsWith('-ROADMAP.md')) cmds.push(['scripts/generate_html.py', rel]);
      if (f.endsWith('GLOSSARIO.md')) cmds.push(['scripts/generate_glossary_html.py', rel]);
    }
  }
  cmds.push(['scripts/generate_index.py']);
  return cmds;
}

function onRoadmapsChange(event, filename) {
  if (!filename) return;
  const abs = path.join(ROADMAPS, filename);
  if (filename.endsWith('.md')) {
    const cmds = genFor(abs);
    if (cmds) debounce('md:' + filename, 250, () => enqueue(cmds));
  } else if (filename.endsWith('.html')) {
    // cobre regeneração manual via CLI (python3 scripts/generate_*.py)
    debounce('html:' + filename, 250, () => broadcast({ reload: 1 }));
  }
}

try {
  fs.watch(ROADMAPS, { recursive: true }, onRoadmapsChange);
} catch {
  // plataformas sem watch recursivo: vigia cada subpasta existente
  fs.watch(ROADMAPS, onRoadmapsChange);
  for (const dir of fs.readdirSync(ROADMAPS)) {
    const sub = path.join(ROADMAPS, dir);
    try {
      if (fs.statSync(sub).isDirectory()) fs.watch(sub, onRoadmapsChange);
    } catch {
      /* pasta removida entre a listagem e o watch */
    }
  }
}

fs.watch(SCRIPTS, (event, filename) => {
  if (filename && filename.endsWith('.py')) {
    debounce('scripts', 400, () => enqueue(regenAll()));
  }
});

fs.watch(ROOT, (event, filename) => {
  if (filename === 'index.html') {
    debounce('index', 250, () => broadcast({ reload: 1 }));
  }
});

/* ---------------- HTTP ---------------- */

function sendJson(res, obj, status = 200) {
  const body = Buffer.from(JSON.stringify(obj), 'utf-8');
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': body.length,
  });
  res.end(body);
}

function handleProgressPost(req, res) {
  let body = '';
  req.on('data', (chunk) => {
    body += chunk;
    if (body.length > 1e6) req.destroy();
  });
  req.on('end', () => {
    let roadmap, node, done;
    try {
      ({ roadmap, node, done } = JSON.parse(body));
      done = Boolean(done);
      if (!SLUG_RE.test(roadmap) || !NODE_RE.test(node)) throw 0;
    } catch {
      return sendJson(res, { erro: 'payload inválido' }, 400);
    }
    const data = loadProgress();
    const nodes = data[roadmap] || (data[roadmap] = {});
    if (done) {
      nodes[node] = true;
    } else {
      delete nodes[node];
      if (!Object.keys(nodes).length) delete data[roadmap];
    }
    saveProgress(data);
    sendJson(res, { ok: true });
  });
}

function serveStatic(req, res, urlPath) {
  let filePath = path.normalize(path.join(ROOT, urlPath));
  if (filePath !== ROOT && !filePath.startsWith(ROOT + path.sep)) {
    res.writeHead(403);
    return res.end('forbidden');
  }
  try {
    if (fs.statSync(filePath).isDirectory()) filePath = path.join(filePath, 'index.html');
  } catch {
    /* stat falhou: cai no 404 abaixo */
  }
  const ext = path.extname(filePath).toLowerCase();
  let content;
  try {
    content = fs.readFileSync(filePath);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    return res.end('não encontrado');
  }
  if (ext === '.html') {
    const html = content.toString('utf-8');
    content = Buffer.from(
      html.includes('</body>') ? html.replace('</body>', RELOAD_SNIPPET + '</body>') : html,
      'utf-8'
    );
  }
  res.writeHead(200, {
    'Content-Type': MIME[ext] || 'application/octet-stream',
    'Content-Length': content.length,
  });
  res.end(content);
}

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  if (urlPath === '/api/progresso') {
    if (req.method === 'GET') return sendJson(res, loadProgress());
    if (req.method === 'POST') return handleProgressPost(req, res);
    return sendJson(res, { erro: 'método não suportado' }, 405);
  }
  if (urlPath === '/api/livereload' && req.method === 'GET') return serveSSE(req, res);
  if (req.method !== 'GET') {
    res.writeHead(405);
    return res.end();
  }
  serveStatic(req, res, urlPath);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`Porta ${PORT} em uso. Rode: node server.js --porta ${PORT + 1}`);
    process.exit(1);
  }
  throw err;
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`\nServidor rodando em http://localhost:${PORT}/`);
  for (const dir of fs.readdirSync(ROADMAPS)) {
    const sub = path.join(ROADMAPS, dir);
    try {
      if (!fs.statSync(sub).isDirectory()) continue;
      for (const f of fs.readdirSync(sub)) {
        if (f.endsWith('.html')) console.log(`  http://localhost:${PORT}/roadmaps/${dir}/${f}`);
      }
    } catch {
      /* ignora pastas inacessíveis */
    }
  }
  console.log('\nWatcher ativo:');
  console.log('  • editar roadmaps/**/*.md  → regenera o HTML e recarrega a página');
  console.log('  • editar scripts/*.py      → regenera tudo e recarrega');
  console.log(`\nProgresso salvo automaticamente em ${PROGRESS}`);
  console.log('Ctrl+C para parar.\n');
});
