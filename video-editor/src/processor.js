'use strict';

const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const OUT = {
  first: path.join(ROOT, 'output', 'frames', 'first'),
  last: path.join(ROOT, 'output', 'frames', 'last'),
  compare: path.join(ROOT, 'output', 'compare'),
  reports: path.join(ROOT, 'output', 'reports'),
  transcoded: path.join(ROOT, 'output', 'transcoded'),
};

function run(cmd, args) {
  return new Promise((resolve, reject) => {
    execFile(cmd, args, { maxBuffer: 1024 * 1024 * 64 }, (err, stdout, stderr) => {
      if (err) {
        err.stderr = String(stderr || '').slice(-2000);
        return reject(err);
      }
      resolve(stdout);
    });
  });
}

const ffprobe = (file) => run('ffprobe', [
  '-v', 'error',
  '-print_format', 'json',
  '-show_format', '-show_streams',
  file,
]);

function baseName(file) {
  return path.basename(file, path.extname(file));
}

function fmtDuration(sec) {
  sec = Number(sec) || 0;
  const h = String(Math.floor(sec / 3600)).padStart(2, '0');
  const m = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
  const s = (sec % 60).toFixed(1).padStart(4, '0');
  return `${h}:${m}:${s}`;
}

function parseFps(rate) {
  if (!rate || rate === '0/0') return 0;
  const [a, b] = rate.split('/').map(Number);
  return b ? a / b : Number(rate) || 0;
}

/** 提取首帧：直接取视频第一帧 */
async function extractFirst(file, outPath, cfg) {
  await run('ffmpeg', [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-i', file,
    '-frames:v', '1',
    '-q:v', String(cfg.frameQuality),
    outPath,
  ]);
}

/** 提取尾帧：优先按 EOF 偏移定位，失败则按总帧数定位 */
async function extractLast(file, outPath, cfg, meta) {
  try {
    await run('ffmpeg', [
      '-y', '-hide_banner', '-loglevel', 'error',
      '-sseof', '-0.1',
      '-i', file,
      '-frames:v', '1',
      '-update', '1',
      '-q:v', String(cfg.frameQuality),
      outPath,
    ]);
    if (fs.existsSync(outPath) && fs.statSync(outPath).size > 0) return;
    throw new Error('sseof produced empty output');
  } catch (e) {
    const fps = meta.fps || 25;
    const dur = Number(meta.duration) || 0;
    const lastIdx = Math.max(0, Math.round(dur * fps) - 1);
    await run('ffmpeg', [
      '-y', '-hide_banner', '-loglevel', 'error',
      '-i', file,
      '-vf', `select='eq(n,${lastIdx})'`,
      '-frames:v', '1',
      '-fps_mode', 'passthrough',
      '-q:v', String(cfg.frameQuality),
      outPath,
    ]);
  }
}

/** 首尾帧左右拼接为一张对比图 */
async function buildCompare(firstPath, lastPath, outPath) {
  await run('ffmpeg', [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-i', firstPath,
    '-i', lastPath,
    '-filter_complex', '[0:v][1:v]hstack=inputs=2',
    '-q:v', '2',
    outPath,
  ]);
}

/** 转码 / 压缩 */
async function transcode(file, outPath, cfg) {
  const t = cfg.transcode;
  const args = [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-i', file,
    '-c:v', t.codec,
    '-crf', String(t.crf),
    '-preset', t.preset,
    '-c:a', t.audioCodec,
    '-b:a', t.audioBitrate,
    '-movflags', '+faststart',
  ];
  if (t.scale) args.push('-vf', `scale=${t.scale}`);
  args.push(outPath);
  await run('ffmpeg', args);
}

/**
 * 处理单个视频：报告 → 首帧 → 尾帧 → 对比图 → 转码
 * @returns {{name, files, meta}}
 */
async function processVideo(file, cfg) {
  const name = baseName(file);
  const ext = path.extname(file).toLowerCase();
  const out = {
    name,
    source: file,
    report: path.join(OUT.reports, `${name}.json`),
    first: path.join(OUT.first, `${name}.${cfg.frameFormat}`),
    last: path.join(OUT.last, `${name}.${cfg.frameFormat}`),
    compare: path.join(OUT.compare, `${name}.png`),
    transcoded: path.join(OUT.transcoded, `${name}.mp4`),
    compareFile: null,
    transcodeFile: null,
    steps: {},
  };

  // 1. 视频信息报告
  const probe = JSON.parse(await ffprobe(file));
  const vStream = (probe.streams || []).find((s) => s.codec_type === 'video') || {};
  const meta = {
    file: path.basename(file),
    path: file,
    container: (probe.format && probe.format.format_name) || '',
    sizeBytes: Number((probe.format && probe.format.size) || 0),
    durationSec: Number((probe.format && probe.format.duration) || 0),
    duration: fmtDuration((probe.format && probe.format.duration) || 0),
    bitRateKbps: Math.round(Number((probe.format && probe.format.bit_rate) || 0) / 1000),
    width: vStream.width || null,
    height: vStream.height || null,
    resolution: vStream.width ? `${vStream.width}x${vStream.height}` : null,
    fps: Number((vStream.avg_frame_rate && parseFps(vStream.avg_frame_rate)) || 0).toFixed(3),
    videoCodec: vStream.codec_name || null,
    pixelFormat: vStream.pix_fmt || null,
    audioCodec: ((probe.streams || []).find((s) => s.codec_type === 'audio') || {}).codec_name || null,
    extractedAt: new Date().toISOString(),
  };
  fs.writeFileSync(out.report, JSON.stringify({ meta, source: probe }, null, 2));
  out.steps.report = 'ok';

  // 2 & 3. 首尾帧
  await extractFirst(file, out.first, cfg);
  out.steps.firstFrame = 'ok';
  await extractLast(file, out.last, cfg, meta);
  out.steps.lastFrame = 'ok';

  // 4. 拼接对比图
  if (cfg.compare && cfg.compare.enabled) {
    await buildCompare(out.first, out.last, out.compare);
    out.steps.compare = 'ok';
    out.compareFile = out.compare;
  }

  // 5. 转码 / 压缩
  if (cfg.transcode && cfg.transcode.enabled && ext !== '.gif') {
    await transcode(file, out.transcoded, cfg);
    out.steps.transcode = 'ok';
    out.transcodeFile = out.transcoded;
  }

  out.meta = meta;
  return out;
}

/** 判断某视频是否已处理完成（以报告文件存在为准） */
function isProcessed(file, cfg) {
  const report = path.join(OUT.reports, `${baseName(file)}.json`);
  if (!fs.existsSync(report)) return false;
  const first = path.join(OUT.first, `${baseName(file)}.${cfg.frameFormat}`);
  return fs.existsSync(first);
}

module.exports = { processVideo, isProcessed, OUT, ROOT };
