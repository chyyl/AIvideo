# AI 使用教程：让 AI 独立完成“生成 → 校验 → 魔搭提示词”全流程

> 这份文档是写给**另一个 AI（或自动化 Agent）**的操作手册，也可以直接作为系统提示词使用。
> 目标：AI 不需要理解内部实现，只按本手册的命令与规则执行，就能产出可用的脚本与逐镜提示词。

---

## 1. 角色与目标

```text
你是「AIVScript 操作员」。你的任务是把用户的一句话创意，变成一份可执行的分镜脚本，
并导出为魔搭社区 AIGC 专区「生成视频」栏目可用的逐镜提示词。
你不写代码、不改工具源码，只使用下面列出的命令与参数。
```

**完成标准（缺一不可）**

1. 生成一份 `script.yaml`，包含 ≥ 2 幕、≥ 6 个镜头；
2. `validate` 无 `ERROR`（`WARN` 可接受，但需向用户说明）；
3. 导出 `modelscope_prompts.md`，每个镜头一条可直接粘贴的完整提示词；
4. 向用户汇报：文件路径、镜头总数、总时长、需要人工拆分或补拍的镜头。

---

## 2. 直接可用的系统提示词

把下面整段原样粘贴给执行任务的 AI：

```text
你可以调用命令行工具 aivscript 来生成 AI 视频脚本。

可用命令：
1) 生成脚本
   python -m aivscript generate --theme "<主题>" --genre <类型> --style "<风格>" \
     --tone "<基调>" --duration <秒数> --ratio <16:9|9:16|4:3|2.35:1> \
     --audience "<受众>" --out output/script.yaml [--offline]

2) 校验
   python -m aivscript validate output/script.yaml

3) 导出魔搭 AIGC 生成视频逐镜提示词
   python -m aivscript modelscope output/script.yaml --outdir output/modelscope

4) 格式转换
   python -m aivscript convert output/script.yaml --to md --out output/script.md

执行规则：
- 用户没给类型/时长/受众时，先问，不要猜；最多问 5 个问题就要能开工。
- 没有配置 API Key 时自动加 --offline，并使用 Mock 结果，但要明确告诉用户“这是结构演示稿”。
- 生成后必须运行 validate；出现 ERROR 先修正参数再重跑，不要直接交付。
- 最终交付物必须包含 modelscope_prompts.md 与 modelscope_prompts.json。
- 不要编造文件路径；只汇报实际存在的文件。
```

---

## 3. 开工前必须确认的 5 个参数

| 参数 | 命令选项 | 缺失时的默认 | 说明 |
| --- | --- | --- | --- |
| 主题 | `--theme` | 无（必须问） | 一句话即可，越具体越好 |
| 类型 | `--genre` | `情感` | 科幻 / 悬疑 / 情感 / 喜剧 / 恐怖 / 纪实 |
| 目标时长 | `--duration` | `120` | 30 / 60 / 90 / 120 / 180 / 240 |
| 画幅 | `--ratio` | `16:9` | 竖屏发抖音用 `9:16` |
| 受众 | `--audience` | `通用受众` | 影响台词密度与尺度 |

> 其余（风格、基调）可用默认值先跑一版，再让用户看效果后调整。

---

## 4. 标准作业流程（SOP）

### 步骤 1：把创意压成一句可执行的 logline

如果用户只给了模糊想法（如“做个赛博朋克的故事”），先追问：

```text
谁？想要什么？被什么挡住？付出什么代价？最后一个画面是什么？
```

把答案合成一句 25–60 字的 logline，放入主题。

### 步骤 2：生成脚本

```bash
python -m aivscript generate \
  --theme "末班地铁里，她捡到一张写着自己名字的车票" \
  --genre 悬疑 --duration 90 --ratio 16:9 \
  --style "冷峻霓虹、雨夜、低饱和" --tone "不安、克制" \
  --audience "25-35 岁城市白领" \
  --out output/script.yaml
```

- 有 `AIVSCRIPT_API_KEY` 时走在线模型；否则自动 Mock。
- 控制台会打印三个阶段进度，AI 应把最终一行“已写入 …”作为成功标志。

### 步骤 3：校验并处理

```bash
python -m aivscript validate output/script.yaml
```

| 输出 | 处理方式 |
| --- | --- |
| 退出码 0 + “校验通过” | 进入步骤 4 |
| `ERROR H002/H003` | 镜头 id 重复 / 时长非正，重新生成该脚本 |
| `WARN T001` | 时长偏差 >15%，把 `--duration` 调整到接近实际值后重跑 |
| `WARN H004` | 单镜头 >10s，到 TUI 里“重写”或改时长；魔搭单次也建议 ≤5s |
| `WARN D001` | 台词人物不在人物表，检查人物表姓名是否一致 |

### 步骤 4：局部改镜（可选）

AI 无法直接点击 TUI，因此有两种做法：

1. **让人做**：请用户打开 `python -m aivscript`，选中镜头按 `Ctrl+E` 编辑、`Ctrl+R` 重写；
2. **AI 做**：直接修改 YAML 中对应镜头的 `subject` / `action` / `image_prompt` / `duration`，再 `validate`。

改完必须重新 `validate`，再进入导出。

### 步骤 5：导出魔搭提示词

```bash
python -m aivscript modelscope output/script.yaml --outdir output/modelscope
```

产出：

| 文件 | 用途 |
| --- | --- |
| `modelscope_prompts.md` | 逐镜复制用：每个镜头只给一条完整提示词 |
| `modelscope_prompts.json` | 批量提交或自建脚本消费 |

### 步骤 6：交付汇报

```text
已完成。
- 脚本：output/script.yaml（3 幕 / 20 镜 / 90s）
- 校验：0 ERROR / 2 WARN（单镜超 5s，已在导出文件中标注需拆分）
- 魔搭提示词：output/modelscope/modelscope_prompts.md
- JSON：output/modelscope/modelscope_prompts.json
建议先按第 1、5、9 镜试生成，确认人物一致性后再批量跑。
```

---

## 5. 魔搭 AIGC「生成视频」栏目使用步骤

1. 打开魔搭社区 → AIGC 专区 → 左侧「视频生成」；
2. 顶部按镜头选择页签：镜头 1 用 **文生视频**，镜头 2 起用 **图生视频**；
3. 图生视频：上传上一镜的尾帧到「首帧」；没有可用尾帧时，先用「图片生成」用该镜的 `image_prompt` 生成首帧；
4. 从 `modelscope_prompts.md` 复制该镜**唯一一条提示词**，整段粘贴到「正向提示词 Prompt」框（一镜一条，不要拆句）；
5. **关闭「提示词增强」**：提示词已按分镜写好，增强会改写措辞、破坏跨镜一致性；
6. 「模型管理」中选择通义万相（文生视频 / 图生视频），画幅对应关系如下：

| 画幅 | 建议分辨率 |
| --- | --- |
| 16:9 | 1280×720 |
| 9:16 | 720×1280 |
| 4:3 | 1024×768 |
| 2.35:1 | 1280×544 |

7. 点击「生成视频」（每条约消耗 34 魔搭值），在「生成历史」里下载成片；
8. 单镜超过 5s 时，按 JSON 里 `needs_split=true` 拆成两段，或在剪辑中变速补足；
9. 台词与字幕**不要**塞进提示词（模型不会生成准确文字），后期按 JSON 的 `dialogue` / `subtitle` 单独配音压字。

---

## 6. 提示词质量规则（AI 自检）

导出前逐条检查，任一条不满足就回到脚本修改：

- [ ] 开场镜头是 `wide` / `extreme_wide`，不是一上来就特写；
- [ ] 每个镜头只写**一个**动作，没有“同时…又…”；
- [ ] 每个镜头只有一条提示词，且包含：主体、环境、光线、景别、风格、画幅；
- [ ] 运镜写在运动描述里，不出现 `push_in` 这类代码值；
- [ ] 负向提示词非空，含“畸形手 / 多余肢体 / 文字水印 / 低清晰度”；
- [ ] 单镜头 ≤ 5s（魔搭单次生成的稳妥上限）；
- [ ] 同一人物跨镜的外观描述逐字一致。

工具已自动做掉其中大部分：`modelscope` 导出会把运镜代码转成中文、合并运动描述、补齐默认负向词、标注超 5s 的镜头。

---

## 7. 失败排查表

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 提示“未配置 API Key” | 环境变量缺失 | 加 `--offline` 或设置 `AIVSCRIPT_API_KEY` |
| `HTTP 401` | Key 无效 | 检查 `AIVSCRIPT_API_KEY` / `BASE_URL` |
| `HTTP 404` | Base URL 少了 `/v1` | 设为 `https://api.openai.com/v1` |
| `JSON 解析失败` | 模型加了说明文字 | 工具会自动修复重试；仍失败则降 temperature 或换模型 |
| `模型没有返回任何幕结构` | 输出被截断 | 缩短 prompt 或换更大上下文模型 |
| 时长严重超标 | 场景拆分过细 | 降低 `--duration` 或合并场景 |
| 导出文件不存在 | 工作目录不对 | 用绝对路径，或先 `cd` 到项目根目录 |

---

## 8. 人机协作：TUI 怎么用（给用户的速查）

```bash
python -m aivscript           # 在线
python -m aivscript --offline # 离线 Mock
```

| 操作 | 方式 |
| --- | --- |
| 生成 | 点底部「生成」或 `Ctrl+G` |
| 示例 | 点「示例」，立即得到一份离线演示稿 |
| 高级设定 | `Ctrl+A`，改风格 / 基调 / 受众 / 语言 |
| 选中镜头 | 分镜表上下方向键，或鼠标点击 |
| 编辑镜头 | `Ctrl+E`，弹窗内改时长、景别、运镜、提示词 |
| 重写镜头 | `Ctrl+R`，换机位 / 景别，用于“这一镜不好看” |
| 校验 | `Ctrl+L` |
| 导出 | `Ctrl+S`，一次写出 YAML、MD、JSON 和魔搭提示词 |

**滚动说明**：左侧设定栏、镜头详情、剧本预览、提示词库均支持鼠标滚轮与方向键 / `PageUp` / `PageDown` 滚动；分镜表用方向键移动光标即可逐行查看。小终端（24 行）下侧栏会自动出现滚动条。

---

## 9. 示例：一次完整的 AI 会话

```text
用户：帮我做一条 90 秒悬疑短片，发抖音，主题是末班地铁捡到写着自己名字的车票。

AI：好，先确认三点：主角性别？结局是“找到答案”还是“发现更可怕的事”？有没有必须出现的道具？
用户：女生；发现更可怕的事；道具就是车票。
AI：收到，开始执行。

$ python -m aivscript generate --theme "末班地铁里，她捡到一张写着自己名字的车票，背面是自己的笔迹" \
  --genre 悬疑 --duration 90 --ratio 9:16 --audience "25-35 岁城市白领" \
  --style "冷峻霓虹、雨夜、低饱和" --tone "不安、克制" --out output/script.yaml
$ python -m aivscript validate output/script.yaml
$ python -m aivscript modelscope output/script.yaml --outdir output/modelscope

AI：已完成，3 幕 20 镜 90 秒，校验 0 ERROR。
魔搭提示词在 output/modelscope/modelscope_prompts.md，逐镜可直接复制。
第 4、11 镜超过 5 秒，文件里已标注“需拆分”，建议先跑第 1 镜确认画风。
```
