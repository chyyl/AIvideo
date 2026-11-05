# AIVScript

AI 视频脚本自动生成器：**Textual TUI** + **YAML 分镜 DSL** + **提示词库**。

输入一句主题，三阶段生成可直接执行的短片脚本（幕 / 场景 / 节拍 / 镜头 / 中英提示词），在终端里编辑、校验、预览，并导出 YAML / Markdown / JSON。

```
┌ AIVScript · AI 视频脚本生成器 ───────────────────────────────┐
│ ① 创作设定            │ 《末班地铁》 · 3 幕 · 20 镜 · 90s      │
│ [高级设定 Ctrl+A]     │ ┌ 分镜表 ┬ 剧本预览 ┬ 镜头详情 ┬ 提示词库 ┐│
│ 主题  [末班地铁…]     │ │ shot-1-1-1  4.0s  wide  push_in …      ││
│ 类型  [悬疑     ▾]    │ │ shot-1-1-2  4.0s  medium static …      ││
│ 时长  [90 秒    ▾]    │ └───────────────────────────────────────┘│
│ 画幅  [16:9     ▾]    │ 日志：阶段 1/3 → 2/3 → 3/3               │
│                       │ [生成] [示例] [校验] [编辑] [重写] [导出]│
└───────────────────────────────────────────────────────────────┘
```

## 特性

- **开箱即用**：无 API Key 时自动进入离线 Mock 模式，完整跑通生成 → 编辑 → 导出。
- **提示词驱动**：三阶段串行调用（立意 → 场景 → 分镜），每阶段强制严格 JSON，解析失败自动修复重试。
- **双轨脚本**：YAML 是规范格式，Markdown 是人读剧本，二者可无损互转（见 [格式标准](docs/SCRIPT_FORMAT_SPEC.md)）。
- **TUI 全流程**：分镜表、剧本预览、镜头详情、提示词库、单镜头编辑 / 重写、静态校验、一键导出。
- **任意 OpenAI 兼容端点**：OpenAI、DeepSeek、Moonshot、自建中转均可。

## 安装

```bash
pip install -e .
# 或仅安装依赖后以模块方式运行
pip install textual pyyaml
```

要求 Python ≥ 3.10。

## 使用

### TUI

```bash
python -m aivscript              # 启动
python -m aivscript run --offline # 强制离线 Mock
```

| 快捷键 | 作用 |
| --- | --- |
| `Ctrl+G` | 生成脚本 |
| `Ctrl+A` | 高级设定（风格 / 基调 / 受众 / 语言） |
| `Ctrl+E` | 编辑当前镜头 |
| `Ctrl+R` | 重写当前镜头（换机位/景别） |
| `Ctrl+L` | 校验 |
| `Ctrl+S` | 导出全部（YAML + MD + JSON） |
| `Ctrl+Q` | 退出 |

导出目录：`output/<时间戳>/`。

### 命令行

```bash
# 生成
python -m aivscript generate --theme "末班地铁里，她捡到一张车票" \
  --genre 悬疑 --duration 90 --out output/demo.yaml --offline

# 校验（有 ERROR 时退出码为 1）
python -m aivscript validate output/demo.yaml

# 格式转换
python -m aivscript convert output/demo.yaml --to md
python -m aivscript convert output/demo.md --to json
```

### 接入模型

```bash
export AIVSCRIPT_API_KEY=sk-xxx
export AIVSCRIPT_BASE_URL=https://api.openai.com/v1   # 可换成任意兼容端点
export AIVSCRIPT_MODEL=gpt-4o-mini
python -m aivscript
```

兼容回退变量：`OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL`。

## 项目结构

```
aivscript/
├── models.py        # DSL 数据模型（Script/Act/Scene/Beat/Shot…）
├── serialize.py     # YAML / JSON / Markdown 导出与解析
├── validate.py      # 24 条静态校验规则
├── llm.py           # OpenAI 兼容客户端（标准库实现）
├── prompts.py       # 提示词库 + 42 问提问链
├── generator.py     # 三阶段管线 + 离线 Mock 后端
├── app.py           # Textual TUI
└── __main__.py      # CLI
docs/
├── SCRIPT_FORMAT_SPEC.md   # 语言格式标准 v1.0
└── PROMPTING_GUIDE.md      # 文本 AI + 提问生成剧情的方法与 42 问
examples/
├── demo.yaml
└── demo.md
```

## 文档

- [脚本语言格式标准 v1.0](docs/SCRIPT_FORMAT_SPEC.md) — 字段、枚举、校验规则、Markdown 文法、转换矩阵。
- [提示词与提问指南](docs/PROMPTING_GUIDE.md) — 六轮 42 问、创作简报模板、单场戏三步法、批评式迭代。

## 测试

```bash
pytest -q
```

覆盖：三阶段生成、时长预算、YAML/MD/JSON 往返一致性、校验规则、TUI 无头交互。

## 边界

- 只负责“脚本层”，不调用绘图 / 视频 / TTS API；`image_prompt`、`video_prompt` 直接对接下游即可。
- 离线 Mock 产出的是结构完整但内容模板化的演示脚本，用于验证流程，不用于正式创作。
- Markdown 解析只保证工具自身生成的格式（见规范 §9.3）。
