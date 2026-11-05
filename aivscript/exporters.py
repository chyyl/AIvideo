"""导出为魔搭社区（ModelScope）AIGC 专区「生成视频」可用的逐镜提示词。

输出两种文件：
- modelscope_prompts.md   逐镜可直接复制的提示词 + 推荐参数
- modelscope_prompts.json 供批量提交 / 自建脚本消费

注意：魔搭生成视频栏目以「单个提示词 = 一段视频」为单位，
因此这里按镜头展开，并把运镜与动作合进正向提示词。
"""
from __future__ import annotations

import json

from .models import CAMERA_ZH, SHOT_SIZE_ZH, Script

RESOLUTION_MAP = {
    "16:9": "1280×720",
    "9:16": "720×1280",
    "4:3": "1024×768",
    "2.35:1": "1280×544",
}
DEFAULT_NEGATIVE = "畸形手、多余肢体、面部变形、文字水印、低清晰度、画面抖动、塑料质感"
DEFAULT_FPS = 16          # 万相系列常用帧率
MAX_SECONDS = 5.0         # 生成栏目常见单次时长上限


def _sanitize(text: str) -> str:
    for code, zh in CAMERA_ZH.items():
        text = text.replace(f"（{code}）", f"（{zh}）")
    while "，，" in text:
        text = text.replace("，，", "，")
    return text.strip("，。 ")


def _shot_prompt(script: Script, shot) -> str:
    base = shot.image_prompt.zh.strip()
    if not base:
        base = f"{SHOT_SIZE_ZH.get(shot.shot_size, shot.shot_size)}，{shot.subject}，{shot.action}"
    parts = [base]
    if shot.video_prompt and shot.video_prompt not in base:
        parts.append(shot.video_prompt)
    parts.append("画面稳定，主体一致，无镜头切换")
    return _sanitize("，".join(p.strip("，。 ") for p in parts if p.strip()))


def _frame_count(seconds: float, fps: int) -> int:
    # 万相系列按 4n+1 帧生成
    n = max(4, round(seconds * fps / 4))
    return 4 * n + 1


def modelscope_records(script: Script, fps: int = DEFAULT_FPS, max_seconds: float = MAX_SECONDS) -> list[dict]:
    records: list[dict] = []
    for index, shot in enumerate(script.shots, start=1):
        duration = float(shot.duration)
        record = {
            "index": index,
            "shot_id": shot.id,
            "duration": round(duration, 2),
            "frame_count": _frame_count(duration, fps),
            "needs_split": duration > max_seconds,
            "aspect_ratio": script.meta.aspect_ratio,
            "resolution": RESOLUTION_MAP.get(script.meta.aspect_ratio, "1280×720"),
            "model_hint": "通义万相 · 文生视频" if index == 1 else "通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）",
            "prompt": _shot_prompt(script, shot),
            "negative_prompt": shot.negative_prompt or DEFAULT_NEGATIVE,
            "dialogue": shot.dialogue_text(),
            "subtitle": shot.subtitle,
            "camera": CAMERA_ZH.get(shot.camera, shot.camera),
        }
        records.append(record)
    return records


def to_modelscope_json(script: Script, fps: int = DEFAULT_FPS, max_seconds: float = MAX_SECONDS) -> str:
    payload = {
        "target": "modelscope-aigc-video",
        "title": script.meta.title,
        "genre": script.meta.genre,
        "style": script.meta.style,
        "aspect_ratio": script.meta.aspect_ratio,
        "fps": fps,
        "max_seconds_per_clip": max_seconds,
        "shots": modelscope_records(script, fps, max_seconds),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def to_modelscope_markdown(script: Script, fps: int = DEFAULT_FPS, max_seconds: float = MAX_SECONDS) -> str:
    records = modelscope_records(script, fps, max_seconds)
    meta = script.meta
    lines = [
        f"# 魔搭 AIGC 生成视频 · 逐镜提示词｜《{meta.title}》",
        "",
        f"- 类型 / 风格：{meta.genre} / {meta.style}",
        f"- 画幅 / 分辨率：{meta.aspect_ratio} / {RESOLUTION_MAP.get(meta.aspect_ratio, '1280×720')}",
        f"- 帧率：{fps} fps（万相按 4n+1 帧生成）",
        f"- 镜头数：{len(records)}　｜　理论总时长：{script.duration:g}s",
        "",
        "## 使用方法",
        "",
        "1. 打开魔搭社区 AIGC 专区 → 生成视频 → 选择通义万相（文生视频）模型。",
        "2. 一个镜头只用一条提示词：整段复制到提示词框即可，不要拆句。",
        f"3. 负向提示词统一填：{DEFAULT_NEGATIVE}（可选，不填也能生成）。",
        "4. 画幅、分辨率、时长按该镜「推荐参数」设置；时长超过 5s 的镜头请按提示拆分或分段生成。",
        "5. 需要人物一致时，第 2 镜起可切换到「图生视频」，以上一镜尾帧作为首帧参考。",
        "6. 台词与字幕不进入提示词（模型不生成文字），后期按「台词 / 字幕」轨单独配音与压字。",
        "",
        "## 镜头速查表",
        "",
        "| # | 镜头 | 时长 | 帧数 | 分辨率 | 需拆分 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            f"| {record['index']} | {record['shot_id']} | {record['duration']:g}s | "
            f"{record['frame_count']} | {record['resolution']} | "
            f"{'是' if record['needs_split'] else '否'} |"
        )

    lines += ["", "## 逐镜提示词", ""]
    for record in records:
        lines += [
            f"### {record['index']}. {record['shot_id']}　{record['duration']:g}s · "
            f"{record['resolution']} · {record['camera']}",
            "",
            "**提示词（复制这一整条）**",
            "",
            "```text",
            record["prompt"],
            "```",
            "",
            f"**推荐参数**：时长 {record['duration']:g}s（约 {record['frame_count']} 帧 @{fps}fps）"
            f"　｜　画幅 {record['aspect_ratio']}　｜　分辨率 {record['resolution']}"
            f"　｜　{record['model_hint']}",
        ]
        if record["needs_split"]:
            lines.append(
                f"**注意**：该镜超过 {max_seconds:g}s，建议在生成栏目内拆成两段，或在剪辑中变速。"
            )
        if record["dialogue"]:
            lines.append(f"**台词**：{record['dialogue']}")
        if record["subtitle"]:
            lines.append(f"**字幕**：{record['subtitle']}")
        lines.append("")

    lines += [
        "## 一致性参数建议",
        "",
        f"- 固定负向提示词：{DEFAULT_NEGATIVE}",
        "- 同一人物跨镜时，保持 `appearance` 描述逐字一致，或使用上一镜尾帧做图生视频。",
        "- 同一场景内镜头尽量固定 seed（若栏目提供），便于失败镜头单独重跑。",
        "",
    ]
    return "\n".join(lines)


def write_modelscope_files(script: Script, outdir, fps: int = DEFAULT_FPS) -> list:
    """写出 md + json，返回文件路径列表。"""
    from pathlib import Path

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = script.meta.title or "script"
    md_path = outdir / "modelscope_prompts.md"
    json_path = outdir / "modelscope_prompts.json"
    md_path.write_text(to_modelscope_markdown(script, fps), encoding="utf-8")
    json_path.write_text(to_modelscope_json(script, fps), encoding="utf-8")
    return [md_path, json_path]
