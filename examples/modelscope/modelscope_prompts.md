# 魔搭 AIGC 生成视频 · 逐镜提示词｜《末班地铁里》

- 类型 / 风格：悬疑 / 冷峻霓虹、雨夜、低饱和
- 画幅 / 分辨率：16:9 / 1280×720
- 帧率：16 fps（万相按 4n+1 帧生成）
- 镜头数：20　｜　理论总时长：90s

## 使用方法

1. 打开魔搭社区 AIGC 专区 → 生成视频 → 选择通义万相（文生视频）模型。
2. 复制某一镜的「正向提示词」到提示词框，反向提示词填入负向提示词。
3. 画幅、分辨率、时长按该镜「推荐参数」设置；时长超过 5s 的镜头请按提示拆分或分段生成。
4. 需要人物一致时，第 2 镜起可切换到「图生视频」，以上一镜尾帧作为首帧参考。
5. 台词与字幕不进入提示词（模型不生成文字），后期按「台词 / 字幕」轨单独配音与压字。

## 镜头速查表

| # | 镜头 | 时长 | 帧数 | 分辨率 | 需拆分 |
| --- | --- | --- | --- | --- | --- |
| 1 | shot-1-1-1 | 4.5s | 73 | 1280×720 | 否 |
| 2 | shot-1-1-2 | 4.5s | 73 | 1280×720 | 否 |
| 3 | shot-1-1-3 | 4.5s | 73 | 1280×720 | 否 |
| 4 | shot-1-1-4 | 4.5s | 73 | 1280×720 | 否 |
| 5 | shot-1-2-1 | 4.5s | 73 | 1280×720 | 否 |
| 6 | shot-1-2-2 | 4.5s | 73 | 1280×720 | 否 |
| 7 | shot-1-2-3 | 4.5s | 73 | 1280×720 | 否 |
| 8 | shot-1-2-4 | 4.5s | 73 | 1280×720 | 否 |
| 9 | shot-2-1-1 | 4.5s | 73 | 1280×720 | 否 |
| 10 | shot-2-1-2 | 4.5s | 73 | 1280×720 | 否 |
| 11 | shot-2-1-3 | 4.5s | 73 | 1280×720 | 否 |
| 12 | shot-2-1-4 | 4.5s | 73 | 1280×720 | 否 |
| 13 | shot-2-2-1 | 4.5s | 73 | 1280×720 | 否 |
| 14 | shot-2-2-2 | 4.5s | 73 | 1280×720 | 否 |
| 15 | shot-2-2-3 | 4.5s | 73 | 1280×720 | 否 |
| 16 | shot-2-2-4 | 4.5s | 73 | 1280×720 | 否 |
| 17 | shot-3-1-1 | 4.5s | 73 | 1280×720 | 否 |
| 18 | shot-3-1-2 | 4.5s | 73 | 1280×720 | 否 |
| 19 | shot-3-1-3 | 4.5s | 73 | 1280×720 | 否 |
| 20 | shot-3-1-4 | 4.5s | 73 | 1280×720 | 否 |

## 逐镜提示词

### 1. shot-1-1-1　4.5s · 1280×720 · 缓推

**正向提示词（中文，直接粘贴）**

```text
远景，阿岚，位于老公寓楼道，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（缓推），老公寓楼道里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
wide shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频
**台词**：老周：你早就知道，只是不想承认。
**字幕**：你早就知道，只是不想承认。

### 2. shot-1-1-2　4.5s · 1280×720 · 固定

**正向提示词（中文，直接粘贴）**

```text
中景，老周，位于老公寓楼道，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，固定机位，老周开口说话，表情克制，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 3. shot-1-1-3　4.5s · 1280×720 · 跟拍

**正向提示词（中文，直接粘贴）**

```text
中近景，阿岚，位于老公寓楼道，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（跟拍），他伸手去关灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 4. shot-1-1-4　4.5s · 1280×720 · 拉远

**正向提示词（中文，直接粘贴）**

```text
特写，阿岚，位于老公寓楼道，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（拉远），老公寓楼道里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 5. shot-1-2-1　4.5s · 1280×720 · 缓推

**正向提示词（中文，直接粘贴）**

```text
远景，阿岚，位于深夜便利店，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（缓推），深夜便利店里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
wide shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）
**台词**：老周：你早就知道，只是不想承认。
**字幕**：你早就知道，只是不想承认。

### 6. shot-1-2-2　4.5s · 1280×720 · 固定

**正向提示词（中文，直接粘贴）**

```text
中景，老周，位于深夜便利店，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，固定机位，老周开口说话，表情克制，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 7. shot-1-2-3　4.5s · 1280×720 · 跟拍

**正向提示词（中文，直接粘贴）**

```text
中近景，阿岚，位于深夜便利店，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（跟拍），他伸手去关灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 8. shot-1-2-4　4.5s · 1280×720 · 拉远

**正向提示词（中文，直接粘贴）**

```text
特写，阿岚，位于深夜便利店，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（拉远），深夜便利店里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 9. shot-2-1-1　4.5s · 1280×720 · 缓推

**正向提示词（中文，直接粘贴）**

```text
远景，阿岚，位于地下停车场，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（缓推），地下停车场里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
wide shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）
**台词**：老周：你早就知道，只是不想承认。
**字幕**：你早就知道，只是不想承认。

### 10. shot-2-1-2　4.5s · 1280×720 · 固定

**正向提示词（中文，直接粘贴）**

```text
中景，老周，位于地下停车场，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，固定机位，老周开口说话，表情克制，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 11. shot-2-1-3　4.5s · 1280×720 · 跟拍

**正向提示词（中文，直接粘贴）**

```text
中近景，阿岚，位于地下停车场，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（跟拍），他伸手去关灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 12. shot-2-1-4　4.5s · 1280×720 · 拉远

**正向提示词（中文，直接粘贴）**

```text
特写，阿岚，位于地下停车场，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（拉远），地下停车场里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 13. shot-2-2-1　4.5s · 1280×720 · 缓推

**正向提示词（中文，直接粘贴）**

```text
远景，阿岚，位于老公寓楼道，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（缓推），老公寓楼道里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
wide shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）
**台词**：老周：你早就知道，只是不想承认。
**字幕**：你早就知道，只是不想承认。

### 14. shot-2-2-2　4.5s · 1280×720 · 固定

**正向提示词（中文，直接粘贴）**

```text
中景，老周，位于老公寓楼道，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，固定机位，老周开口说话，表情克制，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 15. shot-2-2-3　4.5s · 1280×720 · 跟拍

**正向提示词（中文，直接粘贴）**

```text
中近景，阿岚，位于老公寓楼道，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（跟拍），他伸手去关灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 16. shot-2-2-4　4.5s · 1280×720 · 拉远

**正向提示词（中文，直接粘贴）**

```text
特写，阿岚，位于老公寓楼道，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（拉远），老公寓楼道里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 17. shot-3-1-1　4.5s · 1280×720 · 缓推

**正向提示词（中文，直接粘贴）**

```text
远景，阿岚，位于深夜便利店，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（缓推），深夜便利店里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
wide shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）
**台词**：老周：你早就知道，只是不想承认。
**字幕**：你早就知道，只是不想承认。

### 18. shot-3-1-2　4.5s · 1280×720 · 固定

**正向提示词（中文，直接粘贴）**

```text
中景，老周，位于深夜便利店，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，固定机位，老周开口说话，表情克制，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 19. shot-3-1-3　4.5s · 1280×720 · 跟拍

**正向提示词（中文，直接粘贴）**

```text
中近景，阿岚，位于深夜便利店，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（跟拍），他伸手去关灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
medium close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

### 20. shot-3-1-4　4.5s · 1280×720 · 拉远

**正向提示词（中文，直接粘贴）**

```text
特写，阿岚，位于深夜便利店，单一顶光与长阴影，冷峻霓虹、雨夜、低饱和，电影感构图，16:9，缓慢运镜（拉远），深夜便利店里只剩一盏灯，画面稳定，主体一致，无镜头切换
```

**正向提示词（English）**

```text
close-up shot, a single subject in a dim interior, mystery thriller style, moody lighting, muted palette, film grain, 16:9 aspect ratio, highly detailed. Smooth motion, consistent subject, no camera cuts, no text overlay.
```

**反向提示词**

```text
畸形手、多余肢体、文字水印、低清晰度、面部变形、塑料质感
```

**推荐参数**：时长 4.5s（约 73 帧 @16fps）　｜　画幅 16:9　｜　分辨率 1280×720　｜　通义万相 · 文生视频 / 图生视频（可用上一镜尾帧）

## 一致性参数建议

- 固定负向提示词：畸形手、多余肢体、面部变形、文字水印、低清晰度、画面抖动、塑料质感
- 同一人物跨镜时，保持 `appearance` 描述逐字一致，或使用上一镜尾帧做图生视频。
- 同一场景内镜头尽量固定 seed（若栏目提供），便于失败镜头单独重跑。
