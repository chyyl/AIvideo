"""命令行入口：默认启动 TUI，也支持无界面生成、校验与格式转换。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import GenInput, Generator, build_backend
from .serialize import from_json, from_markdown, from_yaml, to_json, to_markdown, to_yaml
from .validate import validate


def _load(path: str):
    text = Path(path).read_text(encoding="utf-8")
    suffix = Path(path).suffix.lower()
    if suffix in (".yaml", ".yml"):
        return from_yaml(text)
    if suffix == ".json":
        return from_json(text)
    if suffix in (".md", ".markdown"):
        return from_markdown(text)
    raise SystemExit(f"不支持的文件类型：{suffix}（支持 .yaml/.yml/.json/.md）")


def _cmd_generate(args: argparse.Namespace) -> int:
    backend = build_backend(offline=args.offline)
    inp = GenInput(
        theme=args.theme,
        genre=args.genre,
        style=args.style,
        tone=args.tone,
        target_duration=args.duration,
        aspect_ratio=args.ratio,
        audience=args.audience,
    )

    def progress(stage: str, message: str) -> None:
        print(f"  · {message}")

    script = Generator(backend, progress).generate(inp)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    suffix = out.suffix.lower()
    if suffix in (".yaml", ".yml"):
        out.write_text(to_yaml(script), encoding="utf-8")
    elif suffix == ".json":
        out.write_text(to_json(script), encoding="utf-8")
    elif suffix in (".md", ".markdown"):
        out.write_text(to_markdown(script), encoding="utf-8")
    else:
        raise SystemExit("输出文件需以 .yaml / .json / .md 结尾")
    issues = validate(script)
    print(f"已写入 {out}（{len(list(script.shots))} 镜 / {script.duration:g}s）")
    for issue in issues:
        print(f"  ! {issue}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    script = _load(args.file)
    issues = validate(script)
    if not issues:
        print("校验通过：没有发现问题")
        return 0
    for issue in issues:
        print(issue)
    return 1 if any(i.level == "error" for i in issues) else 0


def _cmd_convert(args: argparse.Namespace) -> int:
    script = _load(args.file)
    target = args.to.lower()
    out = Path(args.out) if args.out else Path(args.file).with_suffix(f".{target}")
    if target in ("yaml", "yml"):
        text = to_yaml(script)
    elif target == "md":
        text = to_markdown(script)
    elif target == "json":
        text = to_json(script)
    else:
        raise SystemExit("--to 只支持 yaml / md / json")
    out.write_text(text, encoding="utf-8")
    print(f"已写入 {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aivscript", description="AI 视频脚本自动生成器（TUI + DSL）"
    )
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="启动 TUI（默认命令）")
    run.add_argument("--offline", action="store_true", help="强制离线 Mock 模式")

    gen = sub.add_parser("generate", help="无界面生成脚本")
    gen.add_argument("--theme", required=True)
    gen.add_argument("--genre", default="情感")
    gen.add_argument("--style", default="自然光、低饱和")
    gen.add_argument("--tone", default="克制")
    gen.add_argument("--duration", type=int, default=120)
    gen.add_argument("--ratio", default="16:9")
    gen.add_argument("--audience", default="通用受众")
    gen.add_argument("--out", default="output/script.yaml")
    gen.add_argument("--offline", action="store_true")

    val = sub.add_parser("validate", help="校验脚本")
    val.add_argument("file")

    conv = sub.add_parser("convert", help="格式转换（YAML/MD/JSON）")
    conv.add_argument("file")
    conv.add_argument("--to", required=True, choices=["yaml", "yml", "md", "json"])
    conv.add_argument("--out")
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    if not argv or argv[0] in ("-h", "--help"):
        parser.print_help()
        return 0
    if argv[0] not in {"run", "generate", "validate", "convert"}:
        argv.insert(0, "run")
    args = parser.parse_args(argv)

    if args.command == "generate":
        return _cmd_generate(args)
    if args.command == "validate":
        return _cmd_validate(args)
    if args.command == "convert":
        return _cmd_convert(args)

    from .app import launch

    launch(offline=getattr(args, "offline", False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
