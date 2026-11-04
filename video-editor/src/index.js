'use strict';

const fs = require('fs');
const path = require('path');
const { processVideo, isProcessed, ROOT } = require('./processor');
const { createServer } = require('./server');

const CFG_PATH = path.join(ROOT, 'config.json');
const INPUT = path.join(ROOT, 'input');
const LOG_FILE = path.join(ROOT, 'logs', 'process.log');

// ---------- 配置 ----------
function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(CFG_PATH, 'utf8'));
  } catch (e) {
    console.error('读取 config.json 失败：' + e.message);
    process.exit(1);
  }
}

// ---------- 参数 ----------
const argv = process.argv.slice(2);
const opts = { once: false, watch: true, server: true, port: null, paths: [] };
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--once') opts.once = true;
  else if (a === '--no-watch') opts.watch = false;
  else if (a === '--no-server') opts.server = false;
  else if (a === '--port') opts.port = Number(argv[++i]);
  else if (a === '-h' || a === '--help') {
    console.log([
      '用法: node src/index.js [视频或文件夹路径...] [选项]',
      '',
      '选项:',
      '  --once        处理完命令行参数/已有 input 文件后退出（不常驻监控）',
      '  --no-watch    不监控 input/ 文件夹',
      '  --no-server   不启动网页服务',
      '  --port <n>    指定网页端口（默认读 config.json）',
      '',
      '不带参数启动 = 常驻模式：监控 input/ + 网页查看/下载。',
    ].join('\n'));
    process.exit(0);
  } else opts.paths.push(path.resolve(a));
}

const cfg = loadConfig();
if (opts.port) cfg.port = opts.port;

// ---------- 目录 ----------
for (const d of [
  INPUT,
  path.join(ROOT, 'output', 'frames', 'first'),
  path.join(ROOT, 'output', 'frames', 'last'),
  path.join(ROOT, 'output', 'compare'),
  path.join(ROOT, 'output', 'reports'),
  path.join(ROOT, 'output', 'transcoded'),
  path.join(ROOT, 'logs'),
]) fs.mkdirSync(d, { recursive: true });

// ---------- 日志 ----------
function log(msg) {
  const line = `[${new Date().toLocaleString('zh-CN', { hour12: false })}] ${msg}`;
  console.log(line);
  try { fs.appendFileSync(LOG_FILE, line + '\n'); } catch {}
}

// ---------- 处理队列（串行，避免并发打满 CPU） ----------
let chain = Promise.resolve();
const inFlight = new Set();
const failed = new Map();

function enqueue(file, reason) {
  const key = path.resolve(file);
  if (inFlight.has(key)) return;
  inFlight.add(key);
  chain = chain.then(async () => {
    const name = path.basename(key);
    try {
      if (isProcessed(key, cfg) && reason === 'watch') {
        log(`跳过（已处理）: ${name}`);
        return;
      }
      log(`开始处理: ${name}`);
      const t0 = Date.now();
      const out = await processVideo(key, cfg);
      const steps = Object.keys(out.steps).join(', ');
      log(`完成 ${name}（${((Date.now() - t0) / 1000).toFixed(1)}s）→ ${steps}`);
      failed.delete(key);
    } catch (e) {
      failed.set(key, e.message || String(e));
      log(`失败 ${name}: ${(e.stderr || e.message || e).toString().split('\n').slice(-3).join(' | ')}`);
    } finally {
      inFlight.delete(key);
    }
  });
}

// ---------- 收集要处理的文件 ----------
function isSupported(f) {
  return cfg.supported.includes(path.extname(f).toLowerCase());
}

function collectFiles(p) {
  const st = fs.statSync(p);
  if (st.isFile()) return isSupported(p) ? [p] : [];
  return fs.readdirSync(p)
    .filter((f) => isSupported(f))
    .map((f) => path.join(p, f));
}

// ---------- 监控 input/（按文件体积稳定判断下载完成） ----------
const trackers = new Map(); // file -> {size, stable, done}

function scanInput() {
  let names = [];
  try { names = fs.readdirSync(INPUT); } catch { return; }
  const current = new Set();

  for (const f of names) {
    const full = path.join(INPUT, f);
    if (!isSupported(f)) continue;
    current.add(full);

    let st;
    try { st = fs.statSync(full); } catch { continue; }

    const done = isProcessed(full, cfg) || failed.has(full) || inFlight.has(full);
    if (done) { trackers.delete(full); continue; }

    const t = trackers.get(full) || { size: -1, stable: 0 };
    if (st.size === t.size && st.size > 0) t.stable += 1;
    else { t.size = st.size; t.stable = 0; }
    trackers.set(full, t);

    if (t.stable >= cfg.stableChecks) {
      trackers.delete(full);
      enqueue(full, 'watch');
    }
  }

  // 清理已移走的文件记录
  for (const key of trackers.keys()) if (!current.has(key)) trackers.delete(key);
}

// ---------- 启动 ----------
(async function main() {
  log('======== 视频编辑器启动 ========');
  log(`目录: input/ → output/{frames/first, frames/last, compare, reports, transcoded}`);

  // 1. 处理命令行指定的文件 / 文件夹
  for (const p of opts.paths) {
    if (!fs.existsSync(p)) { log(`路径不存在，跳过: ${p}`); continue; }
    for (const f of collectFiles(p)) enqueue(f, 'cli');
  }
  await chain;

  // 2. 启动网页服务
  if (opts.server) {
    try {
      await createServer({ port: cfg.port, onUploaded: (f) => enqueue(f, 'upload') });
      log(`网页查看/下载: http://localhost:${cfg.port}`);
    } catch (e) {
      log(`网页服务启动失败: ${e.message}`);
    }
  }

  // 3. 监控 input/
  if (opts.watch) {
    log(`监控中: 把 AI 视频放进 ${path.relative(process.cwd(), INPUT) || 'input/'}/ 即可自动处理`);
    scanInput();
    const timer = setInterval(scanInput, cfg.scanIntervalMs);

    if (opts.once) {
      // --once：等所有现有文件处理完再退出
      const waitDone = setInterval(async () => {
        if (trackers.size === 0 && inFlight.size === 0) {
          await chain;
          clearInterval(waitDone);
          clearInterval(timer);
          log('一次性处理完成，退出。');
          process.exit(0);
        }
      }, 500);
    }
  } else if (opts.once) {
    await chain;
    log('处理完成，退出。');
    process.exit(0);
  }
})();
