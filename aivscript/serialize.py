"""YAML / JSON / Markdown 三种序列化格式与互转。"""
from __future__ import annotations

import json
import re
from typing import Any

import yaml

from .models import (
    Act,
    Beat,
    Character,
    DSL_VERSION,
    DialogueLine,
    ImagePrompt,
    Meta,
    Scene,
    Script,
    Shot,
    CAMERA_ZH,
    SHOT_SIZE_ZH,
)

BEAT_ZH = {"action": "动作", "dialogue": "对话", "transition": "转场", "montage": "蒙太奇"}
BEAT_TYPES = {v: k for k, v in BEAT_ZH.items()}

META_LABELS = {
    "类型": "genre",
    "视觉风格": "style",
    "语言": "language",
    "画幅": "aspect_ratio",
    "受众": "audience",
    "基调": "tone",
}

CHAR_LABELS = {
    "角色": "role",
    "年龄": "age",
    "外观": "appearance",
    "声音": "voice",
    "人物弧光": "arc",
}

SHOT_DETAIL_LABELS = {
    "音效": "sfx",
    "配乐": "bgm",
    "字幕": "subtitle",
    "图像提示词（中文）": "image_zh",
    "图像提示词（英文）": "image_en",
    "视频提示词": "video_prompt",
    "负面提示词": "negative_prompt",
    "备注": "notes",
}


# ---------------------------------------------------------------- YAML / JSON


def to_dict(script: Script) -> dict:
    data = script.to_dict()
    data["dsl"] = DSL_VERSION
    return data


def to_yaml(script: Script) -> str:
    return yaml.safe_dump(
        to_dict(script),
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    )


def to_yaml_dict(script: Script) -> dict:
    return to_dict(script)


def from_yaml(text: str) -> Script:
    data = yaml.safe_load(text) or {}
    return Script.from_dict(data)


def to_json(script: Script) -> str:
    return json.dumps(to_dict(script), ensure_ascii=False, indent=2)


def from_json(text: str) -> Script:
    return Script.from_dict(json.loads(text))


# ---------------------------------------------------------------- 时间码


def shot_timecodes(script: Script) -> dict[str, tuple[float, float]]:
    """返回 {shot_id: (start, end)}，按镜头顺序累计。"""
    result: dict[str, tuple[float, float]] = {}
    cursor = 0.0
    for shot in script.shots:
        start = cursor
        cursor += shot.duration
        result[shot.id] = (round(start, 2), round(cursor, 2))
    return result


def format_tc(seconds: float) -> str:
    minutes, sec = divmod(max(seconds, 0), 60)
    return f"{int(minutes):02d}:{sec:05.2f}"


# ---------------------------------------------------------------- Markdown 导出


def _cell(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def to_markdown(script: Script) -> str:
    m = script.meta
    lines: list[str] = [f"# 《{m.title}》", ""]
    if m.logline:
        lines += [f"> 一句话故事：{m.logline}", ""]
    lines += ["## 基本信息", ""]
    for label, key in META_LABELS.items():
        value = getattr(m, key)
        if value:
            lines.append(f"- {label}：{value}")
    lines += [f"- 目标时长：{m.target_duration} 秒", ""]

    if script.characters:
        lines += ["## 人物", ""]
        for ch in script.characters:
            lines += [f"### {ch.name}", ""]
            for label, key in CHAR_LABELS.items():
                value = getattr(ch, key)
                if value:
                    lines.append(f"- {label}：{value}")
            lines.append("")

    timecodes = shot_timecodes(script)
    for act in script.acts:
        lines += [f"## {act.title or '幕'}", ""]
        if act.summary:
            lines += [f"> {act.summary}", ""]
        for scene in act.scenes:
            lines += [f"### {scene.heading or scene.id}", ""]
            if scene.location:
                lines.append(f"- 地点：{scene.location}")
            lines.append(f"- 时间：{scene.time_of_day}")
            if scene.weather:
                lines.append(f"- 天气：{scene.weather}")
            lines.append("")
            if scene.summary:
                lines += [f"> {scene.summary}", ""]
            if scene.beats:
                lines += ["#### 剧情节拍", ""]
                for beat in scene.beats:
                    label = BEAT_ZH.get(beat.type, beat.type)
                    if beat.type == "dialogue" and beat.character:
                        delivery = f"（{beat.delivery}）" if beat.delivery else ""
                        lines.append(f"- [{label}] {beat.character}{delivery}：{beat.text}")
                    else:
                        lines.append(f"- [{label}] {beat.text}")
                lines.append("")

            lines += [
                "#### 分镜",
                "",
                "| ID | # | 时长 | 景别 | 运镜 | 主体 | 动作 | 转场 |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
            for shot in scene.shots:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            _cell(shot.id),
                            str(shot.order),
                            f"{shot.duration:g}",
                            shot.shot_size,
                            shot.camera,
                            _cell(shot.subject),
                            _cell(shot.action),
                            shot.transition_out,
                        ]
                    )
                    + " |"
                )
            lines.append("")

            for shot in scene.shots:
                start, end = timecodes.get(shot.id, (0.0, 0.0))
                lines += [f"##### 镜头 {shot.id} 细节", ""]
                lines.append(f"- 时间码：{format_tc(start)} → {format_tc(end)}")
                for d in shot.dialogue:
                    delivery = f"（{d.delivery}）" if d.delivery else ""
                    who = d.character or "旁白"
                    lines.append(f"- 台词：{who}{delivery}：{d.text}")
                if shot.sfx:
                    lines.append(f"- 音效：{'；'.join(shot.sfx)}")
                for label, key in SHOT_DETAIL_LABELS.items():
                    if key == "sfx":
                        continue
                    if key == "image_zh":
                        value = shot.image_prompt.zh
                    elif key == "image_en":
                        value = shot.image_prompt.en
                    else:
                        value = getattr(shot, key)
                    if value:
                        lines.append(f"- {label}：{value}")
                lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------- Markdown 解析


def _split_bullet(line: str) -> tuple[str, str] | None:
    if not line.startswith("- "):
        return None
    body = line[2:].strip()
    for sep in ("：", ":"):
        if sep in body:
            key, value = body.split(sep, 1)
            return key.strip(), value.strip()
    return None


def _parse_dialogue(value: str) -> DialogueLine:
    match = re.match(r"^([^（(：:]+)[（(]([^）)]*)[）)]：(.*)$", value)
    if match:
        return DialogueLine(
            character=match.group(1).strip(),
            delivery=match.group(2).strip(),
            text=match.group(3).strip(),
        )
    for sep in ("：", ":"):
        if sep in value:
            who, text = value.split(sep, 1)
            if len(who) <= 12:
                return DialogueLine(character=who.strip(), text=text.strip())
    return DialogueLine(text=value.strip())


def _parse_beat(value: str) -> Beat:
    match = re.match(r"^\[(.*?)\]\s*(.*)$", value)
    if not match:
        return Beat(type="action", text=value.strip())
    label, rest = match.group(1).strip(), match.group(2).strip()
    beat_type = BEAT_TYPES.get(label, "action")
    beat = Beat(type=beat_type, text=rest)
    if beat_type == "dialogue":
        parsed = _parse_dialogue(rest)
        beat.character = parsed.character
        beat.delivery = parsed.delivery
        beat.text = parsed.text
    return beat


def _split_row(line: str) -> list[str]:
    cells = re.split(r"(?<!\\)\|", line.strip())
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return [c.strip().replace("\\|", "|") for c in cells]


def from_markdown(text: str) -> Script:
    """解析由 to_markdown 生成的字节级格式（也容忍手工小幅修改）。"""
    script = Script(dsl=DSL_VERSION)
    meta = Meta()
    chars: list[Character] = []
    acts: list[Act] = []
    act: Act | None = None
    scene: Scene | None = None
    current_shot: Shot | None = None
    section = ""
    in_table = False

    def new_shot(_scene: Scene, cells: list[str]) -> Shot:
        table = dict(zip(["id", "order", "duration", "shot_size", "camera",
                          "subject", "action", "transition_out"], cells))
        return Shot(
            id=table.get("id", ""),
            order=int(float(table.get("order") or 0)) if table.get("order") else 1,
            duration=float(table.get("duration") or 4.0),
            shot_size=table.get("shot_size") or "medium",
            camera=table.get("camera") or "static",
            subject=table.get("subject", ""),
            action=table.get("action", ""),
            transition_out=table.get("transition_out") or "cut",
        )

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("# "):
            meta.title = stripped[2:].strip().strip("《》")
            section = "title"
            continue
        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            in_table = False
            if heading == "基本信息":
                section = "meta"
                continue
            if heading == "人物":
                section = "chars"
                continue
            section = "act"
            act = Act(id=f"act-{len(acts) + 1}", title=heading)
            acts.append(act)
            scene = None
            current_shot = None
            continue
        if stripped.startswith("### "):
            heading = stripped[4:].strip()
            in_table = False
            if section == "chars":
                chars.append(Character(id=f"char-{len(chars) + 1}", name=heading))
                continue
            if act is None:
                act = Act(id="act-1", title="第一幕")
                acts.append(act)
            scene = Scene(
                id=f"scene-{len(acts)}-{len(act.scenes) + 1}",
                heading=heading,
            )
            act.scenes.append(scene)
            section = "scene"
            current_shot = None
            continue
        if stripped.startswith("##### "):
            in_table = False
            shot_id = re.sub(r"^(镜头|SHOT)\s*", "", stripped[6:].strip(), flags=re.I)
            shot_id = re.sub(r"\s*细节$", "", shot_id)
            current_shot = (
                next((s for s in scene.shots if s.id == shot_id), None) if scene else None
            )
            if current_shot is None and scene is not None:
                current_shot = Shot(id=shot_id)
                scene.shots.append(current_shot)
            continue
        if stripped.startswith("#### "):
            in_table = stripped[5:].strip() == "分镜"
            section = "shots" if in_table else "beats"
            continue

        if stripped.startswith(">"):
            note = stripped[1:].strip()
            if section == "title" or (note.startswith("一句话故事")):
                meta.logline = note.split("：", 1)[-1] if "：" in note else note
            elif act is not None and scene is None:
                act.summary = note
            elif scene is not None:
                scene.summary = note
            continue

        if in_table:
            if stripped.startswith("|") and "---" not in stripped:
                cells = _split_row(stripped)
                if cells and cells[0].lower() in ("id", "#"):
                    continue
                if scene is not None and len(cells) >= 5:
                    scene.shots.append(new_shot(scene, cells))
            continue

        if section == "beats" and scene is not None and stripped.startswith("- "):
            scene.beats.append(_parse_beat(stripped[2:].strip()))
            continue

        bullet = _split_bullet(stripped)
        if bullet:
            key, value = bullet
            if section == "meta":
                if key == "目标时长":
                    digits = re.findall(r"\d+", value)
                    meta.target_duration = int(digits[0]) if digits else 120
                elif key in META_LABELS:
                    setattr(meta, META_LABELS[key], value)
            elif section == "chars" and chars:
                if key in CHAR_LABELS:
                    setattr(chars[-1], CHAR_LABELS[key], value)
            elif section == "scene" and scene is not None:
                if key == "地点":
                    scene.location = value
                elif key == "时间":
                    scene.time_of_day = value
                elif key == "天气":
                    scene.weather = value
            elif section == "beats" and scene is not None:
                scene.beats.append(_parse_beat(value))
            elif current_shot is not None:
                if key == "时间码":
                    continue
                if key == "台词":
                    current_shot.dialogue.append(_parse_dialogue(value))
                elif key in SHOT_DETAIL_LABELS:
                    field_name = SHOT_DETAIL_LABELS[key]
                    if field_name == "image_zh":
                        current_shot.image_prompt.zh = value
                    elif field_name == "image_en":
                        current_shot.image_prompt.en = value
                    elif field_name == "sfx":
                        current_shot.sfx = [x for x in re.split(r"；|;", value) if x.strip()]
                    else:
                        setattr(current_shot, field_name, value)

    script.meta = meta
    script.characters = chars
    script.acts = acts
    for act in acts:
        for scene in act.scenes:
            for index, shot in enumerate(scene.shots, start=1):
                if not shot.id:
                    shot.id = f"shot-{act.id.split('-')[-1]}-{scene.id.split('-')[-1]}-{index}"
                shot.order = index
    return script
