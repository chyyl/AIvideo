"""脚本静态校验：结构、引用、时长与字段取值。"""
from __future__ import annotations

from dataclasses import dataclass

from .models import CAMERA_MOVES, SHOT_SIZES, TRANSITIONS, Script

ERROR = "error"
WARNING = "warning"


@dataclass
class Issue:
    level: str
    code: str
    message: str
    path: str = ""

    def __str__(self) -> str:
        prefix = "ERROR" if self.level == ERROR else "WARN"
        where = f" [{self.path}]" if self.path else ""
        return f"{prefix} {self.code}{where}: {self.message}"


def validate(script: Script) -> list[Issue]:
    issues: list[Issue] = []
    meta = script.meta

    if not meta.title.strip():
        issues.append(Issue(ERROR, "M001", "meta.title 不能为空", "meta.title"))
    if not meta.logline.strip():
        issues.append(Issue(WARNING, "M002", "缺少 logline，检索与宣发会缺少一句话卖点", "meta.logline"))
    if meta.target_duration <= 0:
        issues.append(Issue(ERROR, "M003", "meta.target_duration 必须为正整数", "meta.target_duration"))

    if not script.acts:
        issues.append(Issue(ERROR, "A001", "脚本至少需要一幕", "acts"))
    if not script.characters:
        issues.append(Issue(WARNING, "C001", "没有人物表，台词引用无法校验", "characters"))

    char_ids = [c.id for c in script.characters]
    names = {c.name for c in script.characters}
    for cid in char_ids:
        if not cid:
            issues.append(Issue(ERROR, "C002", "人物 id 不能为空", "characters"))
    for i, cid in enumerate(char_ids):
        if char_ids.count(cid) > 1:
            issues.append(Issue(ERROR, "C003", f"人物 id 重复：{cid}", "characters"))
            break

    seen_ids: set[str] = set()
    shot_ids: list[str] = []
    for act_index, act in enumerate(script.acts, start=1):
        if not act.scenes:
            issues.append(Issue(ERROR, "A002", f"第 {act_index} 幕没有场景", act.id))
        if not act.title.strip():
            issues.append(Issue(WARNING, "A003", f"第 {act_index} 幕缺标题", act.id))
        for scene in act.scenes:
            sid = scene.id or "<empty>"
            if not scene.shots:
                issues.append(Issue(WARNING, "S001", f"场景 {sid} 没有分镜", sid))
            if not scene.heading.strip():
                issues.append(Issue(WARNING, "S002", f"场景 {sid} 缺少场次标题", sid))
            for shot in scene.shots:
                shot_ids.append(shot.id)
                path = shot.id or scene.id
                if not shot.id:
                    issues.append(Issue(ERROR, "H001", f"场景 {sid} 存在空镜头 id", sid))
                if shot.id in seen_ids:
                    issues.append(Issue(ERROR, "H002", f"镜头 id 重复：{shot.id}", path))
                seen_ids.add(shot.id)
                if shot.duration <= 0:
                    issues.append(Issue(ERROR, "H003", "镜头时长必须为正数", path))
                elif shot.duration > 10:
                    issues.append(Issue(WARNING, "H004", f"镜头时长 {shot.duration}s 偏长，单镜头建议 ≤10s", path))
                if shot.shot_size not in SHOT_SIZES:
                    issues.append(Issue(WARNING, "H005", f"未知景别 {shot.shot_size}", path))
                if shot.camera not in CAMERA_MOVES:
                    issues.append(Issue(WARNING, "H006", f"未知运镜 {shot.camera}", path))
                if shot.transition_out not in TRANSITIONS:
                    issues.append(Issue(WARNING, "H007", f"未知转场 {shot.transition_out}", path))
                if not shot.subject.strip():
                    issues.append(Issue(WARNING, "H008", "缺少镜头主体", path))
                for line in shot.dialogue:
                    if line.character and names and line.character not in names:
                        issues.append(
                            Issue(WARNING, "D001", f"台词人物“{line.character}”不在人物表", path)
                        )
                    if not line.text.strip():
                        issues.append(Issue(WARNING, "D002", "存在空台词行", path))

    for scene in (s for a in script.acts for s in a.scenes):
        orders = [s.order for s in scene.shots]
        if orders != sorted(orders):
            issues.append(Issue(WARNING, "H009", f"场景 {scene.id} 镜头 order 未按升序排列", scene.id))

    total = script.duration
    if total > 0 and meta.target_duration > 0:
        delta = total - meta.target_duration
        if abs(delta) > meta.target_duration * 0.15:
            issues.append(
                Issue(
                    WARNING,
                    "T001",
                    f"成片时长 {total:g}s 与目标 {meta.target_duration}s 偏差超过 15%",
                    "meta.target_duration",
                )
            )
    if len(script.acts) > 5:
        issues.append(Issue(WARNING, "A004", "幕数超过 5，短视频节奏可能过散", "acts"))
    return issues
