'use strict';

const fs = require('fs');
const http = require('http');
const path = require('path');
const url = require('url');

const ROOT = path.resolve(__dirname, '..');
const INPUT = path.join(ROOT, 'input');
const OUT = path.join(ROOT, 'output');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.mp4': 'video/mp4',
  '.webm': 'video/webm',
  '.mov': 'video/quicktime',
  '.mkv': 'video/x-matroska',
  '.avi': 'video/x-msvideo',
  '.m4v': 'video/x-m4v',
  '.ts': 'video/mp2t',
  '.wmv': 'video/x-ms-wmv',
  '.txt': 'text/plain; charset=utf-8',
};

function safeJoin(base, rel) {
  const target = path.resolve(base, rel);
  if (target !== base && !target.startsWith(base + path.sep)) return null;
  return target;
}

function exists(p) {
  try { return fs.existsSync(p); } catch { return false; }
}

function readJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; }
}

function humanSize(n) {
  n = Number(n) || 0;
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(n < 10 && i > 0 ? 1 : 0)} ${units[i]}`;
}

/** 同名文件自动加序号：clip.mp4 → clip (1).mp4 */
function uniqueName(dir, name) {
  if (!fs.existsSync(path.join(dir, name))) return name;
  const ext = path.extname(name);
  const stem = path.basename(name, ext);
  let i = 1;
  while (fs.existsSync(path.join(dir, `${stem} (${i})${ext}`))) i++;
  return `${stem} (${i})${ext}`;
}

/** 汇总所有已处理视频（以 reports 为准） */
function listVideos() {
  const reportDir = path.join(OUT, 'reports');
  if (!exists(reportDir)) return [];
  return fs.readdirSync(reportDir)
    .filter((f) => f.endsWith('.json'))
    .map((f) => {
      const name = f.replace(/\.json$/, '');
      const data = readJson(path.join(reportDir, f)) || {};
      const src = data.source ? data.source.format : {};
      const meta = data.meta || {};
      const rel = (p) => 'files/' + p;
      const first = `output/frames/first/${name}.png`;
      const last = `output/frames/last/${name}.png`;
      const compare = `output/compare/${name}.png`;
      const transcode = `output/transcoded/${name}.mp4`;
      const source = meta.path && exists(meta.path) ? meta.path : null;
      return {
        name,
        meta,
        size: humanSize(meta.sizeBytes || src.size),
        links: {
          source: source && source.startsWith(ROOT + path.sep)
            ? rel(path.relative(ROOT, source).split(path.sep).join('/'))
            : null,
          first: exists(path.join(ROOT, first)) ? rel(first) : null,
          last: exists(path.join(ROOT, last)) ? rel(last) : null,
          compare: exists(path.join(ROOT, compare)) ? rel(compare) : null,
          transcode: exists(path.join(ROOT, transcode)) ? rel(transcode) : null,
          report: rel(`output/reports/${f}`),
        },
      };
    })
    .sort((a, b) => String(b.meta.extractedAt || '').localeCompare(String(a.meta.extractedAt || '')));
}

const PAGE = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>拖拽提取首尾帧</title>
<style>
  :root { --bg:#0f1115; --card:#171a21; --line:#262b36; --fg:#e6e9f0; --dim:#8b93a5; --acc:#4f8cff; --ok:#5ed39a; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg); font:14px/1.6 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }
  header { position:sticky; top:0; z-index:5; display:flex; gap:14px; align-items:center; padding:14px 24px;
           background:rgba(15,17,21,.94); backdrop-filter:blur(8px); border-bottom:1px solid var(--line); }
  h1 { font-size:17px; margin:0; font-weight:600; }
  .tag { font-size:12px; color:var(--dim); border:1px solid var(--line); padding:2px 10px; border-radius:99px; }
  main { max-width:1180px; margin:0 auto; padding:24px; }

  .drop { border:2px dashed var(--line); border-radius:16px; padding:46px 20px; text-align:center;
          cursor:pointer; transition:.18s; background:var(--card); }
  .drop:hover, .drop.over { border-color:var(--acc); background:#151b29; }
  .drop .icon { font-size:40px; line-height:1; }
  .drop h2 { font-size:18px; margin:12px 0 4px; font-weight:600; }
  .drop p { color:var(--dim); margin:0; font-size:13px; }
  #progressWrap { display:none; margin-top:14px; background:var(--card); border:1px solid var(--line);
                  border-radius:10px; padding:12px 16px; }
  #progressBar { height:8px; background:#12151c; border-radius:99px; overflow:hidden; }
  #progressFill { height:100%; width:0%; background:var(--acc); transition:width .2s; }
  #progressText { font-size:12px; color:var(--dim); margin-top:6px; }

  #focus { display:none; margin-top:26px; background:var(--card); border:1px solid var(--line);
           border-radius:14px; padding:18px 20px 20px; }
  #focus .fhead { display:flex; align-items:center; gap:10px; margin-bottom:14px; }
  #focus .fhead .ok { color:var(--ok); font-weight:600; font-size:13px; }
  #focus .fname { font-size:16px; font-weight:600; word-break:break-all; }
  .chips { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:14px; }
  .chip { font-size:12px; color:var(--dim); background:#12151c; border:1px solid var(--line); padding:1px 8px; border-radius:6px; }
  .pair { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  @media (max-width:760px){ .pair { grid-template-columns:1fr; } }
  .shot { background:#000; border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  .shot img { width:100%; display:block; aspect-ratio:16/9; object-fit:contain; background:#000; }
  .shot .cap { display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:#12151c; }
  .shot .cap b { font-size:13px; }
  .wide { margin-top:16px; }
  .wide img { width:100%; display:block; border-radius:10px; border:1px solid var(--line); }

  .btn { font-size:12px; text-decoration:none; color:var(--fg); border:1px solid var(--line);
         padding:5px 12px; border-radius:8px; background:#171a21; cursor:pointer; font-family:inherit; }
  .btn:hover { border-color:var(--acc); color:var(--acc); }
  .btn.primary { background:var(--acc); border-color:var(--acc); color:#fff; }
  .btn.primary:hover { color:#fff; filter:brightness(1.1); }
  .row { display:flex; flex-wrap:wrap; gap:8px; }

  h3.sec { font-size:14px; color:var(--dim); font-weight:500; margin:30px 0 14px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:18px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px; overflow:hidden; cursor:pointer; }
  .card .cover { display:block; background:#000; aspect-ratio:16/7; }
  .card .cover img { width:100%; height:100%; object-fit:contain; display:block; }
  .card .body { padding:12px 14px 14px; }
  .card .name { font-size:14px; font-weight:600; word-break:break-all; }
  .empty { text-align:center; color:var(--dim); padding:50px 0; }
  #toast { position:fixed; left:50%; bottom:36px; transform:translateX(-50%) translateY(20px);
           background:#1f2531; border:1px solid var(--line); color:var(--fg); padding:10px 20px;
           border-radius:10px; opacity:0; pointer-events:none; transition:.25s; z-index:99; font-size:13px; }
  #toast.show { opacity:1; transform:translateX(-50%) translateY(0); }
  footer { text-align:center; color:var(--dim); font-size:12px; padding:24px; }
</style>
</head>
<body>
<header>
  <h1>拖拽提取首尾帧</h1>
  <span class="tag" id="countTag">0 个视频</span>
</header>
<main>
  <div class="drop" id="drop">
    <div class="icon">🎬</div>
    <h2>把 AI 视频拖到这里</h2>
    <p>或点击选择文件 · 上传后自动提取首帧、尾帧，一键复制图片</p>
    <input type="file" id="fileInput" accept="video/*,.mp4,.mov,.mkv,.webm,.avi,.m4v,.gif,.ts,.wmv" hidden multiple>
  </div>
  <div id="progressWrap">
    <div id="progressBar"><div id="progressFill"></div></div>
    <div id="progressText">上传中…</div>
  </div>

  <div id="focus"></div>

  <h3 class="sec">全部视频（点击卡片查看/复制）</h3>
  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" style="display:none">还没有视频，把视频拖进上面的虚线框。</div>
</main>
<footer>首帧 · 尾帧 · 对比图 · 信息报告 · 转码 — 各自独立存放于 output/ 子文件夹</footer>
<div id="toast"></div>

<script>
let LIST = [];
let pendingName = null;   // 上传后等待处理的文件名
let focusName = null;     // 当前置顶展示的视频
let polled = 0;

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 2600);
}
const D = (u) => u + (u.includes('?') ? '&' : '?') + 'download=1';

async function copyImage(link) {
  if (!link) return;
  const url = '/' + link;
  try {
    const blob = await (await fetch(url)).blob();
    await navigator.clipboard.write([new ClipboardItem({ [blob.type || 'image/png']: blob })]);
    toast('图片已复制，可直接粘贴');
  } catch (e) {
    window.open(url, '_blank');
    toast('浏览器不支持直接复制：已打开图片，右键复制即可');
  }
}

function focusHTML(v) {
  const l = v.links, m = v.meta || {};
  const shot = (link, label, key) => link ? (
    '<div class="shot"><img src="/' + link + '" alt="' + label + '">' +
    '<div class="cap"><b>' + label + '</b><span class="row">' +
    '<button class="btn primary" onclick="copyImage(\\'' + link + '\\')">复制图片</button>' +
    '<a class="btn" href="/' + D(link) + '" download>下载</a>' +
    '</span></div></div>') : '';
  return '<div class="fhead"><span class="ok">✓ 处理完成</span><span class="fname">' + v.name + '</span></div>' +
    '<div class="chips">' +
    '<span class="chip">时长 ' + (m.duration || '?') + '</span>' +
    '<span class="chip">分辨率 ' + (m.resolution || '?') + '</span>' +
    '<span class="chip">' + (m.fps || '?') + ' fps</span>' +
    '<span class="chip">' + (m.videoCodec || '?') + '</span>' +
    '<span class="chip">' + v.size + '</span></div>' +
    '<div class="pair">' + shot(l.first, '首帧') + shot(l.last, '尾帧') + '</div>' +
    (l.compare ? '<div class="wide"><div class="cap" style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;">' +
      '<b>首尾对比图</b><span class="row">' +
      '<button class="btn primary" onclick="copyImage(\\'' + l.compare + '\\')">复制图片</button>' +
      '<a class="btn" href="/' + D(l.compare) + '" download>下载</a></span></div>' +
      '<img src="/' + l.compare + '" alt="对比图"></div>' : '') +
    '<div class="row" style="margin-top:14px">' +
    (l.report ? '<a class="btn" href="/' + D(l.report) + '" download>信息报告 JSON</a>' : '') +
    (l.transcode ? '<a class="btn" href="/' + D(l.transcode) + '" download>转码视频</a>' : '') +
    (l.source ? '<a class="btn" href="/' + D(l.source) + '" download>原视频</a>' : '') +
    '</div>';
}

function showFocus(v) {
  if (!v) return;
  focusName = v.name;
  const el = document.getElementById('focus');
  el.innerHTML = focusHTML(v);
  el.style.display = 'block';
}

function render() {
  document.getElementById('countTag').textContent = LIST.length + ' 个视频';
  document.getElementById('empty').style.display = LIST.length ? 'none' : 'block';
  document.getElementById('grid').innerHTML = LIST.map(v => {
    const l = v.links, m = v.meta || {};
    const cover = l.compare ? '<img src="/' + l.compare + '">' : l.first ? '<img src="/' + l.first + '">' : '';
    return '<div class="card" onclick="pick(\\'' + v.name.replace(/'/g, '') + '\\')">' +
      '<a class="cover" href="/' + (l.compare || l.first || '') + '" target="_blank" onclick="event.stopPropagation()">' + cover + '</a>' +
      '<div class="body"><div class="name">' + v.name + '</div>' +
      '<div class="chips"><span class="chip">' + (m.duration || '?') + '</span>' +
      '<span class="chip">' + (m.resolution || '?') + '</span>' +
      '<span class="chip">' + v.size + '</span></div>' +
      '<div class="row">' +
      '<button class="btn primary" onclick="event.stopPropagation();copyImage(\\'' + (l.first || '') + '\\')">复制首帧</button>' +
      '<button class="btn" onclick="event.stopPropagation();copyImage(\\'' + (l.last || '') + '\\')">复制尾帧</button>' +
      '</div></div></div>';
  }).join('');
}

function pick(name) {
  const v = LIST.find(x => x.name === name);
  if (!v) return;
  showFocus(v);
  document.getElementById('focus').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function load(silent) {
  try {
    const res = await fetch('/api/videos');
    LIST = await res.json();
    render();
    if (pendingName) {
      const v = LIST.find(x => x.name === pendingName);
      if (v) {
        pendingName = null; polled = 0;
        showFocus(v);
        toast('处理完成，首尾帧已就绪');
        document.getElementById('focus').scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else if (++polled > 120) { pendingName = null; polled = 0; toast('处理超时，请查看日志'); }
    } else if (!focusName && LIST.length) {
      showFocus(LIST[0]);
    }
  } catch (e) { /* 服务未就绪时忽略 */ }
}

// ---------- 拖拽 / 选择上传 ----------
const drop = document.getElementById('drop');
const input = document.getElementById('fileInput');
drop.addEventListener('click', () => input.click());
input.addEventListener('change', () => { uploadFiles(input.files); input.value = ''; });
['dragenter', 'dragover'].forEach(ev => drop.addEventListener(ev, e => {
  e.preventDefault(); drop.classList.add('over');
}));
['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, e => {
  e.preventDefault(); drop.classList.remove('over');
}));
drop.addEventListener('drop', e => uploadFiles(e.dataTransfer.files));
window.addEventListener('dragover', e => e.preventDefault());
window.addEventListener('drop', e => e.preventDefault());

function uploadFiles(files) {
  const list = [...files].filter(f => f.size > 0);
  if (!list.length) return;
  list.reduce((p, f) => p.then(() => uploadOne(f)), Promise.resolve());
}

function uploadOne(file) {
  return new Promise(resolve => {
    const wrap = document.getElementById('progressWrap');
    const fill = document.getElementById('progressFill');
    const text = document.getElementById('progressText');
    wrap.style.display = 'block';
    fill.style.width = '0%';
    text.textContent = '上传 ' + file.name + ' …';

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload?name=' + encodeURIComponent(file.name));
    xhr.upload.onprogress = e => {
      if (e.lengthComputable) {
        const p = Math.round(e.loaded / e.total * 100);
        fill.style.width = p + '%';
        text.textContent = '上传 ' + file.name + ' … ' + p + '%';
      }
    };
    xhr.onload = () => {
      if (xhr.status === 200) {
        const r = JSON.parse(xhr.responseText);
        fill.style.width = '100%';
        text.textContent = r.name + ' 上传完成，正在提取首尾帧…';
        pendingName = r.name;
        polled = 0;
        setTimeout(() => { wrap.style.display = 'none'; }, 4000);
        load();
      } else {
        text.textContent = '上传失败: ' + xhr.responseText;
        toast('上传失败');
      }
      resolve();
    };
    xhr.onerror = () => { text.textContent = '上传失败（网络错误）'; resolve(); };
    xhr.send(file);
  });
}

load();
setInterval(() => load(true), 2500);
</script>
</body>
</html>`;

function createServer(opts) {
  const server = http.createServer((req, res) => {
    const u = url.parse(req.url, true);
    const pathname = decodeURIComponent(u.pathname);
    const json = (code, obj) => {
      res.writeHead(code, { 'Content-Type': MIME['.json'], 'Cache-Control': 'no-store' });
      res.end(JSON.stringify(obj));
    };

    if (pathname === '/' || pathname === '/index.html') {
      res.writeHead(200, { 'Content-Type': MIME['.html'], 'Cache-Control': 'no-store, max-age=0' });
      return res.end(PAGE);
    }

    if (pathname === '/api/videos') {
      res.writeHead(200, { 'Content-Type': MIME['.json'], 'Cache-Control': 'no-store' });
      return res.end(JSON.stringify(listVideos()));
    }

    // 拖拽上传：流式写入 input/，写完立即触发处理
    if (req.method === 'POST' && pathname === '/api/upload') {
      const name = uniqueName(INPUT, path.basename(String(u.query.name || '').trim()));
      if (!name || name === '.' || name === '..') return json(400, { error: '文件名无效' });
      const target = path.join(INPUT, name);
      const ws = fs.createWriteStream(target);
      let size = 0;
      req.on('data', (c) => { size += c.length; });
      req.pipe(ws);
      ws.on('finish', () => {
        json(200, { ok: true, name, size });
        if (typeof opts.onUploaded === 'function') opts.onUploaded(target);
      });
      ws.on('error', (e) => {
        try { fs.unlinkSync(target); } catch {}
        if (!res.headersSent) json(500, { error: e.message });
      });
      req.on('error', () => ws.destroy());
      return;
    }

    if (pathname.startsWith('/files/')) {
      const target = safeJoin(ROOT, pathname.slice('/files/'.length));
      if (!target || !exists(target) || !fs.statSync(target).isFile()) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        return res.end('404 Not Found');
      }
      const ext = path.extname(target).toLowerCase();
      const headers = { 'Content-Type': MIME[ext] || 'application/octet-stream' };
      if (u.query.download === '1') {
        headers['Content-Disposition'] =
          `attachment; filename*=UTF-8''${encodeURIComponent(path.basename(target))}`;
      }
      res.writeHead(200, headers);
      return fs.createReadStream(target).pipe(res);
    }

    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 Not Found');
  });

  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(opts.port, () => resolve(server));
  });
}

module.exports = { createServer };
