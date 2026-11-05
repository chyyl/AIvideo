"""AI 视频脚本 DSL v1.0 的 Python 数据模型。

设计原则：
1. 结构化字段齐全，便于程序消费（TTS、绘图、图生视频、剪辑）。
2. 所有派生信息（时间码、总时长）在序列化时计算，不写回源数据。
3. 未知字段在反序列化时被忽略，缺失字段使用安全默认值，保证向前兼容。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

DSL_VERSION = "aivscript/1.0"

SHOT_SIZES = (
    "extreme_wide",
    "wide",
    "full",
    "medium",
    "medium_close",
    "close",
    "extreme_close",
)
SHOT_SIZE_ZH = {
    "extreme_wide": "大远景",
    "wide": "远景",
    "full": "全景",
    "medium": "中景",
    "medium_close": "中近景",
    "close": "特写",
    "extreme_close": "大特写",
}
CAMERA_MOVES = (
    "static",
    "push_in",
    "pull_out",
    "pan_left",
    "pan_right",
    "tilt_up",
    "tilt_down",
    "tracking",
    "handheld",
    "crane_up",
    "orbit",
)
CAMERA_ZH = {
    "static": "固定",
    "push_in": "缓推",
    "pull_out": "拉远",
    "pan_left": "左摇",
    "pan_right": "右摇",
    "tilt_up": "上仰",
    "tilt_down": "下俯",
    "tracking": "跟拍",
    "handheld": "手持",
    "crane_up": "升降",
    "orbit": "环绕",
}
BEAT_TYPES = ("action", "dialogue", "transition", "montage")
TRANSITIONS = ("cut", "fade_in", "fade_out", "dissolve", "wipe", "match_cut", "flash")
TIME_OF_DAY = ("dawn", "morning", "noon", "afternoon", "dusk", "night")


def _s(value: Any, default: str = "") -> str:
    return default if value is None else str(value)


def _f(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _i(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


@dataclass
class DialogueLine:
    character: str = ""
    text: str = ""
    delivery: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "DialogueLine":
        if isinstance(data, str):
            return cls(character="", text=data)
        data = _dict(data)
        return cls(
            character=_s(data.get("character")),
            text=_s(data.get("text")),
            delivery=_s(data.get("delivery")),
        )

    def to_dict(self) -> dict:
        out: dict[str, Any] = {"character": self.character, "text": self.text}
        if self.delivery:
            out["delivery"] = self.delivery
        return out


@dataclass
class ImagePrompt:
    zh: str = ""
    en: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "ImagePrompt":
        if isinstance(data, str):
            return cls(zh=data)
        data = _dict(data)
        return cls(zh=_s(data.get("zh")), en=_s(data.get("en")))

    def to_dict(self) -> dict:
        return {"zh": self.zh, "en": self.en}


@dataclass
class Shot:
    id: str = ""
    order: int = 1
    duration: float = 4.0
    shot_size: str = "medium"
    camera: str = "static"
    subject: str = ""
    action: str = ""
    dialogue: list[DialogueLine] = field(default_factory=list)
    sfx: list[str] = field(default_factory=list)
    bgm: str = ""
    subtitle: str = ""
    image_prompt: ImagePrompt = field(default_factory=ImagePrompt)
    video_prompt: str = ""
    negative_prompt: str = ""
    transition_out: str = "cut"
    notes: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "Shot":
        data = _dict(data)
        return cls(
            id=_s(data.get("id")),
            order=_i(data.get("order"), 1),
            duration=_f(data.get("duration"), 4.0),
            shot_size=_s(data.get("shot_size"), "medium"),
            camera=_s(data.get("camera"), "static"),
            subject=_s(data.get("subject")),
            action=_s(data.get("action")),
            dialogue=[DialogueLine.from_dict(x) for x in _list(data.get("dialogue"))],
            sfx=[_s(x) for x in _list(data.get("sfx")) if _s(x)],
            bgm=_s(data.get("bgm")),
            subtitle=_s(data.get("subtitle")),
            image_prompt=ImagePrompt.from_dict(data.get("image_prompt")),
            video_prompt=_s(data.get("video_prompt")),
            negative_prompt=_s(data.get("negative_prompt")),
            transition_out=_s(data.get("transition_out"), "cut"),
            notes=_s(data.get("notes")),
        )

    def to_dict(self) -> dict:
        out: dict[str, Any] = {
            "id": self.id,
            "order": self.order,
            "duration": round(self.duration, 2),
        }
        for key, value in (
            ("shot_size", self.shot_size),
            ("camera", self.camera),
            ("subject", self.subject),
            ("action", self.action),
        ):
            if value:
                out[key] = value
        if self.dialogue:
            out["dialogue"] = [d.to_dict() for d in self.dialogue]
        if self.sfx:
            out["sfx"] = list(self.sfx)
        for key, value in (
            ("bgm", self.bgm),
            ("subtitle", self.subtitle),
        ):
            if value:
                out[key] = value
        prompt = self.image_prompt.to_dict()
        if prompt["zh"] or prompt["en"]:
            out["image_prompt"] = prompt
        for key, value in (
            ("video_prompt", self.video_prompt),
            ("negative_prompt", self.negative_prompt),
            ("transition_out", self.transition_out),
            ("notes", self.notes),
        ):
            if value:
                out[key] = value
        return out

    def dialogue_text(self) -> str:
        return "；".join(
            f"{d.character}：{d.text}" if d.character else d.text for d in self.dialogue
        )


@dataclass
class Beat:
    id: str = ""
    type: str = "action"
    text: str = ""
    character: str = ""
    delivery: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "Beat":
        data = _dict(data)
        return cls(
            id=_s(data.get("id")),
            type=_s(data.get("type"), "action"),
            text=_s(data.get("text")),
            character=_s(data.get("character")),
            delivery=_s(data.get("delivery")),
        )

    def to_dict(self) -> dict:
        out: dict[str, Any] = {"id": self.id, "type": self.type, "text": self.text}
        if self.character:
            out["character"] = self.character
        if self.delivery:
            out["delivery"] = self.delivery
        return out


@dataclass
class Scene:
    id: str = ""
    heading: str = ""
    location: str = ""
    time_of_day: str = "night"
    weather: str = ""
    summary: str = ""
    beats: list[Beat] = field(default_factory=list)
    shots: list[Shot] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "Scene":
        data = _dict(data)
        return cls(
            id=_s(data.get("id")),
            heading=_s(data.get("heading")),
            location=_s(data.get("location")),
            time_of_day=_s(data.get("time_of_day"), "night"),
            weather=_s(data.get("weather")),
            summary=_s(data.get("summary")),
            beats=[Beat.from_dict(x) for x in _list(data.get("beats"))],
            shots=[Shot.from_dict(x) for x in _list(data.get("shots"))],
        )

    def to_dict(self) -> dict:
        out: dict[str, Any] = {
            "id": self.id,
            "heading": self.heading,
            "location": self.location,
            "time_of_day": self.time_of_day,
            "summary": self.summary,
            "beats": [b.to_dict() for b in self.beats],
            "shots": [s.to_dict() for s in self.shots],
        }
        if self.weather:
            out["weather"] = self.weather
        return out

    @property
    def duration(self) -> float:
        return round(sum(s.duration for s in self.shots), 2)


@dataclass
class Act:
    id: str = ""
    title: str = ""
    summary: str = ""
    scenes: list[Scene] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "Act":
        data = _dict(data)
        return cls(
            id=_s(data.get("id")),
            title=_s(data.get("title")),
            summary=_s(data.get("summary")),
            scenes=[Scene.from_dict(x) for x in _list(data.get("scenes"))],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "scenes": [s.to_dict() for s in self.scenes],
        }

    @property
    def duration(self) -> float:
        return round(sum(s.duration for s in self.scenes), 2)


@dataclass
class Character:
    id: str = ""
    name: str = ""
    role: str = ""
    age: str = ""
    appearance: str = ""
    voice: str = ""
    arc: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "Character":
        data = _dict(data)
        return cls(
            id=_s(data.get("id")),
            name=_s(data.get("name")),
            role=_s(data.get("role")),
            age=_s(data.get("age")),
            appearance=_s(data.get("appearance")),
            voice=_s(data.get("voice")),
            arc=_s(data.get("arc")),
        )

    def to_dict(self) -> dict:
        out: dict[str, Any] = {"id": self.id, "name": self.name, "role": self.role}
        for key, value in (
            ("age", self.age),
            ("appearance", self.appearance),
            ("voice", self.voice),
            ("arc", self.arc),
        ):
            if value:
                out[key] = value
        return out


@dataclass
class Meta:
    title: str = ""
    logline: str = ""
    genre: str = ""
    style: str = ""
    language: str = "zh-CN"
    aspect_ratio: str = "16:9"
    target_duration: int = 120
    audience: str = ""
    tone: str = ""

    @classmethod
    def from_dict(cls, data: Any) -> "Meta":
        data = _dict(data)
        return cls(
            title=_s(data.get("title"), "未命名"),
            logline=_s(data.get("logline")),
            genre=_s(data.get("genre")),
            style=_s(data.get("style")),
            language=_s(data.get("language"), "zh-CN"),
            aspect_ratio=_s(data.get("aspect_ratio"), "16:9"),
            target_duration=_i(data.get("target_duration"), 120),
            audience=_s(data.get("audience")),
            tone=_s(data.get("tone")),
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "logline": self.logline,
            "genre": self.genre,
            "style": self.style,
            "language": self.language,
            "aspect_ratio": self.aspect_ratio,
            "target_duration": self.target_duration,
            "audience": self.audience,
            "tone": self.tone,
        }


@dataclass
class Script:
    dsl: str = DSL_VERSION
    meta: Meta = field(default_factory=Meta)
    characters: list[Character] = field(default_factory=list)
    acts: list[Act] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "Script":
        data = _dict(data)
        return cls(
            dsl=_s(data.get("dsl"), DSL_VERSION),
            meta=Meta.from_dict(data.get("meta")),
            characters=[Character.from_dict(x) for x in _list(data.get("characters"))],
            acts=[Act.from_dict(x) for x in _list(data.get("acts"))],
        )

    def to_dict(self) -> dict:
        return {
            "dsl": self.dsl,
            "meta": self.meta.to_dict(),
            "characters": [c.to_dict() for c in self.characters],
            "acts": [a.to_dict() for a in self.acts],
        }

    @property
    def shots(self) -> Iterable[Shot]:
        for act in self.acts:
            for scene in act.scenes:
                yield from scene.shots

    @property
    def duration(self) -> float:
        return round(sum(s.duration for s in self.shots), 2)

    def get_shot(self, shot_id: str) -> Shot | None:
        return next((s for s in self.shots if s.id == shot_id), None)

    def find_scene_of_shot(self, shot_id: str) -> Scene | None:
        for act in self.acts:
            for scene in act.scenes:
                if any(s.id == shot_id for s in scene.shots):
                    return scene
        return None
