"""aivscript — AI 视频脚本自动生成器（TUI）。"""
from .models import DSL_VERSION, Script
from .generator import GenInput, Generator, MockBackend, LLMBackend, build_backend
from .serialize import (
    from_json,
    from_markdown,
    from_yaml,
    to_json,
    to_markdown,
    to_yaml,
)
from .validate import validate

__all__ = [
    "DSL_VERSION",
    "Script",
    "GenInput",
    "Generator",
    "MockBackend",
    "LLMBackend",
    "build_backend",
    "to_yaml",
    "from_yaml",
    "to_markdown",
    "from_markdown",
    "to_json",
    "from_json",
    "validate",
]
__version__ = "0.1.0"
