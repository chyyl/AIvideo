"""三阶段生成管线：立意 → 场景 → 分镜。

后端抽象（Backend）让"在线模型"和"离线 Mock"走同一条管线，
保证离线演示产出的数据结构与真实调用完全一致。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, Protocol

from .llm import LLMClient, LLMError, extract_json
from .models import Act, Character, Meta, Scene, Script, Shot, CAMERA_ZH, SHOT_SIZE_ZH
from .prompts import (
    PREMISE_USER,
    REPAIR_USER,
    SCENES_USER,
    SHOTS_USER,
    SYSTEM_DIRECTOR,
    SYSTEM_WRITER,
)

Progress = Callable[[str, str], None]


class GenerationError(RuntimeError):
    pass


@dataclass
class GenInput:
    theme: str = "雨夜里，他等了十年的一通电话"
    genre: str = "情感"
    style: str = "胶片颗粒、低饱和、手持质感"
    tone: str = "克制、留白"
    target_duration: int = 120
    aspect_ratio: str = "16:9"
    audience: str = "25-35 岁城市观众"
    language: str = "zh-CN"

    def to_meta(self) -> dict:
        data = asdict(self)
        return {
            "title": self.theme[:12],
            "logline": "",
            "genre": self.genre,
            "style": self.style,
            "language": self.language,
            "aspect_ratio": self.aspect_ratio,
            "target_duration": self.target_duration,
            "audience": self.audience,
            "tone": self.tone,
        }


# ---------------------------------------------------------------- 后端


class Backend(Protocol):
    def premise(self, inp: GenInput) -> dict: ...

    def scenes(self, inp: GenInput, context: dict) -> dict: ...

    def shots(self, inp: GenInput, context: dict) -> dict: ...

    def regen_shot(self, inp: GenInput, shot: dict) -> dict: ...


def _first_clause(text: str, limit: int) -> str:
    text = (text or "").strip()
    for sep in ("，", "。", "；", "、", ","):
        if sep in text:
            text = text.split(sep)[0]
            break
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _characters_text(characters: list[Character]) -> str:
    return "\n".join(
        f"- {c.name}（{c.role}）：外观 {c.appearance}；声音 {c.voice}；弧光 {c.arc}"
        for c in characters
    )


class LLMBackend:
    """真实模型后端：提示词 → JSON → 数据模型。"""

    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient()

    def _ask(self, system: str, user: str) -> dict:
        try:
            raw = self.client.complete(system, user)
        except LLMError as exc:
            raise GenerationError(str(exc)) from exc
        try:
            return extract_json(raw)
        except LLMError as first:
            repair = REPAIR_USER.format(error=str(first), raw=raw[:2000])
            try:
                fixed = self.client.complete(SYSTEM_DIRECTOR, repair)
                return extract_json(fixed)
            except LLMError as second:
                raise GenerationError(f"模型输出无法解析：{first}；重试后仍失败：{second}") from second

    def premise(self, inp: GenInput) -> dict:
        user = PREMISE_USER.format(**asdict(inp))
        return self._ask(SYSTEM_WRITER, user)

    def scenes(self, inp: GenInput, context: dict) -> dict:
        user = SCENES_USER.format(**context)
        return self._ask(SYSTEM_WRITER, user)

    def shots(self, inp: GenInput, context: dict) -> dict:
        user = SHOTS_USER.format(**context)
        return self._ask(SYSTEM_DIRECTOR, user)

    def regen_shot(self, inp: GenInput, shot: dict) -> dict:
        import json

        user = REGEN_SHOT_USER.format(shot_json=json.dumps(shot, ensure_ascii=False, indent=2))
        return self._ask(SYSTEM_DIRECTOR, user)


# ---------------------------------------------------------------- 离线 Mock

GENRE_PALETTE = {
    "科幻": {
        "en": "science fiction",
        "locations": ["星港候机厅", "废弃观测站", "雨夜天台"],
        "weather": ["细雨", "浓雾", "无风"],
        "light": "冷蓝霓虹与屏幕反光",
        "detail": "全息屏上跳出一行错误代码",
    },
    "悬疑": {
        "en": "mystery thriller",
        "locations": ["老公寓楼道", "深夜便利店", "地下停车场"],
        "weather": ["阴天", "小雨", "闷热"],
        "light": "单一顶光与长阴影",
        "detail": "门缝下塞进一张没有署名的照片",
    },
    "情感": {
        "en": "intimate drama",
        "locations": ["出租屋", "医院走廊", "清晨的公交站"],
        "weather": ["小雨", "晴转阴", "微凉"],
        "light": "窗边自然光与暖色台灯",
        "detail": "手机屏幕亮起又熄灭",
    },
    "喜剧": {
        "en": "deadpan comedy",
        "locations": ["共享办公室", "24 小时便利店", "末班地铁"],
        "weather": ["晴", "闷热", "小雨"],
        "light": "高亮荧光灯与冷白反光",
        "detail": "打印机吐出一张完全空白的纸",
    },
    "恐怖": {
        "en": "slow-burn horror",
        "locations": ["老宅客厅", "长走廊", "地下室"],
        "weather": ["雷雨", "阴雾", "无风"],
        "light": "手电筒光斑与月光",
        "detail": "墙里传来三下敲击声",
    },
    "纪实": {
        "en": "documentary",
        "locations": ["清晨街道", "在建工地", "普通人家客厅"],
        "weather": ["晴", "阴", "小雨"],
        "light": "自然光、现场实光",
        "detail": "账本上有一页被反复折过",
    },
}

SIZE_EN = {
    "extreme_wide": "extreme wide",
    "wide": "wide",
    "full": "full",
    "medium": "medium",
    "medium_close": "medium close-up",
    "close": "close-up",
    "extreme_close": "extreme close-up",
}


class MockBackend:
    """离线后端：不调用模型，用结构模板产出可演示的完整脚本。"""

    protagonist = "主角"

    def premise(self, inp: GenInput) -> dict:
        palette = GENRE_PALETTE.get(inp.genre, GENRE_PALETTE["情感"])
        protagonist = "阿岚"
        self.protagonist = protagonist
        title = inp.theme.strip().strip("《》")
        if len(title) > 14:
            clause = title.split("，")[0].strip()
            title = clause if len(clause) <= 14 else clause[:13] + "…"
        acts = [
            {
                "id": "act-1",
                "title": "第一幕 · 日常的裂缝",
                "summary": "建置：主角的日常被一个细节打破，观众获得追问的理由。",
                "scenes": [
                    {
                        "id": "scene-1-1",
                        "heading": f"INT. {palette['locations'][0]} - 夜",
                        "location": palette["locations"][0],
                        "time_of_day": "night",
                        "weather": palette["weather"][0],
                        "summary": f"{protagonist}在{inp.theme[:16]}的余波里回到熟悉的空间。",
                    },
                    {
                        "id": "scene-1-2",
                        "heading": f"EXT. {palette['locations'][1]} - 夜",
                        "location": palette["locations"][1],
                        "time_of_day": "night",
                        "weather": palette["weather"][1],
                        "summary": f"{palette['detail']}，他决定不声张。",
                    },
                ],
            },
            {
                "id": "act-2",
                "title": "第二幕 · 追逐与代价",
                "summary": "对抗：主动接近真相，每一次接近都付出一点代价。",
                "scenes": [
                    {
                        "id": "scene-2-1",
                        "heading": f"INT. {palette['locations'][2]} - 凌晨",
                        "location": palette["locations"][2],
                        "time_of_day": "dawn",
                        "weather": palette["weather"][2],
                        "summary": "他找到一个不该存在的记录，并第一次说谎。",
                    },
                    {
                        "id": "scene-2-2",
                        "heading": f"EXT. {palette['locations'][0]} - 黎明",
                        "location": palette["locations"][0],
                        "time_of_day": "dawn",
                        "weather": palette["weather"][0],
                        "summary": "代价显现：他必须在两件重要的事之间选一件。",
                    },
                ],
            },
            {
                "id": "act-3",
                "title": "第三幕 · 留白",
                "summary": "转折：答案给出一半，情绪落在未说出口的那句话上。",
                "scenes": [
                    {
                        "id": "scene-3-1",
                        "heading": f"INT. {palette['locations'][1]} - 清晨",
                        "location": palette["locations"][1],
                        "time_of_day": "morning",
                        "weather": palette["weather"][1],
                        "summary": "他做出了选择，镜头停在空着的座位上。",
                    },
                ],
            },
        ]
        return {
            "meta": {
                "title": title or "未命名",
                "logline": (
                    f"{inp.genre}短片：{inp.theme}。{protagonist}为了一个说不清的答案，"
                    f"必须在黎明前放弃他唯一确定的东西。"
                ),
            },
            "characters": [
                {
                    "id": "char-1",
                    "name": protagonist,
                    "role": "主角",
                    "age": "30 岁上下",
                    "appearance": "短发，深灰风衣，右手腕有一道旧疤",
                    "voice": "几乎不用感叹句，语速慢，停顿多",
                    "arc": "从回避到承认：他最终选择了说真话，但已经太晚",
                },
                {
                    "id": "char-2",
                    "name": "老周",
                    "role": "同伴 / 阻碍",
                    "age": "45 岁",
                    "appearance": "微胖，旧夹克，总是拎着一个磨破的公文包",
                    "voice": "热络、爱讲道理、句子长",
                    "arc": "他一直在替主角维持体面，最后先离开",
                },
            ],
            "acts": acts,
        }

    def scenes(self, inp: GenInput, context: dict) -> dict:
        # 场景数据已由 premise 阶段给出，这里补充节拍。
        palette = GENRE_PALETTE.get(inp.genre, GENRE_PALETTE["情感"])
        scenes = []
        for scene in context["scenes"]:
            location = scene.get("location", "房间")
            scenes.append(
                {
                    **scene,
                    "beats": [
                        {
                            "type": "action",
                            "text": f"{scene.get('location', '')}里只剩一盏灯，{palette['detail']}。",
                        },
                        {
                            "type": "dialogue",
                            "text": "你早就知道，只是不想承认。",
                            "character": "老周",
                            "delivery": "压低声",
                        },
                        {
                            "type": "action",
                            "text": "他伸手去关灯，手停在半空，又收了回来。",
                        },
                    ],
                }
            )
        return {"scenes": scenes}

    def shots(self, inp: GenInput, context: dict) -> dict:
        palette = GENRE_PALETTE.get(inp.genre, GENRE_PALETTE["情感"])
        budget = float(context["scene_budget"])
        count = max(2, min(5, round(budget / 4)))
        duration = round(budget / count, 1)
        beats = context.get("beats_data") or [{"type": "action", "text": "沉默的停顿"}]
        sizes = ["wide", "medium", "medium_close", "close", "wide"]
        cameras = ["push_in", "static", "tracking", "pull_out", "handheld"]
        dialogue_beat = next((b for b in beats if b.get("type") == "dialogue"), None)
        shots = []
        for index in range(count):
            beat = beats[index % len(beats)]
            size = sizes[index % len(sizes)]
            camera = cameras[index % len(cameras)]
            camera_zh = CAMERA_ZH.get(camera, camera)
            if beat.get("type") == "dialogue":
                who = beat.get("character") or "人物"
                subject = who
                action_text = f"{who}开口说话，表情克制"
            else:
                subject = getattr(self, "protagonist", "主角")
                action_text = _first_clause(beat.get("text", ""), 32) or "画面静止，只有光线变化"
            dialogue = []
            if index == 0 and dialogue_beat:
                dialogue = [
                    {
                        "character": dialogue_beat.get("character", "老周"),
                        "text": dialogue_beat.get("text", ""),
                        "delivery": dialogue_beat.get("delivery", "低声"),
                    }
                ]
            shots.append(
                {
                    "id": f"shot-{context['act_index']}-{context['scene_index']}-{index + 1}",
                    "order": index + 1,
                    "duration": duration,
                    "shot_size": size,
                    "camera": camera,
                    "subject": subject,
                    "action": action_text,
                    "dialogue": dialogue,
                    "sfx": ["雨声" if "雨" in inp.style or index == 0 else "环境底噪"],
                    "bgm": "低频弦乐，音量渐弱" if index == 0 else "静音，只留呼吸声",
                    "subtitle": dialogue[0]["text"] if dialogue else "",
                    "image_prompt": {
                        "zh": (
                            f"{SHOT_SIZE_ZH.get(size, size)}，{subject}，"
                            f"位于{context['location']}，{palette['light']}，"
                            f"{inp.style}，电影感构图，{inp.aspect_ratio}"
                        ),
                        "en": (
                            f"{SIZE_EN.get(size, size)} shot, a single subject in a dim interior, "
                            f"{palette['en']} style, moody lighting, muted palette, "
                            f"film grain, {inp.aspect_ratio} aspect ratio, highly detailed"
                        ),
                    },
                    "video_prompt": (
                        f"固定机位，{action_text[:30]}"
                        if camera == "static"
                        else f"缓慢运镜（{camera_zh}），{action_text[:30]}"
                    ),
                    "negative_prompt": "畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感",
                    "transition_out": "cut" if index < count - 1 else "fade_out",
                    "notes": f"第 {index + 1} 镜，控制在 {duration}s 内",
                }
            )
        return {"shots": shots}

    def regen_shot(self, inp: GenInput, shot: dict) -> dict:
        sizes = ["wide", "medium", "medium_close", "close"]
        cameras = ["push_in", "pull_out", "tracking", "handheld"]
        new_size = sizes[(sizes.index(shot.get("shot_size", "medium")) + 1) % len(sizes)] \
            if shot.get("shot_size") in sizes else sizes[1]
        new_camera = cameras[(cameras.index(shot.get("camera", "static")) + 1) % len(cameras)] \
            if shot.get("camera") in cameras else cameras[0]
        subtitle = shot.get("subtitle", "") or shot.get("subject", "")
        return {
            **shot,
            "shot_size": new_size,
            "camera": new_camera,
            "image_prompt": {
                "zh": (
                    f"{SHOT_SIZE_ZH.get(new_size, new_size)}，{subtitle}，"
                    f"位于原场景，冷调环境光，{inp.style}，电影感构图，{inp.aspect_ratio}"
                ),
                "en": (
                    f"{SIZE_EN.get(new_size, new_size)} shot, {subtitle}, "
                    f"cold ambient light, {inp.style}, cinematic, film grain, "
                    f"{inp.aspect_ratio} aspect ratio"
                ),
            },
            "video_prompt": f"换机位：{new_camera}，动作不变，节奏略放慢",
            "notes": "离线 Mock 重写：仅调整机位与景别，用于验证流程",
        }


# ---------------------------------------------------------------- 管线


def _normalize(script: Script) -> Script:
    for act_index, act in enumerate(script.acts, start=1):
        if not act.id:
            act.id = f"act-{act_index}"
        for scene_index, scene in enumerate(act.scenes, start=1):
            if not scene.id:
                scene.id = f"scene-{act_index}-{scene_index}"
            for shot_index, shot in enumerate(scene.shots, start=1):
                shot.order = shot_index
                if not shot.id:
                    shot.id = f"shot-{act_index}-{scene_index}-{shot_index}"
    return script


class Generator:
    def __init__(self, backend: Backend, progress: Progress | None = None) -> None:
        self.backend = backend
        self.progress = progress or (lambda stage, msg: None)

    def generate(self, inp: GenInput) -> Script:
        self.progress("premise", "阶段 1/3 · 扩展立意、人物与三幕结构")
        try:
            premise = self.backend.premise(inp)
        except GenerationError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise GenerationError(f"立意阶段失败：{exc}") from exc

        meta_data = {**inp.to_meta(), **{k: v for k, v in (premise.get("meta") or {}).items() if v}}
        characters = [Character.from_dict(x) for x in premise.get("characters") or []]
        acts = [Act.from_dict(x) for x in premise.get("acts") or []]
        if not acts:
            raise GenerationError("模型没有返回任何幕结构")
        for index, character in enumerate(characters, start=1):
            if not character.id:
                character.id = f"char-{index}"

        script = _normalize(Script(meta=Meta.from_dict(meta_data), characters=characters, acts=acts))
        total_scenes = sum(len(a.scenes) for a in script.acts) or len(script.acts)
        scene_budget = max(inp.target_duration / total_scenes, 6.0)

        for act_index, act in enumerate(script.acts, start=1):
            self.progress(
                "scenes",
                f"阶段 2/3 · 细化第 {act_index}/{len(script.acts)} 幕的场景与节拍",
            )
            existing = [
                {"id": s.id, "heading": s.heading, "summary": s.summary} for s in act.scenes
            ]
            context = {
                "act_index": act_index,
                "title": script.meta.title,
                "logline": script.meta.logline,
                "genre": script.meta.genre,
                "style": script.meta.style,
                "tone": script.meta.tone,
                "target_duration": script.meta.target_duration,
                "act_title": act.title,
                "act_summary": act.summary,
                "characters": _characters_text(script.characters),
                "existing_scenes": "\n".join(f"- {s}" for s in existing) or "（无）",
                "scenes": [s.to_dict() for s in act.scenes],
                "act_budget": round(script.meta.target_duration / len(script.acts), 1),
            }
            try:
                data = self.backend.scenes(inp, context)
            except GenerationError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise GenerationError(f"第 {act_index} 幕场景阶段失败：{exc}") from exc
            scenes = [Scene.from_dict(x) for x in data.get("scenes") or []]
            if scenes:
                # 用新场景（含 beat），但场次标题/地点/摘要缺失时回退到上一版
                merged: list[Scene] = []
                for index, scene in enumerate(scenes):
                    if index < len(act.scenes):
                        old = act.scenes[index]
                        scene.heading = scene.heading or old.heading
                        scene.location = scene.location or old.location
                        scene.summary = scene.summary or old.summary
                    merged.append(scene)
                act.scenes = merged
            for index, scene in enumerate(act.scenes, start=1):
                scene.id = scene.id or f"scene-{act_index}-{index}"

        for act_index, act in enumerate(script.acts, start=1):
            for scene_index, scene in enumerate(act.scenes, start=1):
                self.progress(
                    "shots",
                    f"阶段 3/3 · 拆分镜头 {scene_index}/{len(act.scenes)}（第 {act_index} 幕）",
                )
                palette = GENRE_PALETTE.get(inp.genre, GENRE_PALETTE["情感"])
                context = {
                    "act_index": act_index,
                    "scene_index": scene_index,
                    "heading": scene.heading,
                    "location": scene.location or scene.heading,
                    "location_en": scene.location or scene.heading,
                    "time_of_day": scene.time_of_day,
                    "weather": scene.weather,
                    "summary": scene.summary,
                    "beats": "\n".join(
                        f"- [{b.type}] "
                        + (f"{b.character}（{b.delivery}）：{b.text}" if b.type == "dialogue" else b.text)
                        for b in scene.beats
                    )
                    or "- [action] 无",
                    "beats_data": [b.to_dict() for b in scene.beats],
                    "characters": _characters_text(script.characters),
                    "style": script.meta.style or inp.style,
                    "style_en": inp.style,
                    "genre": inp.genre,
                    "aspect_ratio": script.meta.aspect_ratio,
                    "language": script.meta.language,
                    "scene_budget": round(scene_budget, 1),
                    "light": palette["light"],
                }
                try:
                    data = self.backend.shots(inp, context)
                except GenerationError:
                    raise
                except Exception as exc:  # noqa: BLE001
                    raise GenerationError(f"{scene.id} 分镜阶段失败：{exc}") from exc
                scene.shots = [
                    Shot.from_dict({**x, "order": i + 1})
                    for i, x in enumerate(data.get("shots") or [])
                ]
                if not scene.shots:
                    raise GenerationError(f"{scene.id} 没有生成任何镜头")

        _normalize(script)
        self.progress("done", f"完成：{len(script.acts)} 幕 / {len(list(script.shots))} 个镜头 / {script.duration:g}s")
        return script

    def regenerate_shot(self, inp: GenInput, shot: Shot) -> Shot:
        data = self.backend.regen_shot(inp, shot.to_dict())
        return Shot.from_dict({**shot.to_dict(), **data})


def build_backend(offline: bool = False) -> Backend:
    client = LLMClient()
    if offline or client.config.offline:
        return MockBackend()
    return LLMBackend(client)
