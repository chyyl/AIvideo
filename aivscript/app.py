"""Textual TUI：AI 视频脚本自动生成器。"""
from __future__ import annotations

from pathlib import Path
from time import strftime

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Markdown,
    RichLog,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

from .generator import GenInput, Generator, MockBackend, build_backend
from .llm import LLMClient
from .models import CAMERA_MOVES, CAMERA_ZH, SHOT_SIZES, SHOT_SIZE_ZH, Script, Shot
from .prompts import PROMPT_LIBRARY, question_chain_text
from .serialize import to_json, to_markdown, to_yaml
from .validate import validate

GENRES = ["科幻", "悬疑", "情感", "喜剧", "恐怖", "纪实"]
DURATIONS = [30, 60, 90, 120, 180, 240]
RATIOS = ["16:9", "9:16", "4:3", "2.35:1"]


def _log_line(log: RichLog, message: str) -> None:
    log.write(Text(f"[{strftime('%H:%M:%S')}] {message}", style="grey70"))


class ShotEditorScreen(Screen[dict | None]):
    """单镜头编辑弹窗。"""

    BINDINGS = [("escape", "cancel", "取消")]

    CSS = """
    ShotEditorScreen { align: center middle; }
    #editor { width: 80; height: 90%; border: thick #4ea1d3; background: #14171c; padding: 1 2; }
    #editor .field { color: #7fd1ff; height: 1; margin-top: 1; }
    #editor Input, #editor Select { margin-bottom: 1; }
    #editor-buttons { height: auto; margin-top: 1; }
    """

    def __init__(self, shot: Shot) -> None:
        super().__init__()
        self.shot = shot

    def compose(self) -> ComposeResult:
        shot = self.shot
        with VerticalScroll(id="editor"):
            yield Label(f"编辑镜头 · {shot.id}")
            yield Label("时长（秒）", classes="field")
            yield Input(str(shot.duration), id="f-duration")
            yield Label("景别", classes="field")
            yield Select(
                [(SHOT_SIZE_ZH.get(s, s), s) for s in SHOT_SIZES],
                value=shot.shot_size if shot.shot_size in SHOT_SIZES else "medium",
                id="f-size",
                allow_blank=False,
            )
            yield Label("运镜", classes="field")
            yield Select(
                [(CAMERA_ZH.get(c, c), c) for c in CAMERA_MOVES],
                value=shot.camera if shot.camera in CAMERA_MOVES else "static",
                id="f-camera",
                allow_blank=False,
            )
            yield Label("主体", classes="field")
            yield Input(shot.subject, id="f-subject")
            yield Label("动作 / 画面", classes="field")
            yield Input(shot.action, id="f-action")
            yield Label("字幕 / 台词", classes="field")
            yield Input(shot.subtitle or shot.dialogue_text(), id="f-subtitle")
            yield Label("图像提示词（中文）", classes="field")
            yield Input(shot.image_prompt.zh, id="f-zh")
            yield Label("图像提示词（英文）", classes="field")
            yield Input(shot.image_prompt.en, id="f-en")
            yield Label("视频提示词", classes="field")
            yield Input(shot.video_prompt, id="f-video")
            yield Label("备注", classes="field")
            yield Input(shot.notes, id="f-notes")
            with Horizontal(id="editor-buttons"):
                yield Button("保存", id="save", variant="primary")
                yield Button("取消", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        if event.button.id != "save":
            return
        try:
            duration = float(self.query_one("#f-duration", Input).value or 4)
        except ValueError:
            duration = self.shot.duration
        self.dismiss(
            {
                "duration": duration,
                "shot_size": self.query_one("#f-size", Select).value,
                "camera": self.query_one("#f-camera", Select).value,
                "subject": self.query_one("#f-subject", Input).value,
                "action": self.query_one("#f-action", Input).value,
                "subtitle": self.query_one("#f-subtitle", Input).value,
                "image_prompt": {
                    "zh": self.query_one("#f-zh", Input).value,
                    "en": self.query_one("#f-en", Input).value,
                },
                "video_prompt": self.query_one("#f-video", Input).value,
                "notes": self.query_one("#f-notes", Input).value,
            }
        )

    def action_cancel(self) -> None:
        self.dismiss(None)


class AdvancedScreen(Screen[dict | None]):
    """高级设定弹窗：风格 / 基调 / 受众 / 语言。"""

    BINDINGS = [("escape", "cancel", "取消")]

    CSS = """
    AdvancedScreen { align: center middle; }
    #advanced { width: 70; height: auto; border: thick #4ea1d3; background: #14171c; padding: 1 2; }
    #advanced .field { color: #7fd1ff; height: 1; margin-top: 1; }
    """

    def __init__(self, values: dict) -> None:
        super().__init__()
        self.values = values

    def compose(self) -> ComposeResult:
        with Vertical(id="advanced"):
            yield Label("高级设定（影响全片视听与提示词）")
            yield Label("视觉风格", classes="field")
            yield Input(self.values.get("style", ""), id="a-style")
            yield Label("基调", classes="field")
            yield Input(self.values.get("tone", ""), id="a-tone")
            yield Label("受众", classes="field")
            yield Input(self.values.get("audience", ""), id="a-audience")
            yield Label("字幕语言", classes="field")
            yield Select(
                [("中文", "zh-CN"), ("English", "en-US")],
                value=self.values.get("language", "zh-CN"),
                id="a-language",
                allow_blank=False,
            )
            with Horizontal(id="advanced-buttons"):
                yield Button("保存", id="save", variant="primary")
                yield Button("取消", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        if event.button.id != "save":
            return
        self.dismiss(
            {
                "style": self.query_one("#a-style", Input).value,
                "tone": self.query_one("#a-tone", Input).value,
                "audience": self.query_one("#a-audience", Input).value,
                "language": self.query_one("#a-language", Select).value,
            }
        )

    def action_cancel(self) -> None:
        self.dismiss(None)


class AIVScriptApp(App[None]):
    TITLE = "AIVScript · AI 视频脚本生成器"
    SUB_TITLE = "YAML 分镜 DSL ↔ Markdown 剧本"
    BINDINGS = [
        ("ctrl+g", "generate", "生成"),
        ("ctrl+e", "edit_shot", "编辑"),
        ("ctrl+r", "regen_shot", "重写"),
        ("ctrl+l", "validate_script", "校验"),
        ("ctrl+s", "export_all", "导出"),
        ("ctrl+a", "advanced", "高级"),
        ("ctrl+q", "quit", "退出"),
    ]

    CSS = """
    Screen { background: #0e1116; color: #e6e8ec; }
    #body { layout: horizontal; height: 1fr; }
    #sidebar { width: 36; border: round #2b3240; padding: 1; }
    #main { width: 1fr; padding: 0 1; }
    .section-title { color: #7fd1ff; text-style: bold; margin-bottom: 1; }
    .field { color: #8a97a8; height: 1; margin-top: 1; }
    #status { height: 2; content-align: left middle; color: #9aa7b8; }
    #shots { height: 1fr; }
    #shot-detail { height: 1fr; padding: 1; }
    #log { height: 6; border: round #2b3240; }
    #toolbar { height: 3; margin-top: 1; }
    #toolbar Button { margin-right: 1; min-width: 8; }
    TabbedContent { height: 1fr; }
    TabPane { height: 1fr; }
    #preview, #prompts { height: 1fr; }
    """

    def __init__(self, offline: bool = False) -> None:
        super().__init__()
        self.force_offline = offline
        self.script: Script | None = None
        self.current_shot_id: str | None = None
        self.style = "自然光、低饱和、胶片颗粒"
        self.tone = "克制、留白"
        self.audience = "25-35 岁城市观众"
        self.language = "zh-CN"

    # ------------------------------------------------------------ 布局

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="body"):
            with Vertical(id="sidebar"):
                yield Static("① 创作设定", classes="section-title")
                yield Button("高级设定 Ctrl+A", id="advanced")
                yield Static("主题 / 题目", classes="field")
                yield Input("雨夜里，他等了十年的一通电话", id="theme")
                yield Static("类型", classes="field")
                yield Select([(g, g) for g in GENRES], value="情感", id="genre", allow_blank=False)
                yield Static("目标时长（秒）", classes="field")
                yield Select(
                    [(f"{d} 秒", d) for d in DURATIONS], value=120, id="duration", allow_blank=False
                )
                yield Static("画幅", classes="field")
                yield Select([(r, r) for r in RATIOS], value="16:9", id="ratio", allow_blank=False)

            with Vertical(id="main"):
                yield Static("就绪", id="status")
                with TabbedContent(initial="tab-shots"):
                    with TabPane("分镜表", id="tab-shots"):
                        yield DataTable(id="shots", cursor_type="row")
                    with TabPane("剧本预览", id="tab-preview"):
                        yield Markdown("", id="preview")
                    with TabPane("镜头详情", id="tab-detail"):
                        yield Static("选中一行分镜查看完整镜头信息", id="shot-detail")
                    with TabPane("提示词库", id="tab-prompts"):
                        yield Markdown(self._prompt_text(), id="prompts")
                        yield Button("查看 42 问提问链", id="show-questions")
                yield RichLog(id="log", wrap=True, markup=True)
                with Horizontal(id="toolbar"):
                    yield Button("生成", id="generate", variant="primary")
                    yield Button("示例", id="demo")
                    yield Button("校验", id="validate")
                    yield Button("编辑", id="edit")
                    yield Button("重写", id="regen")
                    yield Button("导出", id="export")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#shots", DataTable).add_columns(
            "镜号", "时长", "景别", "运镜", "主体", "台词", "转场"
        )
        client = LLMClient()
        if self.force_offline or client.config.offline:
            self.query_one("#status", Static).update(
                "模式：离线 Mock（未设置 AIVSCRIPT_API_KEY）  ｜  Ctrl+G 生成 / Ctrl+A 高级设定"
            )
            _log_line(self.query_one("#log", RichLog), "未检测到 API Key，已启用离线 Mock 后端")
        else:
            self.query_one("#status", Static).update(
                f"模式：在线模型 {client.config.model}  @ {client.config.base_url}"
            )
        self.query_one("#generate", Button).focus()

    # ------------------------------------------------------------ 输入与生成

    def _input(self) -> GenInput:
        return GenInput(
            theme=self.query_one("#theme", Input).value.strip() or "一个没有说出口的告别",
            genre=self.query_one("#genre", Select).value or "情感",
            style=self.style,
            tone=self.tone,
            target_duration=int(self.query_one("#duration", Select).value or 120),
            aspect_ratio=self.query_one("#ratio", Select).value or "16:9",
            audience=self.audience,
            language=self.language,
        )

    def _set_busy(self, busy: bool, message: str = "") -> None:
        for button in self.query("#generate, #demo, #advanced, #validate, #edit, #regen, #export"):
            button.disabled = busy
        if message:
            self.query_one("#status", Static).update(message)

    def _start_generate(self, backend=None) -> None:
        self.last_input = self._input()
        self._run_generation(backend or build_backend(offline=self.force_offline), self.last_input)

    @work(thread=True, exclusive=True, group="generate")
    def _run_generation(self, backend, inp: GenInput) -> None:
        self.call_from_thread(self._set_busy, True, "生成中…")
        log = self.query_one("#log", RichLog)

        def progress(stage: str, message: str) -> None:
            self.call_from_thread(_log_line, log, message)

        try:
            script = Generator(backend, progress).generate(inp)
        except Exception as exc:  # noqa: BLE001
            self.call_from_thread(_log_line, log, f"失败：{exc}")
            self.call_from_thread(self._set_busy, False, "生成失败，详情见日志")
            self.call_from_thread(self.notify, str(exc), severity="error", timeout=8)
            return
        self.call_from_thread(self._apply_script, script)

    def _apply_script(self, script: Script) -> None:
        self.script = script
        first = next(iter(script.shots), None)
        self.current_shot_id = first.id if first else None
        self._refresh_views()
        self._set_busy(False)
        self.notify("脚本生成完成", severity="information")
        self.query_one("#shots", DataTable).focus()

    # ------------------------------------------------------------ 视图刷新

    def _refresh_views(self) -> None:
        if not self.script:
            return
        table = self.query_one("#shots", DataTable)
        table.clear()
        for shot in self.script.shots:
            table.add_row(
                shot.id,
                f"{shot.duration:g}s",
                SHOT_SIZE_ZH.get(shot.shot_size, shot.shot_size),
                CAMERA_ZH.get(shot.camera, shot.camera),
                shot.subject[:24],
                shot.dialogue_text()[:26],
                shot.transition_out,
                key=shot.id,
            )
        self.query_one("#preview", Markdown).update(to_markdown(self.script))
        self.query_one("#prompts", Markdown).update(self._prompt_text())
        if self.current_shot_id:
            self._show_shot(self.current_shot_id)
        self.query_one("#status", Static).update(
            f"《{self.script.meta.title}》 · {len(self.script.acts)} 幕 · "
            f"{len(list(self.script.shots))} 镜 · 成片 {self.script.duration:g}s / "
            f"目标 {self.script.meta.target_duration}s"
        )

    def _prompt_text(self) -> str:
        lines = ["# 提示词库", "", "三个阶段串行调用，每一步都要求严格 JSON。", ""]
        for item in PROMPT_LIBRARY:
            lines += [f"## {item.stage}", "", "**System**", "", "```text", item.system, "```", ""]
            lines += ["**User 模板**", "", "```text", item.user_template, "```", ""]
        return "\n".join(lines)

    # ------------------------------------------------------------ 表格与详情

    @on(DataTable.RowSelected, "#shots")
    def _row_selected(self, event: DataTable.RowSelected) -> None:
        self._select_row(event.row_key.value)

    @on(DataTable.RowHighlighted, "#shots")
    def _row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._select_row(event.row_key.value)

    def _select_row(self, key) -> None:
        shot_id = str(key) if key else None
        if shot_id:
            self.current_shot_id = shot_id
            self._show_shot(shot_id)

    def _show_shot(self, shot_id: str) -> None:
        if not self.script:
            return
        shot = self.script.get_shot(shot_id)
        if not shot:
            return
        scene = self.script.find_scene_of_shot(shot_id)
        lines = [
            f"镜头 {shot.id}   |   {shot.duration:g}s   |   "
            f"{SHOT_SIZE_ZH.get(shot.shot_size, shot.shot_size)}   |   "
            f"{CAMERA_ZH.get(shot.camera, shot.camera)}",
            f"场景：{scene.heading if scene else '-'}",
            "",
            f"主体：{shot.subject}",
            f"动作：{shot.action}",
        ]
        for line in shot.dialogue:
            delivery = f"（{line.delivery}）" if line.delivery else ""
            lines.append(f"台词：{line.character}{delivery}：{line.text}")
        if shot.subtitle:
            lines.append(f"字幕：{shot.subtitle}")
        if shot.sfx:
            lines.append(f"音效：{'；'.join(shot.sfx)}")
        if shot.bgm:
            lines.append(f"配乐：{shot.bgm}")
        lines += [
            "",
            f"图像提示词（中）：{shot.image_prompt.zh}",
            f"图像提示词（EN）：{shot.image_prompt.en}",
            f"视频提示词：{shot.video_prompt}",
            f"负面提示词：{shot.negative_prompt}",
            f"转场：{shot.transition_out}    备注：{shot.notes}",
        ]
        self.query_one("#shot-detail", Static).update("\n".join(lines))

    # ------------------------------------------------------------ 编辑 / 重写

    def _open_editor(self) -> None:
        if not self._require_shot():
            return
        self.push_screen(ShotEditorScreen(self.script.get_shot(self.current_shot_id)), self._after_edit)

    def _after_edit(self, result: dict | None) -> None:
        if not result or not self.script or not self.current_shot_id:
            return
        shot = self.script.get_shot(self.current_shot_id)
        if not shot:
            return
        shot.duration = max(float(result.get("duration") or shot.duration), 0.5)
        for key in ("shot_size", "camera", "subject", "action", "video_prompt", "notes"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                setattr(shot, key, value.strip())
        prompt = result.get("image_prompt") or {}
        shot.image_prompt.zh = prompt.get("zh") or shot.image_prompt.zh
        shot.image_prompt.en = prompt.get("en") or shot.image_prompt.en
        subtitle = (result.get("subtitle") or "").strip()
        if subtitle:
            if shot.dialogue:
                shot.dialogue[0].text = subtitle
            else:
                shot.subtitle = subtitle
        self._refresh_views()
        self.notify(f"已更新 {shot.id}", severity="information")

    def _start_regen(self) -> None:
        if not self._require_shot():
            return
        self._regen_worker(self.current_shot_id)

    @work(thread=True, exclusive=True, group="regen")
    def _regen_worker(self, shot_id: str) -> None:
        shot = self.script.get_shot(shot_id) if self.script else None
        if not shot:
            return
        self.call_from_thread(self._set_busy, True, f"重写 {shot_id} …")
        log = self.query_one("#log", RichLog)
        try:
            new_shot = Generator(build_backend(offline=self.force_offline)).regenerate_shot(
                self.last_input, shot
            )
        except Exception as exc:  # noqa: BLE001
            self.call_from_thread(_log_line, log, f"重写失败：{exc}")
            self.call_from_thread(self._set_busy, False, "重写失败，详情见日志")
            self.call_from_thread(self.notify, str(exc), severity="error")
            return
        new_shot.id = shot.id
        self.call_from_thread(self._replace_shot, shot_id, new_shot)
        self.call_from_thread(_log_line, log, f"已重写 {shot_id}")

    def _replace_shot(self, shot_id: str, new_shot: Shot) -> None:
        if not self.script:
            return
        for scene in (s for a in self.script.acts for s in a.scenes):
            for index, shot in enumerate(scene.shots):
                if shot.id == shot_id:
                    scene.shots[index] = new_shot
                    break
        self._refresh_views()
        self._set_busy(False)

    # ------------------------------------------------------------ 校验 / 导出

    def _validate(self) -> None:
        if not self.script:
            self.notify("请先生成脚本", severity="warning")
            return
        issues = validate(self.script)
        log = self.query_one("#log", RichLog)
        if not issues:
            _log_line(log, "校验通过：没有发现问题")
            self.notify("校验通过", severity="information")
            return
        for issue in issues:
            _log_line(log, str(issue))
        errors = sum(1 for i in issues if i.level == "error")
        self.notify(f"发现 {errors} 个错误 / {len(issues) - errors} 个警告", severity="warning")

    def _export_all(self) -> None:
        if not self.script:
            self.notify("请先生成脚本", severity="warning")
            return
        outdir = Path("output") / strftime("%Y%m%d-%H%M%S")
        outdir.mkdir(parents=True, exist_ok=True)
        stem = self.script.meta.title or "script"
        paths = [
            outdir / f"{stem}.yaml",
            outdir / f"{stem}.md",
            outdir / f"{stem}.json",
        ]
        try:
            paths[0].write_text(to_yaml(self.script), encoding="utf-8")
            paths[1].write_text(to_markdown(self.script), encoding="utf-8")
            paths[2].write_text(to_json(self.script), encoding="utf-8")
        except OSError as exc:
            self.notify(f"写入失败：{exc}", severity="error")
            return
        for path in paths:
            _log_line(self.query_one("#log", RichLog), f"已导出 {path}")
        self.notify(f"已导出 3 个文件到 {outdir}", severity="information")

    def _open_advanced(self) -> None:
        self.push_screen(
            AdvancedScreen(
                {
                    "style": self.style,
                    "tone": self.tone,
                    "audience": self.audience,
                    "language": self.language,
                }
            ),
            self._after_advanced,
        )

    def _after_advanced(self, result: dict | None) -> None:
        if not result:
            return
        self.style = result.get("style", self.style)
        self.tone = result.get("tone", self.tone)
        self.audience = result.get("audience", self.audience)
        self.language = result.get("language", self.language)
        self.notify("高级设定已更新", severity="information")

    def _show_questions(self) -> None:
        self.query_one("#preview", Markdown).update(question_chain_text())
        self.query_one(TabbedContent).active = "tab-preview"

    # ------------------------------------------------------------ 事件与快捷键

    @on(Button.Pressed, "#generate")
    def _on_generate(self) -> None:
        self._start_generate()

    @on(Button.Pressed, "#demo")
    def _on_demo(self) -> None:
        self._start_generate(MockBackend())

    @on(Button.Pressed, "#advanced")
    def _on_advanced(self) -> None:
        self._open_advanced()

    @on(Button.Pressed, "#validate")
    def _on_validate(self) -> None:
        self._validate()

    @on(Button.Pressed, "#edit")
    def _on_edit(self) -> None:
        self._open_editor()

    @on(Button.Pressed, "#regen")
    def _on_regen(self) -> None:
        self._start_regen()

    @on(Button.Pressed, "#export")
    def _on_export(self) -> None:
        self._export_all()

    @on(Button.Pressed, "#show-questions")
    def _on_show_questions(self) -> None:
        self._show_questions()

    def action_generate(self) -> None:
        self._start_generate()

    def action_edit_shot(self) -> None:
        self._open_editor()

    def action_regen_shot(self) -> None:
        self._start_regen()

    def action_validate_script(self) -> None:
        self._validate()

    def action_export_all(self) -> None:
        self._export_all()

    def action_advanced(self) -> None:
        self._open_advanced()

    def _require_shot(self) -> bool:
        if not self.script:
            self.notify("请先生成脚本", severity="warning")
            return False
        if not self.current_shot_id:
            self.notify("请先在分镜表里选中一行", severity="warning")
            return False
        return True


def launch(offline: bool = False) -> None:
    AIVScriptApp(offline=offline).run()
