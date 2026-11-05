"""提示词库：分阶段生成 + 提问链。

这里既是运行时代码，也是文档的单一事实来源（docs 中的提示词与代码保持一致）。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptPair:
    name: str
    stage: str
    system: str
    user_template: str


# ---------------------------------------------------------------- 通用约束

OUTPUT_RULES = """输出要求：
1. 只输出一个合法 JSON 对象，不要 Markdown 代码块、不要解释、不要前后缀。
2. 所有键名必须使用英文 snake_case，严格符合下方 Schema。
3. 所有中文内容使用简体中文；英文提示词使用自然、可被扩散模型理解的英文。
4. 不确定的信息给出合理默认值，不要留空、不要写 "待定"。"""


SYSTEM_WRITER = """你是一名资深短视频编剧，同时懂 AI 视频生成的技术边界。
你擅长把一句主题扩展成结构清晰、可直接拍摄的短片。
你的写作准则是：画面优先、动作优先、台词克制、每个镜头只表达一件事。
你会严格遵守时长预算：镜头以秒为单位，总时长误差控制在目标值 ±10% 以内。
""" + OUTPUT_RULES


SYSTEM_DIRECTOR = """你是一名分镜导演兼 AI 视频提示词工程师。
你熟悉镜头语言（景别、运镜、转场）与生成式模型的能力边界（单镜头 ≤10 秒、动作要简单、避免复杂多人交互）。
你写出的提示词必须包含：主体、动作、环境、光线、镜头、风格、画幅；不要写无法被摄像机执行的心理描写。
""" + OUTPUT_RULES


# ---------------------------------------------------------------- 第一阶段：立意与人物

PREMISE_USER = """【创作任务】把下面的创作设定扩展成一份短片创作大纲。

创作设定：
- 主题 / 题目：{theme}
- 类型：{genre}
- 视觉风格：{style}
- 基调：{tone}
- 目标时长：{target_duration} 秒
- 画幅：{aspect_ratio}
- 受众：{audience}
- 语言：{language}

要求：
1. title：不超过 12 个字，有画面感，不要直白点题。
2. logline：一句话（25~60 字），包含主角、目标、阻碍、代价。
3. 3 幕结构，每幕 1~3 个场景；幕 summary 说明本幕的功能（建置 / 对抗 / 转折）。
4. characters：2~4 人；每人有角色功能、外观（可直接用于绘图）、声音、人物弧光。
5. 单场景预计时长不超过 40 秒。

只输出 JSON：
{{
  "meta": {{"title": string, "logline": string}},
  "characters": [{{
    "id": "char-1",
    "name": string,
    "role": string,
    "age": string,
    "appearance": string,
    "voice": string,
    "arc": string
  }}],
  "acts": [{{
    "id": "act-1",
    "title": "第一幕 · xxxx",
    "summary": string,
    "scenes": [{{
      "id": "scene-1-1",
      "heading": "INT./EXT. 地点 - 时间",
      "location": string,
      "time_of_day": "dawn|morning|noon|afternoon|dusk|night",
      "weather": string,
      "summary": string
    }}]
  }}]
}}"""


# ---------------------------------------------------------------- 第二阶段：场景与节拍

SCENES_USER = """【创作任务】为第 {act_index} 幕细化场景与剧情节拍。

全片信息：
- 题目：{title}
- 一句话故事：{logline}
- 类型 / 风格 / 基调：{genre} / {style} / {tone}
- 目标总时长：{target_duration} 秒
- 本幕标题与功能：{act_title} — {act_summary}

人物：
{characters}

已有场景：
{existing_scenes}

本幕时间预算：约 {act_budget} 秒。

要求：
1. 保持场次标题格式 "INT./EXT. 地点 - 时间"。
2. 每个场景给出 2~4 个剧情节拍（beats），动作与台词交替，不要大段独白。
3. 每个场景 2~4 个镜头量的信息密度，但本阶段不要输出 shots。
4. 台词单句不超过 20 字，便于字幕与配音。
5. 场景之间要有因果推进，不要重复信息。

只输出 JSON：
{{
  "scenes": [{{
    "id": "scene-{act_index}-N",
    "heading": string,
    "location": string,
    "time_of_day": string,
    "weather": string,
    "summary": string,
    "beats": [{{
      "type": "action|dialogue|transition|montage",
      "text": string,
      "character": string,
      "delivery": string
    }}]
  }}]
}}"""


# ---------------------------------------------------------------- 第三阶段：分镜与提示词

SHOTS_USER = """【创作任务】把一个场景拆成可直接生成的分镜表。

场景信息：
- 场次：{heading}
- 地点 / 时间 / 天气：{location} / {time_of_day} / {weather}
- 场景摘要：{summary}

剧情节拍：
{beats}

人物：
{characters}

全片风格：{style}；类型：{genre}；画幅：{aspect_ratio}；语言：{language}

拆分要求：
1. 输出 2~5 个镜头，总时长接近 {scene_budget} 秒，单镜头 2~8 秒。
2. 景别要有变化：至少一个建立镜头（wide/extreme_wide），至少一个情绪镜头（close/extreme_close）。
3. subject 写"画面里最显眼的东西"；action 写"这一秒发生什么"，一个镜头只做一件事。
4. 有台词的镜头，dialogue 数组写台词、说话人（用人物中文名）、delivery（语气/音量）。
5. image_prompt.zh / image_prompt.en：中文 60~120 字、英文 40~90 词，必须含主体、环境、光线、色调、景别、风格；
   英文提示词最后统一追加 "16:9 aspect ratio, cinematic"（画幅按上面给定值替换 16:9）。
6. video_prompt：只写运动与时间变化（如 "缓慢推近，雨滴在玻璃上滑落"），不重复静态外观。
7. negative_prompt：排除常见生成缺陷（畸形手、多余肢体、文字水印、低清晰度、面部变形）。
8. transition_out：镜头与下一镜的衔接方式。

只输出 JSON：
{{
  "shots": [{{
    "id": "shot-{act_index}-{scene_index}-N",
    "order": 1,
    "duration": 4,
    "shot_size": "extreme_wide|wide|full|medium|medium_close|close|extreme_close",
    "camera": "static|push_in|pull_out|pan_left|pan_right|tilt_up|tilt_down|tracking|handheld|crane_up|orbit",
    "subject": string,
    "action": string,
    "dialogue": [{{"character": string, "text": string, "delivery": string}}],
    "sfx": [string],
    "bgm": string,
    "subtitle": string,
    "image_prompt": {{"zh": string, "en": string}},
    "video_prompt": string,
    "negative_prompt": string,
    "transition_out": "cut|fade_in|fade_out|dissolve|wipe|match_cut|flash",
    "notes": string
  }}]
}}"""


# ---------------------------------------------------------------- 修复 / 单镜重写

REPAIR_USER = """你上一次的输出不是合法 JSON 或不符合 Schema。
请修复下面内容，只输出修复后的 JSON，不要解释。

错误信息：{error}

上一次输出：
{raw}
"""

REGEN_SHOT_USER = """【单镜头重写】保留叙事功能，重写这一个镜头的画面与提示词。

原镜头 JSON：
{shot_json}

要求：
1. 换一个不同的机位或景别，避免与前一镜重复。
2. 时长保持在 2~8 秒。
3. 输出的 JSON 结构与原镜头完全一致，只输出该镜头对象本身（不要包在 shots 里）。
"""


PRE_PROMPT = """你是一名资深短视频编剧，同时懂 AI 视频生成的技术边界。
你擅长把一句主题扩展成结构清晰、可直接拍摄的短片。
你的写作准则是：画面优先、动作优先、台词克制、每个镜头只表达一件事。
你会严格遵守时长预算。"""


# ---------------------------------------------------------------- 提问链（30+ 问）

QUESTION_ROUNDS: list[dict] = [
    {
        "round": "第 1 轮 · 定位（先决定「给谁看」）",
        "goal": "确定题材、受众、平台与时长，避免后面反复返工。",
        "questions": [
            "这条视频最终发在哪个平台？抖音 / 视频号 / B 站 / YouTube Shorts / 内部汇报？",
            "目标时长是 15 秒、30 秒、60 秒、3 分钟，还是 5 分钟以上？",
            "核心受众是谁？年龄、职业、他们此刻的焦虑或欲望是什么？",
            "你希望观众看完的第一个情绪是什么：爽、怕、暖、燃、困惑、被说中？",
            "这条视频是独立成片，还是系列中的一集？如果是系列，世界观已有哪些硬设定？",
            "有没有必须出现的品牌、产品、人物或口号？它们允许以什么方式出现？",
        ],
    },
    {
        "round": "第 2 轮 · 故事内核（决定「讲什么」）",
        "goal": "把模糊感觉压缩成一句可执行的故事。",
        "questions": [
            "用一句话说：谁，想要什么，被什么挡住，付出什么代价？",
            "主角最想要的东西，具体到可以拍出来吗（一个物件、一句话、一个动作）？",
            "阻碍来自外部（对手/环境）还是内部（性格/记忆）？",
            "故事的转折点发生在第几秒？观众会在哪一刻意识到事情不对？",
            "结局是得到、失去、还是「以为得到其实失去」？",
            "如果只能保留一个画面让人记住，你希望是哪个画面？",
            "这个故事有没有真实原型或亲历细节？哪个细节最不可替代？",
        ],
    },
    {
        "round": "第 3 轮 · 人物与关系（决定「谁在动」）",
        "goal": "让人物具备可拍的外观与可说的话语方式。",
        "questions": [
            "主角出场时在做什么？这个动作能暴露他的性格吗？",
            "主角的外形关键词是什么（年龄、穿着、一件标志性物品）？",
            "对手/阻碍者的动机是否成立？他自己相信什么？",
            "两人之间此前发生过什么？观众需要知道多少？",
            "谁在说谎？谎言的破绽放在哪个细节上？",
            "有没有一个「沉默的人」（旁观者/路人）承担情绪反应镜头？",
            "主角说话是什么风格：短句、书面、方言、口音、几乎不说话？",
        ],
    },
    {
        "round": "第 4 轮 · 视听（决定「怎么拍」）",
        "goal": "把文字转成可生成的分镜与提示词。",
        "questions": [
            "视觉风格参考哪部片子或哪种摄影流派（冷峻霓虹、胶片颗粒、纪录片手持、广告棚拍）？",
            "主色调是什么？有没有一个贯穿全片的强调色？",
            "光源从哪里来？自然光、霓虹、屏幕光、单一顶光？",
            "画幅与镜头质感：16:9 / 9:16 / 2.35:1，广角还是长焦？",
            "声音设计：环境底噪是什么？有没有一个反复出现的音效？",
            "配乐情绪曲线怎么走？从哪里开始铺，哪里彻底静音？",
            "全片要不要字幕？字幕风格是叙述性、对白式，还是只有关键词？",
            "有没有必须避免的视觉元素（血腥、真实品牌、特定人群特征）？",
        ],
    },
    {
        "round": "第 5 轮 · 生产约束（决定「能不能做出来」）",
        "goal": "提前排除生成失败与返工。",
        "questions": [
            "单镜头是否控制在 10 秒以内？超过的镜头怎么拆？",
            "有没有多人复杂交互、快速打斗、手部特写等生成困难镜头？",
            "人物一致性怎么保证：固定外观描述、参考图、还是同一提示词模板？",
            "需要几个场景？场景能否复用同一空间以减少生成量？",
            "是否需要口型同步？台词长度与镜头时长匹配吗？",
            "交付物只要脚本，还是同时要绘图提示词、视频提示词、配音文案、字幕文件？",
            "谁来验收？验收标准是「能看懂故事」还是「画面达到参考片水准」？",
        ],
    },
    {
        "round": "第 6 轮 · 打磨（决定「还差什么」）",
        "goal": "用苏格拉底式追问找出薄弱环节。",
        "questions": [
            "把结局遮住，前面 80% 是否仍然成立？如果不成立，说明伏笔不足。",
            "删掉任意一个场景，故事还完整吗？如果完整，这个场景就该删或该合并。",
            "每一句台词，能不能用一个动作替代？能替代的就删台词。",
            "观众在第 3 秒会看到什么？如果不够抓人，前 3 秒要重做。",
            "片中信息是「展示」还是「讲述」？把所有「讲述」标出来改写成「展示」。",
            "如果预算只够拍 5 个镜头，你保留哪 5 个？这个排序就是真正的故事骨架。",
            "现在这版最让你不安的地方是什么？那通常就是需要重写的地方。",
        ],
    },
]


def question_chain_text() -> str:
    lines = ["# 提问链：用文本 AI 生成剧情（脚本片段）", ""]
    for block in QUESTION_ROUNDS:
        lines += [f"## {block['round']}", "", f"> {block['goal']}", ""]
        for index, q in enumerate(block["questions"], start=1):
            lines.append(f"{index}. {q}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- 注册表

PROMPT_LIBRARY: list[PromptPair] = [
    PromptPair("premise", "阶段 1 · 立意与人物", SYSTEM_WRITER, PREMISE_USER),
    PromptPair("scenes", "阶段 2 · 场景与节拍", SYSTEM_WRITER, SCENES_USER),
    PromptPair("shots", "阶段 3 · 分镜与提示词", SYSTEM_DIRECTOR, SHOTS_USER),
    PromptPair("regen_shot", "单镜头重写", SYSTEM_DIRECTOR, REGEN_SHOT_USER),
    PromptPair("repair", "JSON 修复", SYSTEM_DIRECTOR, REPAIR_USER),
]


def get_prompt(name: str) -> PromptPair:
    for item in PROMPT_LIBRARY:
        if item.name == name:
            return item
    raise KeyError(f"unknown prompt: {name}")
