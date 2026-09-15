"""JS compartilhado de persistência de progresso, embutido nos HTML gerados.

ProgressStore grava o progresso direto no progresso.json da raiz usando a
File System Access API (Chrome/Edge) — nenhum servidor nem localStorage. O
handle do arquivo fica salvo no IndexedDB, então a escolha é feita uma vez
por navegador. Fallback: se o navegador não suporta a API, tenta o
scripts/serve.py (/api/progresso); se também falhar, avisa na página.
"""

PROGRESS_JS = r"""
const ProgressStore = (() => {
  const DB = 'ai-structure', STORE = 'handles', KEY = 'progresso';
  const TYPES = [{ description: 'JSON', accept: { 'application/json': ['.json'] } }];
  let mode = null; // 'file' | 'api'
  let handle = null;

  function idb() {
    return new Promise((res, rej) => {
      const r = indexedDB.open(DB, 1);
      r.onupgradeneeded = () => r.result.createObjectStore(STORE);
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
  }
  async function saveHandle(h) {
    const db = await idb();
    return new Promise((res, rej) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).put(h, KEY);
      tx.oncomplete = res;
      tx.onerror = () => rej(tx.error);
    });
  }
  async function loadHandle() {
    try {
      const db = await idb();
      return await new Promise(res => {
        const q = db.transaction(STORE, 'readonly').objectStore(STORE).get(KEY);
        q.onsuccess = () => res(q.result || null);
        q.onerror = () => res(null);
      });
    } catch { return null; }
  }
  async function readFile() {
    if (!handle) return null;
    try {
      const t = await (await handle.getFile()).text();
      return t.trim() ? JSON.parse(t) : {};
    } catch { return null; }
  }
  async function writeFile(data) {
    const w = await handle.createWritable();
    await w.write(JSON.stringify(data, null, 2) + '\n');
    await w.close();
  }
  async function apiRead() {
    const r = await fetch('/api/progresso');
    if (!r.ok) throw 0;
    return r.json();
  }

  // init() -> 'ready' | 'connect' | 'regrant' | 'unsupported'
  async function init() {
    if ('showOpenFilePicker' in window) {
      mode = 'file';
      handle = await loadHandle();
      if (!handle) return 'connect';
      try {
        if (await handle.queryPermission({ mode: 'readwrite' }) === 'granted') return 'ready';
      } catch { /* cai no regrant */ }
      return 'regrant';
    }
    try { await apiRead(); mode = 'api'; return 'ready'; }
    catch { return 'unsupported'; }
  }
  async function connect(create) {
    try {
      handle = create
        ? await showSaveFilePicker({ suggestedName: 'progresso.json', types: TYPES })
        : (await showOpenFilePicker({ types: TYPES }))[0];
      await saveHandle(handle);
      if (create) await writeFile((await readFile()) || {});
      mode = 'file';
      return true;
    } catch { return false; }
  }
  async function regrant() {
    try {
      return !!handle && (await handle.requestPermission({ mode: 'readwrite' })) === 'granted';
    } catch { return false; }
  }
  async function read() {
    if (mode === 'file') return await readFile();
    if (mode === 'api') { try { return await apiRead(); } catch { return null; } }
    return null;
  }
  async function setNode(slug, node, done) {
    if (mode === 'file') {
      const data = (await readFile()) || {};
      const nodes = data[slug] || (data[slug] = {});
      if (done) nodes[node] = true;
      else { delete nodes[node]; if (!Object.keys(nodes).length) delete data[slug]; }
      await writeFile(data);
      return;
    }
    if (mode === 'api') {
      const r = await fetch('/api/progresso', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roadmap: slug, node, done }),
      });
      if (!r.ok) throw 0;
      return;
    }
    throw 0;
  }
  return { init, connect, regrant, read, setNode };
})();

// Liga o banner de conexão aos botões e chama onReady(state) quando o
// progresso estiver acessível.
async function wireProgress(banner, onReady) {
  const detail = banner.querySelector('.warn-detail');
  const btns = {
    open: banner.querySelector('[data-act="open"]'),
    create: banner.querySelector('[data-act="create"]'),
    regrant: banner.querySelector('[data-act="regrant"]'),
  };
  function show(visible, msg) {
    banner.style.display = 'block';
    Object.entries(btns).forEach(([k, b]) => { if (b) b.hidden = !visible.includes(k); });
    if (detail) detail.textContent = msg;
  }
  async function ready() {
    const state = (await ProgressStore.read()) || {};
    banner.style.display = 'none';
    onReady(state);
  }
  if (btns.open) btns.open.addEventListener('click', async () => { if (await ProgressStore.connect(false)) ready(); });
  if (btns.create) btns.create.addEventListener('click', async () => { if (await ProgressStore.connect(true)) ready(); });
  if (btns.regrant) btns.regrant.addEventListener('click', async () => { if (await ProgressStore.regrant()) ready(); });
  const status = await ProgressStore.init();
  if (status === 'ready') return ready();
  if (status === 'connect') {
    return show(['open', 'create'], 'Escolha o progresso.json da raiz do projeto (ou crie um). A escolha fica salva.');
  }
  if (status === 'regrant') {
    return show(['regrant'], 'A permissão do arquivo expirou — um clique reconecta.');
  }
  show([], 'Este navegador não grava arquivos (sem File System Access API). Use Chrome/Edge, ou rode python3 scripts/serve.py e abra http://localhost:8000/.');
}
"""

BANNER_HTML = (
    '<p id="savewarn">⚠️ <strong>Progresso não conectado.</strong> '
    '<button data-act="open">Abrir progresso.json</button> '
    '<button data-act="create">Criar na raiz do projeto</button> '
    '<button data-act="regrant">Reconectar progresso.json</button> '
    '<span class="warn-detail"></span></p>'
)

BANNER_CSS = """
  #savewarn { display:none; background:#fee2e2; border:1.5px solid #1a1a1a; border-radius:8px; padding:.5rem .9rem; font-size:.88rem; }
  #savewarn button { font:inherit; font-size:.8rem; font-weight:600; background:#fff; border:1.5px solid #1a1a1a; border-radius:6px; padding:.15rem .6rem; margin:0 .15rem; cursor:pointer; }
  #savewarn .warn-detail { color:#525252; }
"""
