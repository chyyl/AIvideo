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


def _shot_prompt(script: Script, shot, negative: str) -> str:
    """魔搭视频生成页只有一个正向提示词框，因此把画面、运动与排除项合成一条。"""
    base = shot.image_prompt.zh.strip()
    if not base:
        base = f"{SHOT_SIZE_ZH.get(shot.shot_size, shot.shot_size)}，{shot.subject}，{shot.action}"
    parts = [base]
    if shot.video_prompt and shot.video_prompt not in base:
        parts.append(shot.video_prompt)
    parts.append("画面稳定，主体一致，无镜头切换")
    if negative:
        parts.append(f"避免出现：{negative}")
    return _sanitize("，".join(p.strip("，。 ") for p in parts if p.strip()))


def _frame_count(seconds: float, fps: int) -> int:
    # 万相系列按 4n+1 帧生成
    n = max(4, round(seconds * fps / 4))
    return 4 * n + 1


def modelscope_records(script: Script, fps: int = DEFAULT_FPS, max_seconds: float = MAX_SECONDS) -> list[dict]:
    records: list[dict] = []
    prev_shot = ""
    for index, shot in enumerate(script.shots, start=1):
        duration = float(shot.duration)
        negative = shot.negative_prompt or DEFAULT_NEGATIVE
        record = {
            "index": index,
            "shot_id": shot.id,
            "tab": "图生视频" if prev_shot else "文生视频",
            "duration": round(duration, 2),
            "frame_count": _frame_count(duration, fps),
            "needs_split": duration > max_seconds,
            "aspect_ratio": script.meta.aspect_ratio,
            "resolution": RESOLUTION_MAP.get(script.meta.aspect_ratio, "1280×720"),
            "model_hint": "通义万相 · 文生视频" if index == 1 else "通义万相 · 图生视频",
            "prompt": _shot_prompt(script, shot, negative),
            "negative_prompt": negative,
            "image_prompt": shot.image_prompt.zh,
            "first_frame": prev_shot,
            "prompt_enhance": False,
            "estimated_credits": 34,
            "dialogue": shot.dialogue_text(),
            "subtitle": shot.subtitle,
            "camera": CAMERA_ZH.get(shot.camera, shot.camera),
        }
        records.append(record)
        prev_shot = shot.id
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
    """只输出提示词本身：每个镜头一条完整提示词，可直接粘贴，不混入参数与台词。"""
    records = modelscope_records(script, fps, max_seconds)
    lines: list[str] = [f"# 魔搭 AIGC 生成视频 · 逐镜提示词｜《{script.meta.title}》", ""]
    for record in records:
        lines += [f"## 镜头 {record['index']}", "", record["prompt"], ""]
    return "\n".join(lines).rstrip() + "\n"


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
