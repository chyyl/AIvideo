# AI 视频脚本语言格式标准 v1.0

> 标识：`aivscript/1.0`　｜　适用范围：短片 / 广告 / 剧情切片 / AI 视频分镜　｜　状态：草案
>
> 本文件是 `aivscript` 工具链的**唯一权威格式规范**。YAML 是规范格式（canonical），Markdown 是面向人的等价视图，JSON 是面向机器的等价交换格式。

---

## 1. 设计目标

| 目标 | 说明 |
| --- | --- |
| 可读 | 编剧能直接读懂并手改，不依赖工具 |
| 可执行 | 每个镜头自带时长、景别、运镜、提示词，可直接驱动绘图 / 图生视频 / TTS |
| 可校验 | 结构、引用、时长预算均可静态检查，错误在生成前暴露 |
| 可转换 | YAML ↔ Markdown ↔ JSON 无损往返（唯一例外见 §11） |
| 可演进 | 版本号在文件内声明，未知字段忽略，缺失字段取默认值 |

**非目标**：不做剪辑时间线、不做多轨音频工程、不做项目管理（这些由下游工具承担）。

---

## 2. 文件与命名

```
project/
├── script.yaml        # 规范格式，唯一事实来源
├── script.md          # 人读剧本（可由 yaml 生成，也可反向导入）
├── script.json        # 程序消费
└── assets/            # 参考图、配音、成片（可选）
```

推荐扩展名：`.yaml` / `.yml` / `.md` / `.json`。编码统一 UTF-8（无 BOM）。

---

## 3. 顶层结构

```yaml
dsl: aivscript/1.0        # 必填，格式版本
meta: {...}               # 必填，全片元信息
characters: [...]         # 建议，人物表
acts: [...]               # 必填，幕 → 场景 → 节拍 → 镜头
```

层级关系：

```
Script
├── meta
├── characters[]
└── acts[]
    └── scenes[]
        ├── beats[]        # 剧情节拍（文本层）
        └── shots[]        # 分镜（执行层）
            └── dialogue[]
```

> 设计要点：`beats` 解决“讲什么”，`shots` 解决“怎么拍”。同一场景里两者并存，便于先改剧情再重排镜头。

---

## 4. 字段规范

### 4.1 `meta`

| 字段 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `title` | string | 是 | 1–30 字 | 片名 |
| `logline` | string | 建议 | 25–60 字 | 一句话故事：主角 + 目标 + 阻碍 + 代价 |
| `genre` | string | 建议 | 见 §5 | 类型 |
| `style` | string | 建议 | 自由文本 | 视觉风格关键词，会拼进每条提示词 |
| `language` | string | 是 | BCP-47，如 `zh-CN` | 字幕 / 配音语言 |
| `aspect_ratio` | string | 是 | `16:9` `9:16` `4:3` `2.35:1` | 画幅，会拼进提示词 |
| `target_duration` | int | 是 | > 0，单位秒 | 目标成片时长，用于时长预算校验 |
| `audience` | string | 否 | 自由文本 | 受众，影响措辞与尺度 |
| `tone` | string | 否 | 自由文本 | 情绪基调 |

### 4.2 `characters[]`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | string | 是 | 全片唯一，建议 `char-1` |
| `name` | string | 是 | 显示名，台词中的 `character` 必须与之完全一致 |
| `role` | string | 是 | 主角 / 对手 / 同伴 / 功能角色 |
| `age` | string | 否 | 可写区间，如 `30 岁上下` |
| `appearance` | string | 建议 | 可直接写入绘图提示词的外观描述（发型、服装、标志物） |
| `voice` | string | 否 | 音色、语速、口音，用于 TTS 选型 |
| `arc` | string | 否 | 人物弧光，供模型保持人物一致性 |

### 4.3 `acts[]`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | string | 是 | 建议 `act-1` |
| `title` | string | 是 | 如 `第一幕 · 日常的裂缝` |
| `summary` | string | 建议 | 本幕叙事功能（建置 / 对抗 / 转折） |
| `scenes` | array | 是 | 至少 1 个场景 |

### 4.4 `scenes[]`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | string | 是 | 建议 `scene-1-1`（幕序号-场景序号） |
| `heading` | string | 是 | 场次标题，格式 `INT./EXT. 地点 - 时间` |
| `location` | string | 是 | 地点，用于提示词 |
| `time_of_day` | enum | 是 | `dawn` `morning` `noon` `afternoon` `dusk` `night` |
| `weather` | string | 否 | 雨、雾、雪等，影响画面 |
| `summary` | string | 建议 | 该场戏的戏剧功能 |
| `beats` | array | 建议 | 剧情节拍，见 4.5 |
| `shots` | array | 是 | 分镜，至少 1 个 |

### 4.5 `beats[]`（剧情节拍）

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | string | 否 | 可省略，由工具补 `scene-id-beat-N` |
| `type` | enum | 是 | `action` / `dialogue` / `transition` / `montage` |
| `text` | string | 是 | 节拍内容。dialogue 时**不含**人物名前缀 |
| `character` | string | dialogue 时必填 | 说话人姓名，须在人物表中 |
| `delivery` | string | 否 | 语气 / 音量，如 `压低声` |

### 4.6 `shots[]`（分镜）

| 字段 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | string | 是 | 全片唯一 | 建议 `shot-1-1-1` |
| `order` | int | 是 | 场景内从 1 递增 | 镜头顺序 |
| `duration` | float | 是 | 0 < d ≤ 10（秒） | 单镜头时长，超过 10s 触发警告 |
| `shot_size` | enum | 是 | 见 §5 | 景别 |
| `camera` | enum | 是 | 见 §5 | 运镜 |
| `subject` | string | 是 | ≤ 40 字 | 画面里最显眼的主体 |
| `action` | string | 是 | 一个镜头一个动作 | 画面内发生的事 |
| `dialogue` | array | 否 | — | 见 4.7 |
| `sfx` | string[] | 否 | — | 音效列表 |
| `bgm` | string | 否 | — | 配乐提示 |
| `subtitle` | string | 否 | — | 字幕文本（无台词但需要字幕时使用） |
| `image_prompt.zh` | string | 建议 | 60–120 字 | 中文绘图提示词 |
| `image_prompt.en` | string | 建议 | 40–90 词 | 英文绘图提示词，末尾含画幅与 `cinematic` |
| `video_prompt` | string | 建议 | 只写运动与时间变化 | 图生视频提示词 |
| `negative_prompt` | string | 否 | — | 排除项 |
| `transition_out` | enum | 是 | 见 §5 | 与下一镜的衔接 |
| `notes` | string | 否 | — | 制作备注 |

### 4.7 `dialogue[]`

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `character` | string | 是 | 与 `characters[].name` 一致 |
| `text` | string | 是 | 台词正文，建议 ≤ 20 字 / 句 |
| `delivery` | string | 否 | 表演提示 |

---

## 5. 枚举值

**景别 `shot_size`**

| 值 | 中文 | 用途 |
| --- | --- | --- |
| `extreme_wide` | 大远景 | 交代环境、孤独感 |
| `wide` | 远景 | 建立空间关系 |
| `full` | 全景 | 人物全身 + 环境 |
| `medium` | 中景 | 常规叙事 |
| `medium_close` | 中近景 | 对话 |
| `close` | 特写 | 情绪 |
| `extreme_close` | 大特写 | 细节 / 压迫感 |

**运镜 `camera`**：`static` `push_in` `pull_out` `pan_left` `pan_right` `tilt_up` `tilt_down` `tracking` `handheld` `crane_up` `orbit`

**转场 `transition_out`**：`cut` `fade_in` `fade_out` `dissolve` `wipe` `match_cut` `flash`

**节拍类型**：`action` `dialogue` `transition` `montage`

**时间**：`dawn` `morning` `noon` `afternoon` `dusk` `night`

> 未知枚举值不会被拒绝，但产生 `WARN`，便于格式演进。

---

## 6. 时间码与时长预算

- 镜头起始时间由**顺序累计**得出，不写入源文件：

  ```
  start(0) = 0
  start(n) = start(n-1) + duration(n-1)
  ```

- 场景时长 = 该场景所有镜头 `duration` 之和。
- 幕时长 = 该幕所有场景之和；全片时长 = 所有幕之和。
- 时间码格式 `MM:SS.ss`，仅在 Markdown / 派生视图中出现。
- 校验：`|全片时长 - meta.target_duration| > 15%` → `WARN T001`。

---

## 7. 校验规则

校验器输出的问题分 `ERROR`（阻断导出）与 `WARN`（提示）。

| 编号 | 级别 | 含义 |
| --- | --- | --- |
| `M001` | ERROR | `meta.title` 为空 |
| `M002` | WARN | 缺少 logline |
| `M003` | ERROR | `target_duration` 非正 |
| `A001` | ERROR | 没有任何幕 |
| `A002` | ERROR | 某幕没有场景 |
| `A003` | WARN | 某幕缺标题 |
| `A004` | WARN | 幕数 > 5 |
| `C001` | WARN | 没有人物表 |
| `C002` | ERROR | 人物 id 为空 |
| `C003` | ERROR | 人物 id 重复 |
| `S001` | WARN | 场景没有分镜 |
| `S002` | WARN | 场景缺场次标题 |
| `H001` | ERROR | 镜头 id 为空 |
| `H002` | ERROR | 镜头 id 重复 |
| `H003` | ERROR | 镜头时长 ≤ 0 |
| `H004` | WARN | 镜头时长 > 10s |
| `H005` | WARN | 未知景别 |
| `H006` | WARN | 未知运镜 |
| `H007` | WARN | 未知转场 |
| `H008` | WARN | 缺少镜头主体 |
| `H009` | WARN | 镜头 order 未升序 |
| `D001` | WARN | 台词人物不在人物表 |
| `D002` | WARN | 空台词行 |
| `T001` | WARN | 时长偏差超过 15% |

---

## 8. 完整 YAML 示例（节选）

```yaml
dsl: aivscript/1.0
meta:
  title: 末班地铁
  logline: 末班地铁里，她捡到一张写着自己名字的车票，却从未买过票。
  genre: 悬疑
  style: 冷峻霓虹、雨夜、低饱和
  language: zh-CN
  aspect_ratio: '16:9'
  target_duration: 90
  audience: 25-35 岁城市观众
  tone: 不安、克制
characters:
  - id: char-1
    name: 阿岚
    role: 主角
    age: 30 岁上下
    appearance: 短发，深灰风衣，右手腕有一道旧疤
    voice: 语速慢，停顿多
    arc: 从回避到承认
acts:
  - id: act-1
    title: 第一幕 · 日常的裂缝
    summary: 建置
    scenes:
      - id: scene-1-1
        heading: INT. 出租屋 - 夜
        location: 出租屋
        time_of_day: night
        weather: 小雨
        summary: 阿岚回到家，发现口袋里的车票。
        beats:
          - id: scene-1-1-beat-1
            type: action
            text: 她把外套挂上，口袋里掉出一张车票。
          - id: scene-1-1-beat-2
            type: dialogue
            character: 阿岚
            delivery: 低声
            text: 我没有买过。
        shots:
          - id: shot-1-1-1
            order: 1
            duration: 4.0
            shot_size: wide
            camera: push_in
            subject: 出租屋唯一亮着的台灯
            action: 灯光把雨影投在墙上
            dialogue: []
            sfx: [雨声, 冰箱低频]
            bgm: 低频弦乐
            subtitle: ''
            image_prompt:
              zh: 远景，出租屋唯一亮着的台灯，窗上雨痕，冷蓝与暖黄对比，胶片颗粒，16:9
              en: wide shot of a dim apartment lit by a single lamp, rain streaks on the
                window, teal and amber contrast, film grain, 16:9 aspect ratio, cinematic
            video_prompt: 缓慢推近，雨影在墙上移动
            negative_prompt: 畸形手、多余肢体、文字水印、低清晰度
            transition_out: cut
            notes: 建立镜头，控制在 4s
```

完整文件见 [examples/demo.yaml](../examples/demo.yaml)。

---

## 9. Markdown 剧本格式

Markdown 是**固定文法**，不是自由排版。工具按下列规则生成，也按同一规则解析。

### 9.1 文法

```
# 《片名》
> 一句话故事：<logline>

## 基本信息
- 类型：...
- 视觉风格：...
- 语言：...
- 画幅：...
- 受众：...
- 基调：...
- 目标时长：<n> 秒

## 人物
### <姓名>
- 角色：...
- 年龄：...
- 外观：...
- 声音：...
- 人物弧光：...

## <幕标题>
> <幕摘要>

### <场次标题>
- 地点：...
- 时间：...
- 天气：...

> <场景摘要>

#### 剧情节拍
- [动作] ...
- [对话] 姓名（语气）：...

#### 分镜
| ID | # | 时长 | 景别 | 运镜 | 主体 | 动作 | 转场 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shot-1-1-1 | 1 | 4 | wide | push_in | ... | ... | cut |

##### 镜头 <shot-id> 细节
- 时间码：00:00.00 → 00:04.00
- 台词：姓名（语气）：文本
- 音效：...
- 配乐：...
- 字幕：...
- 图像提示词（中文）：...
- 图像提示词（英文）：...
- 视频提示词：...
- 负面提示词：...
- 备注：...
```

### 9.2 约束

1. 各级标题必须使用 `#` / `##` / `###` / `####` / `#####` 的固定层级，层级错位会导致解析失败。
2. 键值行必须是 `- 键：值`（全角冒号）或 `- 键: 值`，**不要**写成 `**键**：值`。
3. 表格列顺序固定；单元格中的 `|` 写作 `\|`。
4. 镜头 ID 在表格与 `#####` 标题中必须一致；缺失时按 `shot-{幕}-{场景}-{序号}` 补齐。
5. 空值行可省略；解析时取默认值。

### 9.3 无损性

YAML → Markdown → YAML 在下列条件下**字节级数据等价**：

- 使用工具生成的 Markdown；
- 不手工改动 ID；
- 不删除 `##### 镜头` 细节段。

导出后再导入时，`order` 会按出现顺序重新编号，`id` 保持不变。

---

## 10. JSON 交换格式

与 YAML 完全同构，仅编码不同：

- UTF-8，`ensure_ascii=false`；
- 2 空格缩进；
- 键顺序保持 `dsl → meta → characters → acts`。

适合下游程序（TTS 批处理、绘图队列、剪辑脚本）直接消费。

---

## 11. 转换矩阵

| 源 → 目标 | YAML | Markdown | JSON |
| --- | --- | --- | --- |
| YAML | — | 无损* | 无损 |
| Markdown | 无损* | — | 无损* |
| JSON | 无损 | 无损* | — |

\* 无损指 §9.3 的字段等价；不包含注释、缩进、空行等排版信息。

命令行：

```bash
python -m aivscript convert script.yaml --to md --out script.md
python -m aivscript convert script.md  --to json
```

---

## 12. 版本演进

- 版本号格式 `aivscript/<major>.<minor>`。
- 新增可选字段 → 升 minor，旧解析器忽略未知键。
- 修改枚举含义 / 必填性 → 升 major，需提供迁移脚本。
- 解析器遇到 `dsl` 缺失时按 `1.0` 处理，并给出 `WARN`。

### 已知扩展点（未实现，保留命名）

| 预留字段 | 位置 | 用途 |
| --- | --- | --- |
| `voice_id` | characters | 绑定 TTS 音色 |
| `ref_image` | characters | 角色参考图，保证一致性 |
| `seed` | shots | 生成随机种子，便于复现 |
| `model` | shots | 指定绘图 / 视频模型 |
| `lip_sync` | shots | 口型同步参数 |

---

## 13. 魔搭 AIGC「生成视频」导出映射

`python -m aivscript modelscope <script.yaml> --outdir <dir>` 按**镜头**展开，输出 `modelscope_prompts.md` 与 `modelscope_prompts.json`。

### 13.1 字段映射

| 输出字段 | 来源 | 规则 |
| --- | --- | --- |
| `prompt` | `image_prompt.zh` + `video_prompt` | 每个镜头只输出一条提示词；拼接后补「画面稳定，主体一致，无镜头切换」；运镜代码转中文；合并重复逗号 |
| `negative_prompt` | `negative_prompt` | 为空时使用默认负向词 |
| `duration` | `duration` | 原样保留，`> 5s` 标记 `needs_split=true` |
| `frame_count` | `duration` × `fps` | 按 4n+1 帧计算，默认 16fps |
| `resolution` | `meta.aspect_ratio` | 16:9→1280×720，9:16→720×1280，4:3→1024×768，2.35:1→1280×544 |
| `dialogue` / `subtitle` | 镜头台词 / 字幕 | 不进入提示词，单独列出供后期配音压字 |

### 13.2 输出约束

- 一个镜头对应一次生成任务，不做镜头合并。
- 台词、字幕不写入提示词（生成模型无法稳定输出文字）。
- `needs_split=true` 的镜头必须在生成栏目内拆段或缩短后剪辑补足。
- 从第 2 镜起建议用「图生视频」并以上一镜尾帧为首帧，维持人物一致性。
