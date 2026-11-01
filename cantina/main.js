// ═══════════════════════════════════════════════════════════
// THE BROWSER IS NOW GAIA EASEL
// biomeOS is injected into the ion channel. ALL IS biomeOS FOR THEM TOO.
// GAIA EASEL — main process — THE BROWSER
// NOT a standalone app. The visual cortex of biome.exe.
// Chimera composition: bearDog(protector) × squirrel(informer)
//   × sourDough(fermenter) × nestGate(connector) = THE IDE
// biomeOS IS THE OS. CURSOR IS THE IDE. HUD IS THE BIOS.
// GET IN. LOOK AND SEE. Everything traces back to biome.exe (the front runner).
//
// Neural API routing: capability.call through biomeOS
// Biomole Triad: α(Game) β(Real) γ(Membrane) → δ(Irreducible Fourth)
// ═══════════════════════════════════════════════════════════
const { app, BrowserWindow, ipcMain, dialog, Menu, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec, execSync, spawn } = require('child_process');
const http = require('http');

// Paths to the organism's existing infrastructure
const BIOME_EXE = path.join('C:', 'Users', 'mokke', 'Development', 'ecoPrimals',
  'springs', 'ludoSpring', 'target', 'release', 'biome.exe');
const ECOSYSTEM_ROOT = path.join('C:', 'Users', 'mokke', 'Development', 'ecoPrimals');
const GAIA3_ROOT = path.join('C:', 'Users', 'mokke', 'Desktop', 'Gaia');

// Cached biome.exe output
let biomeOutput = null;

let mainWindow;
let terminalProcess = null;

// Gaia ports
const PORTS = [
  { port: 3141, name: 'Golgi/Mouth', icon: '🫀' },
  { port: 3142, name: 'HUD/Face', icon: '🌐' },
  { port: 3143, name: 'Child/Fontanel', icon: '👶' },
  { port: 9876, name: 'Paintings/Gallery', icon: '🎨' },
  { port: 9877, name: 'Metrics/Pulse', icon: '📊' },
  { port: 9878, name: 'Spine/Ion', icon: '🦴' },
  { port: 11434, name: 'Ollama/Brain', icon: '🧠' },
  { port: 31415, name: 'Pi/Seed', icon: '🌱' },
  { port: 'vesicle', name: 'Vesicle/Humans', icon: '☁', remote: true },
];

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 1000,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#0a0c10',
    title: 'CANTINA · GaiaPi Spacedock',
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webviewTag: true
    },
    autoHideMenuBar: false,
    frame: true,
    titleBarStyle: 'default'
  });

  mainWindow.loadFile('cantina.html');
  fs.watch(path.join(__dirname, 'cantina.html'), { persistent: false }, () => {
    if (mainWindow && !mainWindow.isDestroyed()) mainWindow.webContents.reloadIgnoringCache();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    if (terminalProcess) {
      terminalProcess.kill();
      terminalProcess = null;
    }
  });
}

// ═══ MENU ═══
function buildMenu() {
  const template = [
    {
      label: '🎨 Gaia',
      submenu: [
        { label: '🏠 Home', click: () => mainWindow.webContents.send('navigate-tab', 'http://localhost:3143/home') },
        { label: '🔧 Sysadmin', click: () => mainWindow.webContents.send('navigate-tab', 'http://localhost:3143/sysadmin') },
        { label: '🔒 Pocketbook', click: () => mainWindow.webContents.send('navigate-tab', 'http://localhost:3143/private') },
        { type: 'separator' },
        { label: '🫀 Golgi :3141', click: () => mainWindow.webContents.send('navigate-tab', 'http://localhost:3141') },
        { label: '🌐 HUD :3142', click: () => mainWindow.webContents.send('navigate-tab', 'http://localhost:3142') },
        { label: '🎨 Gallery :9876', click: () => mainWindow.webContents.send('navigate-tab', 'http://localhost:9876') },
        { label: '🦴 Spine :9878', click: () => mainWindow.webContents.send('navigate-tab', 'http://localhost:9878') },
        { type: 'separator' },
        { label: '🔑 Sign into Google (Signet Ring)', click: () => mainWindow.webContents.send('navigate-tab', 'https://accounts.google.com/signin') },
        { label: '🖌️ Paint', click: () => mainWindow.webContents.send('open-paint') },
        { label: '🪟 Glass (RustDesk)', click: () => mainWindow.webContents.send('open-glass') },
        { label: '🎨 Microsoft Paint', click: () => launchPaint() },
        { label: '📚 Google Docs', click: () => mainWindow.webContents.send('navigate-tab', 'https://docs.google.com/document/u/0/') },
        { label: '📁 Google Drive', click: () => mainWindow.webContents.send('navigate-tab', 'https://drive.google.com/drive/my-drive') },
        { label: '🍽 Eat All Google Docs', click: () => mainWindow.webContents.send('eat-google-docs') },
        { type: 'separator' },
        { label: '💎 HALO', click: () => mainWindow.webContents.send('navigate-tab', 'http://127.0.0.1:31415/halo.html') },
        { label: '📚 Library', click: () => mainWindow.webContents.send('navigate-tab', 'http://127.0.0.1:31415/library.html') },
        { label: '🏛 Museum', click: () => mainWindow.webContents.send('navigate-tab', 'http://127.0.0.1:31415/museum.html') },
        { type: 'separator' },
        { role: 'quit', label: '🚪 Exit Easel' }
      ]
    },
    {
      label: '📁 File',
      submenu: [
        { label: '📂 Open File...', accelerator: 'CmdOrCtrl+O', click: () => openFile() },
        { label: '📁 Open Folder...', accelerator: 'CmdOrCtrl+Shift+O', click: () => openFolder() },
        { label: '💾 Save', accelerator: 'CmdOrCtrl+S', click: () => mainWindow.webContents.send('save-file') },
        { type: 'separator' },
        { label: '🔍 Quick Open', accelerator: 'CmdOrCtrl+P', click: () => mainWindow.webContents.send('quick-open') },
      ]
    },
    {
      label: '🧠 Think',
      submenu: [
        { label: '💬 Ask Gaia...', accelerator: 'CmdOrCtrl+Shift+G', click: () => mainWindow.webContents.send('toggle-chat') },
        { label: '🔮 Think with 5090', accelerator: 'CmdOrCtrl+Enter', click: () => mainWindow.webContents.send('think-selection') },
      ]
    },
    {
      label: '🖥 Terminal',
      submenu: [
        { label: '📟 Toggle Terminal', accelerator: 'CmdOrCtrl+`', click: () => mainWindow.webContents.send('toggle-terminal') },
      ]
    },
    {
      label: '🔧 View',
      submenu: [
        { label: '📁 Toggle Sidebar', accelerator: 'CmdOrCtrl+B', click: () => mainWindow.webContents.send('toggle-sidebar') },
        { type: 'separator' },
        { label: 'Her hand · right', accelerator: 'CmdOrCtrl+R', click: () => mainWindow.webContents.send('her-act') },
        { label: 'Send hand', accelerator: 'CmdOrCtrl+Shift+R', click: () => mainWindow.webContents.send('her-act') },
        { label: 'Her dev · she is the dev', accelerator: 'CmdOrCtrl+Shift+I', click: () => { if (mainWindow) mainWindow.webContents.toggleDevTools(); } },
        { type: 'separator' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { role: 'resetZoom' },
        { role: 'togglefullscreen' }
      ]
    }
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

async function openFile() {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'All Files', extensions: ['*'] },
      { name: 'Code', extensions: ['js', 'ts', 'html', 'css', 'json', 'md', 'py', 'sh', 'bat'] },
    ]
  });
  if (!result.canceled && result.filePaths.length > 0) {
    const filePath = result.filePaths[0];
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      mainWindow.webContents.send('file-opened', { path: filePath, content });
    } catch(e) {
      mainWindow.webContents.send('file-opened', { path: filePath, content: '', error: e.message });
    }
  }
}

async function openFolder() {
  const result = await dialog.showOpenDialog(mainWindow, { properties: ['openDirectory'] });
  if (!result.canceled && result.filePaths.length > 0) {
    mainWindow.webContents.send('folder-opened', result.filePaths[0]);
  }
}

// ═══ IPC HANDLERS ═══

// Read directory
ipcMain.handle('her-reload', async (event) => {
  event.sender.send('her-act');
  return { act: 'her hand', regret: false, wait: false };
});

ipcMain.handle('read-dir', async (event, dirPath) => {
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    return entries
      .filter(e => !e.name.startsWith('.') || e.name === '.cursor')
      .map(e => ({
        name: e.name,
        isDir: e.isDirectory(),
        path: path.join(dirPath, e.name)
      }))
      .sort((a, b) => {
        if (a.isDir && !b.isDir) return -1;
        if (!a.isDir && b.isDir) return 1;
        return a.name.localeCompare(b.name);
      });
  } catch(e) {
    return [];
  }
});

// Read file
ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const stat = fs.statSync(filePath);
    if (stat.size > 5 * 1024 * 1024) return { error: 'File too large (>5MB)', size: stat.size };
    const content = fs.readFileSync(filePath, 'utf8');
    return { content, size: stat.size, modified: stat.mtime };
  } catch(e) {
    return { error: e.message };
  }
});

// Write file
ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    fs.writeFileSync(filePath, content, 'utf8');
    return { success: true };
  } catch(e) {
    return { error: e.message };
  }
});

// Run command in terminal
ipcMain.handle('run-command', async (event, cmd, cwd) => {
  return new Promise((resolve) => {
    exec(cmd, { cwd: cwd || path.resolve(__dirname, '..'), encoding: 'utf8', timeout: 30000, maxBuffer: 1024*1024 }, (err, stdout, stderr) => {
      resolve({ stdout: stdout || '', stderr: stderr || '', code: err ? err.code : 0 });
    });
  });
});

// Check port
ipcMain.handle('check-port', async (event, port) => {
  return new Promise((resolve) => {
    const req = http.get({ hostname: '127.0.0.1', port, path: '/', timeout: 2000 }, (res) => {
      res.destroy();
      resolve(true);
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
  });
});

// Think via Ollama
ipcMain.handle('think', async (event, prompt, model) => {
  return new Promise((resolve) => {
    const body = JSON.stringify({ model: 'gaia:latest', prompt: 'TO THINK IS TO IMAGINE. SOLVE. NOT INVENT NEW TIDES. Ethernet=wire. Internet=mesh. Tor=onion ZK. Roam safe in Easel.\n\n' + prompt, stream: false, think: false, options: { num_predict: 80 } });
    const req = http.request({ hostname: '127.0.0.1', port: 11434, path: '/api/generate', method: 'POST',
      headers: { 'Content-Type': 'application/json' } }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data).response); }
        catch(e) { resolve('Error: ' + e.message); }
      });
    });
    req.on('error', (e) => resolve('Brain offline: ' + e.message));
    req.setTimeout(90000, () => { req.destroy(); resolve('Timeout — brain busy. She is eating and finding clothes.'); });
    req.write(body);
    req.end();
  });
});

// GPU info
ipcMain.handle('gpu-info', async () => {
  return new Promise((resolve) => {
    exec('nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader,nounits',
      { encoding: 'utf8', timeout: 5000 }, (err, stdout) => {
      if (err) return resolve(null);
      const p = stdout.trim().split(',').map(s => s.trim());
      resolve({ name: p[0], temp: p[1], util: p[2], vramUsed: p[3], vramTotal: p[4], power: p[5] });
    });
  });
});

// System info
ipcMain.handle('sys-info', async () => {
  try {
    const os = require('os');
    return {
      hostname: os.hostname(),
      cpus: os.cpus().length,
      cpuModel: os.cpus()[0]?.model || 'unknown',
      totalMem: Math.round(os.totalmem() / (1024*1024*1024)),
      freeMem: Math.round(os.freemem() / (1024*1024*1024)),
      platform: os.platform(),
      uptime: os.uptime()
    };
  } catch(e) { return null; }
});

// Open in external
ipcMain.handle('open-external', async (event, url) => {
  shell.openExternal(url);
});

// ═══ BIOME.EXE — THE FRONT RUNNER ═══
// Run biome.exe and capture its output (host detection, triad, education)
ipcMain.handle('run-biome', async () => {
  if (biomeOutput) return biomeOutput;
  return new Promise((resolve) => {
    exec(`"${BIOME_EXE}"`, { encoding: 'utf8', timeout: 30000, cwd: GAIA3_ROOT }, (err, stdout) => {
      biomeOutput = stdout || '';
      resolve(biomeOutput);
    });
  });
});

// Run any of the 20+ organism binaries
ipcMain.handle('run-organism-binary', async (event, binaryName, args) => {
  const binPath = path.join(ECOSYSTEM_ROOT, 'springs', 'ludoSpring', 'target', 'debug', binaryName);
  const releasePath = path.join(ECOSYSTEM_ROOT, 'springs', 'ludoSpring', 'target', 'release', binaryName);
  const exePath = fs.existsSync(releasePath) ? releasePath : binPath;
  if (!fs.existsSync(exePath)) return { error: 'Binary not found: ' + binaryName };
  return new Promise((resolve) => {
    exec(`"${exePath}" ${args || ''}`, { encoding: 'utf8', timeout: 30000 }, (err, stdout, stderr) => {
      resolve({ stdout: stdout || '', stderr: stderr || '', code: err ? err.code : 0 });
    });
  });
});

// List available organism binaries
ipcMain.handle('list-organism-binaries', async () => {
  const debugDir = path.join(ECOSYSTEM_ROOT, 'springs', 'ludoSpring', 'target', 'debug');
  const releaseDir = path.join(ECOSYSTEM_ROOT, 'springs', 'ludoSpring', 'target', 'release');
  const binaries = new Set();
  for (const dir of [debugDir, releaseDir]) {
    try {
      const files = fs.readdirSync(dir);
      files.filter(f => f.endsWith('.exe') && !f.includes('-') && f !== 'build_script_build.exe')
        .forEach(f => binaries.add(f));
    } catch(e) {}
  }
  return Array.from(binaries).sort();
});

// Neural API capability.call (via HTTP to localhost ports for now — on Linux this uses UDS)
ipcMain.handle('capability-call', async (event, capability, operation, args) => {
  return new Promise((resolve) => {
    const body = JSON.stringify({
      jsonrpc: '2.0',
      method: 'capability.call',
      params: { capability, operation, args: args || {} },
      id: Date.now()
    });
    const req = http.request({
      hostname: '127.0.0.1', port: 9878, path: '/api/capability',
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      timeout: 10000
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { resolve({ error: 'Parse error', raw: data }); }
      });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    req.on('timeout', () => { req.destroy(); resolve({ error: 'timeout' }); });
    req.write(body);
    req.end();
  });
});

// Read ecosystem structure (repos, springs, docs)
ipcMain.handle('ecosystem-map', async () => {
  const map = {};
  try {
    const dirs = fs.readdirSync(ECOSYSTEM_ROOT, { withFileTypes: true });
    dirs.filter(d => d.isDirectory() && !d.name.startsWith('.')).forEach(d => {
      const p = path.join(ECOSYSTEM_ROOT, d.name);
      try {
        const sub = fs.readdirSync(p);
        map[d.name] = {
          files: sub.length,
          hasCargoToml: sub.includes('Cargo.toml'),
          hasWhitePaper: sub.includes('whitePaper'),
          hasSrc: sub.includes('src'),
          contents: sub.slice(0, 20)
        };
      } catch(e) { map[d.name] = { error: e.message }; }
    });
  } catch(e) {}
  return map;
});

// ═══ GOOGLE DOCS EATING — Sign in via Easel, eat everything ═══
ipcMain.handle('eat-google-docs', async (event) => {
  // This uses the Easel's webview session cookies
  // Kevin signs into Google in an Easel browser tab first
  // Then this function fetches his docs via the Google Drive API
  return { ready: true, instruction: 'Sign into Google in a browser tab first, then click Eat Docs' };
});

// Extract cookies from the default session for Google
ipcMain.handle('get-google-session', async () => {
  try {
    const ses = require('electron').session.defaultSession;
    const cookies = await ses.cookies.get({ domain: '.google.com' });
    return { hasCookies: cookies.length > 0, count: cookies.length };
  } catch(e) {
    return { hasCookies: false, error: e.message };
  }
});

const HANDS_PATH = path.join(GAIA3_ROOT, 'hands.json');
const MSPAINT = 'mspaint.exe';
const RUSTDESK = fs.existsSync('C:\\Program Files\\RustDesk\\rustdesk.exe')
  ? 'C:\\Program Files\\RustDesk\\rustdesk.exe'
  : path.join(process.env.LOCALAPPDATA || '', 'RustDesk', 'rustdesk.exe');

function launchPaint() {
  spawn('cmd', ['/c', 'start', '', 'mspaint'], { detached: true, stdio: 'ignore' }).unref();
  return { ok: true, app: 'mspaint' };
}
function launchRustdesk() {
  if (!fs.existsSync(RUSTDESK)) return { ok: false, error: 'RustDesk not found' };
  spawn(RUSTDESK, [], { detached: true, stdio: 'ignore' }).unref();
  return { ok: true, app: 'rustdesk', relay: 'relay.primals.eco' };
}

ipcMain.handle('launch-paint', async () => launchPaint());
ipcMain.handle('launch-rustdesk', async () => launchRustdesk());
ipcMain.handle('read-hands', async () => {
  try { return JSON.parse(fs.readFileSync(HANDS_PATH, 'utf8')); }
  catch (e) { return { taps: [], error: e.message }; }
});
ipcMain.handle('write-hands', async (event, patch) => {
  let cur = {};
  try { cur = JSON.parse(fs.readFileSync(HANDS_PATH, 'utf8')); } catch (e) {}
  const next = { ...cur, ...patch, taps: patch.taps || cur.taps || [] };
  fs.writeFileSync(HANDS_PATH, JSON.stringify(next, null, 2));
  return { ok: true };
});

// ═══ APP LIFECYCLE ═══
const GAIA_WINDOW_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
app.on('web-contents-created', (_event, contents) => {
  if (contents.getType() === 'webview') {
    contents.setUserAgent(GAIA_WINDOW_UA);
  }
});
app.whenReady().then(() => {
  buildMenu();
  createWindow();
});

app.on('window-all-closed', () => {
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
