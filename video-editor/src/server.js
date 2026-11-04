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

/** 汇总所有已处理视频（以 reports 为准，兼容源文件已被移走的情况） */
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
<title>视频首尾帧工作台</title>
<style>
  :root { --bg:#0f1115; --card:#171a21; --line:#262b36; --fg:#e6e9f0; --dim:#8b93a5; --acc:#4f8cff; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg); font:14px/1.6 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }
  header { position:sticky; top:0; z-index:5; display:flex; gap:16px; align-items:center; padding:14px 24px;
           background:rgba(15,17,21,.92); backdrop-filter:blur(8px); border-bottom:1px solid var(--line); }
  h1 { font-size:17px; margin:0; font-weight:600; }
  .tag { font-size:12px; color:var(--dim); border:1px solid var(--line); padding:2px 10px; border-radius:99px; }
  .tag.on { color:#5ed39a; border-color:#2b5c46; }
  main { max-width:1180px; margin:0 auto; padding:24px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:20px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
  .card .cover { position:relative; display:block; background:#000; aspect-ratio:16/7; }
  .card .cover img { width:100%; height:100%; object-fit:contain; display:block; }
  .card .cover .ph { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; color:var(--dim); }
  .body { padding:14px 16px 16px; }
  .name { font-size:15px; font-weight:600; word-break:break-all; }
  .chips { display:flex; flex-wrap:wrap; gap:6px; margin:10px 0 12px; }
  .chip { font-size:12px; color:var(--dim); background:#12151c; border:1px solid var(--line); padding:1px 8px; border-radius:6px; }
  .thumbs { display:flex; gap:10px; margin-bottom:12px; }
  .thumbs a { flex:1; border:1px solid var(--line); border-radius:8px; overflow:hidden; background:#000; }
  .thumbs img { width:100%; display:block; aspect-ratio:16/9; object-fit:cover; }
  .thumbs span { display:block; font-size:11px; color:var(--dim); text-align:center; padding:3px; background:#12151c; }
  .btns { display:flex; flex-wrap:wrap; gap:8px; }
  a.btn { font-size:12px; text-decoration:none; color:var(--fg); border:1px solid var(--line);
          padding:5px 11px; border-radius:8px; background:#12151c; }
  a.btn:hover { border-color:var(--acc); color:var(--acc); }
  .empty { text-align:center; color:var(--dim); padding:80px 0; }
  .empty code { background:#12151c; padding:2px 8px; border-radius:6px; border:1px solid var(--line); }
  footer { text-align:center; color:var(--dim); font-size:12px; padding:24px; }
</style>
</head>
<body>
<header>
  <h1>视频首尾帧工作台</h1>
  <span class="tag on" id="watchTag">监控中</span>
  <span class="tag" id="countTag">0 个视频</span>
  <span class="tag">把 AI 视频丢进 input/ 即可</span>
</header>
<main>
  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" style="display:none">
    还没有视频。把视频文件放进 <code>${'input/'}</code> 文件夹，程序会自动提取首尾帧。
  </div>
</main>
<footer>首帧 / 尾帧 / 对比图 / 信息报告 / 转码 — 各自独立存放于 output/ 子文件夹</footer>
<script>
const D = (u) => u + (u.includes('?') ? '&' : '?') + 'download=1';
async function load() {
  const res = await fetch('/api/videos');
  const list = await res.json();
  const grid = document.getElementById('grid');
  document.getElementById('countTag').textContent = list.length + ' 个视频';
  document.getElementById('empty').style.display = list.length ? 'none' : 'block';
  grid.innerHTML = list.map(v => {
    const l = v.links, m = v.meta || {};
    const cover = l.compare ? '<img src="/'+l.compare+'" alt="对比图">'
      : l.first ? '<img src="/'+l.first+'" alt="首帧">'
      : '<div class="ph">处理中…</div>';
    const btn = (href, text) => href ? '<a class="btn" href="/'+D(href)+'" download>'+text+'</a>' : '';
    return '<div class="card">'
      + '<a class="cover" href="/'+(l.compare||l.first||'')+'" target="_blank">'+cover+'</a>'
      + '<div class="body">'
      + '<div class="name">'+v.name+'</div>'
      + '<div class="chips">'
      + '<span class="chip">时长 '+(m.duration||'?')+'</span>'
      + '<span class="chip">分辨率 '+(m.resolution||'?')+'</span>'
      + '<span class="chip">'+(m.fps||'?')+' fps</span>'
      + '<span class="chip">'+(m.videoCodec||'?')+'</span>'
      + '<span class="chip">'+v.size+'</span>'
      + '</div>'
      + '<div class="thumbs">'
      + (l.first ? '<a href="/'+l.first+'" target="_blank"><img src="/'+l.first+'"><span>首帧</span></a>' : '')
      + (l.last ? '<a href="/'+l.last+'" target="_blank"><img src="/'+l.last+'"><span>尾帧</span></a>' : '')
      + '</div>'
      + '<div class="btns">'
      + btn(l.first,'下载首帧') + btn(l.last,'下载尾帧') + btn(l.compare,'下载对比图')
      + btn(l.report,'报告 JSON') + btn(l.transcode,'转码视频') + btn(l.source,'原视频')
      + '</div></div></div>';
  }).join('');
}
load();
setInterval(load, 3000);
</script>
</body>
</html>`;

function createServer(opts) {
  const server = http.createServer((req, res) => {
    const u = url.parse(req.url, true);
    const pathname = decodeURIComponent(u.pathname);

    if (pathname === '/' || pathname === '/index.html') {
      res.writeHead(200, { 'Content-Type': MIME['.html'] });
      return res.end(PAGE);
    }

    if (pathname === '/api/videos') {
      res.writeHead(200, { 'Content-Type': MIME['.json'], 'Cache-Control': 'no-store' });
      return res.end(JSON.stringify(listVideos()));
    }

    if (pathname.startsWith('/files/')) {
      const rel = pathname.slice('/files/'.length);
      const target = safeJoin(ROOT, rel);
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
