# 画风圣经 · 提示词清单 v0.1

- 画风：**A1 电影感写实 + D4 东方仙侠**
- 画幅：**R1 16:9 / 1920×1080**
- 用途：锁定画风参考图，具体内容随机取样，只验证"风格是否经得住不同题材"
- 出图后把图片按每条的建议文件名放进 `images/` 目录

## 统一风格后缀（每条提示词末尾必须保留）

```text
cinematic photorealistic film still, 35mm anamorphic, natural volumetric light,
muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture,
subtle film grain
```

## 统一负面提示词

```text
cartoon, anime, illustration, 3d render, CGI plastic skin, waxy, oversaturated,
neon colors, modern clothing, brand logo, text, watermark, extra limbs,
deformed hands, extra fingers, lowres, blurry, oversharpened, hdr
```

## 四条硬规则

| 规则 | 内容 |
|---|---|
| A 风格锚定 | 后缀一字不改；禁止 anime / 3d render / illustration / cartoon |
| B 光线四档 | L1 晨雾玉青 5500K / L2 正午琥珀 4300K / L3 黄昏金红 3200K / L4 夜蓝烛火 2800K |
| C 取景镜头 | 16:9，主体留 5% 安全区；只用 28 / 50 / 85mm；空气层必须有雾尘雨雪之一 |
| D 负面清单 | 见上方统一负面词，不允许逐条删改 |

---

## STYLE-00 · 全局画风锚

> A1 电影写实 × D4 东方仙侠 · 所有条目共用

- **基准**：实拍电影质感，东方仙侠美学，非 CG 渲染感
- **镜头**：35mm 变形宽银幕 T2.0，浅景深，轻镜头光晕
- **光线**：自然体积光 + 丁达尔，空气中有雾与尘
- **调色**：玉青压暗部，旧金提亮部，暗部偏墨绿
- **质感**：真实毛孔、织物纹理，轻微颗粒，不做磨皮

**IMAGE PROMPT**

```text
cinematic photorealistic film still, Chinese xianxia fantasy, 35mm anamorphic lens wide open, shallow depth of field, natural volumetric light with god rays through mist, fine floating dust particles, muted jade-teal and aged-gold color palette, deep ink-green shadows, warm highlight rolloff, ultra-detailed realistic skin texture with visible pores, authentic layered silk and linen fabric weave, subtle Kodak Vision3 film grain, 16:9 composition
```

建议文件名：`STYLE-00_lookdev.jpg`

---

## SCENE-01 · 云海仙山 · 晨

> L1 晨雾玉青 · 28mm 大远景

- **地点**：孤峰之上的古山门，千级石阶嵌入崖壁
- **时间**：日出前 20 分钟，云海翻涌
- **光源**：低角度逆光，光束穿云雾形成丁达尔
- **必须出现**：云海、古松、石阶、远山层叠
- **禁止出现**：现代建筑、电线、航拍器

**IMAGE PROMPT**

```text
epic wide establishing shot, a towering immortal mountain peak rising above a thick sea of clouds at dawn, an ancient stone stairway carved into the cliff face, gnarled pines clinging to the rock, distant peaks layered in blue atmospheric haze, low backlight breaking through the mist with strong god rays, cool jade-teal shadows and pale gold rim light on the cloud tops, tiny human silhouette on the stairs for scale, deep focus, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`SCENE-01_cloud-mountain.jpg`

---

## SCENE-02 · 竹林飞瀑 · 正午

> L2 正午琥珀 · 50mm 中景

- **地点**：密竹林深处，一线飞瀑落入墨玉深潭
- **时间**：正午，阳光穿透竹叶
- **光源**：硬光短影，强烈明暗切割
- **必须出现**：竹叶光斑、水雾、湿苔、水面反光

**IMAGE PROMPT**

```text
medium-wide shot inside a dense bamboo forest at high noon, a thin waterfall dropping into a dark jade pool, hard shafts of sunlight cutting through bamboo leaves, floating pollen and water spray suspended in the air, wet moss-covered rocks, deep green shadows with crisp sunlit highlights, backlit water mist glowing, 50mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`SCENE-02_bamboo-falls.jpg`

---

## SCENE-03 · 大漠烽燧 · 黄昏

> L3 黄昏金红 · 28mm 大远景

- **地点**：无人沙海，孤立夯土烽燧只剩半壁
- **时间**：日落前 15 分钟，风沙起
- **光源**：极低角度侧逆光，影子拉长十倍
- **必须出现**：沙脊线、飘扬风沙、破旗、驼队剪影

**IMAGE PROMPT**

```text
wide shot of an ancient ruined beacon tower standing alone on a vast desert dune field at golden hour, wind-blown dust streaming across the sand ridges, extremely long dramatic shadows, warm amber and burnt-orange sunlight against deep teal shadows, a distant caravan silhouette on the horizon, torn fabric flag snapping in the wind, 28mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`SCENE-03_desert-beacon.jpg`

---

## SCENE-04 · 雨夜古镇 · 夜

> L4 夜蓝烛火 · 50mm 中景浅景深

- **地点**：窄巷老街，木构店铺与褪色酒旗
- **时间**：深夜，持续中雨
- **光源**：纸灯笼暖光点状分布，环境蓝
- **必须出现**：湿石反光、雨丝、灯笼光晕、雾

**IMAGE PROMPT**

```text
atmospheric night shot of a narrow ancient Chinese town street in heavy rain, wet stone paving reflecting warm lantern light, wooden shophouses with faded red banners, thin mist and visible rain streaks, deep blue ambient with isolated amber pools of light from paper lanterns, shallow depth of field on a foreground puddle, 50mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`SCENE-04_rainy-town.jpg`

---

## SCENE-05 · 雪岭古道 · 阴天

> L1 变体 冷白高调 · 28mm 大远景

- **地点**：雪线之上的石砌古道，两侧冰崖夹峙
- **光源**：漫射柔光，低对比，冷白偏蓝
- **必须出现**：雪粒子、冰棱、扭曲枯松、旧路碑

**IMAGE PROMPT**

```text
wide shot of a snow-covered mountain pass under flat overcast daylight, a narrow stone-paved ancient road winding between frozen cliff walls, bare twisted pines, wind-driven snow particles streaking across the frame, low-contrast soft white light with subtle blue shadow tones, desaturated cold palette, weathered stone milestone half buried in snow, 28mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`SCENE-05_snow-pass.jpg`

---

## SCENE-06 · 云顶祭坛 · 蓝调

> L4 变体 冷银月光 · 28mm 大远景

- **地点**：悬于云海之上的圆形石祭坛
- **光源**：单一月光侧照，符文微自发光
- **必须出现**：刻纹符文、翻卷云层、残破石柱

**IMAGE PROMPT**

```text
wide shot of a circular stone altar on a clifftop above a rolling sea of clouds at blue hour, ancient carved runes faintly glowing on the stone, thin fog spilling over the cliff edge, a single beam of cold moonlight raking across the altar, broken pillars surrounding it, deep indigo shadows with cold silver highlights, 28mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`SCENE-06_altar-bluehour.jpg`

---

## CHAR-01 · 少年剑客

> 男 · 20 岁 · 参照图正面 3/4

- **脸型**：窄长脸，颧骨清晰，下颌线利
- **眉眼**：直眉、单眼皮、深黑瞳
- **发型**：肩长黑发，皮绳松松低束
- **体型**：瘦而有筋，身高约 178
- **标志**：左眉上方一道旧疤；右手缠布条
- **服装**：洗旧的靛蓝棉麻练功衣，布腰带

**IMAGE PROMPT**

```text
character reference portrait, three-quarter view, upper body, a young Chinese swordsman around twenty, lean wiry build, narrow face with sharp jawline, straight dark eyebrows, deep black eyes, shoulder-length black hair tied loosely with a leather cord, a small old scar above his left eyebrow, right hand wrapped in linen strips, worn indigo-blue cotton training robes with frayed cuffs, dark cloth belt, sword hilt visible at his hip, guarded determined expression, plain deep charcoal background, soft even key light with subtle rim separation, 85mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`CHAR-01_young-swordsman.jpg`

---

## CHAR-02 · 白衣女修

> 女 · 24 岁 · 参照图正面 3/4

- **脸型**：鹅蛋脸，颧骨柔和，下巴略尖
- **眉眼**：长凤眼、浅灰褐瞳、细长眉
- **发型**：黑长直，白玉簪半挽，余发垂至腰
- **体型**：纤长，身高约 168
- **标志**：颈侧一枚浅色小痣；腰佩素玉
- **服装**：象牙白层叠丝袍，领口银线云纹

**IMAGE PROMPT**

```text
character reference portrait, three-quarter view, upper body, an elegant Chinese female cultivator in her mid twenties, oval face with soft cheekbones, long phoenix eyes with pale grey-brown irises, fine arched eyebrows, long straight black hair half pinned with a white jade hairpin, slender tall build, layered ivory silk robes with silver thread cloud embroidery at the collar, a plain jade pendant at her waist, a small pale mole on her neck, serene cold expression, plain deep charcoal background, soft even key light with subtle rim light, 85mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`CHAR-02_white-cultivator.jpg`

---

## CHAR-03 · 白发宗主

> 男 · 70 岁 · 参照图正面 3/4

- **脸型**：方脸，法令纹与眉间纹很深
- **眉眼**：浓白眉、眼窝深、目光锐
- **发型**：银白发束顶髻，长须及胸
- **体型**：瘦高，肩背微驼，身高约 175
- **标志**：左手拇指一枚旧铜扳指
- **服装**：灰绿层叠旧袍，深铜色包边

**IMAGE PROMPT**

```text
character reference portrait, three-quarter view, upper body, an old Chinese sect master around seventy, weathered square face with deep nasolabial folds and furrowed brow, heavy white eyebrows, sunken sharp eyes, silver-white hair in a topknot with a long white beard reaching his chest, tall thin slightly stooped build, faded grey-green layered robes with dark bronze trim, a worn bronze thumb ring on his left hand, wooden staff just visible, dignified calm expression, plain deep charcoal background, soft even key light with subtle rim light, 85mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`CHAR-03_old-master.jpg`

---

## CHAR-04 · 红衣魔修

> 女 · 31 岁 · 参照图正面 3/4

- **脸型**：瘦削锐利，颧骨高，下颌窄
- **眉眼**：上挑眼、黑瞳带一圈暗红、浓烟熏妆
- **发型**：黑长发，暗红缎带缠束
- **体型**：高挑清瘦，身高约 172
- **标志**：颈前一串细银链；右手银爪戒
- **服装**：黑红漆皮护甲罩暗红丝袍

**IMAGE PROMPT**

```text
character reference portrait, three-quarter view, upper body, a Chinese female demonic cultivator in her early thirties, sharp angular face with high cheekbones, upswept eyes with black irises ringed in faint crimson, heavy smoky eye makeup, dark red lips, long black hair bound with crimson silk ribbons, tall lean build, black and crimson lacquered leather armor over dark red silk robes, silver claw rings on her right hand, a thin silver chain at her throat, cold mocking half-smile, plain deep charcoal background, soft even key light with subtle rim light, 85mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`CHAR-04_crimson-cultivator.jpg`

---

## CHAR-05 · 市井孩童

> 男 · 12 岁 · 参照图正面 3/4

- **脸型**：圆脸，婴儿肥未退，鼻梁低
- **眉眼**：圆眼、睫毛长、眉毛淡
- **发型**：参差的短黑发，额前一撮翘起
- **体型**：瘦小，身高约 140
- **标志**：鼻梁上三颗浅雀斑；衣肘打补丁
- **服装**：过大的粗麻短衣，布绳当腰带

**IMAGE PROMPT**

```text
character reference portrait, three-quarter view, upper body, a Chinese street child around twelve, round face with baby fat, low nose bridge and three faint freckles across it, big round eyes with long lashes, light eyebrows, short unevenly cut black hair with a tuft sticking up in front, small thin build, oversized coarse hemp tunic with patched elbows, rope belt, a small cloth bundle strapped to his back, wary curious expression, plain deep charcoal background, soft even key light with subtle rim light, 85mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`CHAR-05_street-child.jpg`

---

## CHAR-06 · 面具术士

> 未知 · 参照图正面 3/4

- **面具**：龟裂的白漆傩面，残存碎金箔
- **身形**：高瘦，肩线极直，颈部细
- **手部**：手指异常修长，指甲偏青
- **服装**：黑麻连帽长袍，褪色赭黄符带
- **配饰**：腰间一串青铜钱，走动有声

**IMAGE PROMPT**

```text
character reference portrait, three-quarter view, upper body, a mysterious Chinese masked diviner, tall and thin with unnaturally straight shoulders, face hidden behind a cracked white lacquer exorcist mask with remnants of gold leaf, hooded black linen robe hung with faded ochre talisman strips, a string of bronze coins at the waist, long thin fingers with faintly blue-tinted nails, complete stillness, unsettling presence, plain deep charcoal background, soft even key light with subtle rim light, 85mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`CHAR-06_masked-diviner.jpg`

---

## PROP-01 · 古剑 · 静置

> 85mm 微距 · 硬侧光

- **形制**：八面汉剑式直刃，剑身略有弧度
- **纹理**：折叠锻打纹，刃口有细密崩口
- **剑鞘**：暗铜包边，云纹阴刻，已氧化发乌
- **配件**：褪色墨绿丝穗，缠绳磨损起毛

**IMAGE PROMPT**

```text
close-up product still of an ancient Chinese straight sword lying on dark stone, slightly curved blade with visible layered forging pattern, fine chips along the edge, tarnished bronze scabbard with engraved cloud motifs, worn dark green silk tassel, a single hard side light raking across the metal surface to reveal scratches, volumetric dust in the beam, plain deep charcoal background, 85mm macro lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`PROP-01_ancient-sword.jpg`

---

## PROP-02 · 罗盘与符纸

> 50mm 俯拍 · 烛光低位

- **主体**：青铜风水罗盘，多层同心刻度环
- **陪体**：散落赭黄符纸，朱砂符文，边缘焦黑
- **环境**：旧木桌面，划痕与烛泪
- **光位**：右下方烛光，强烈明暗对比

**IMAGE PROMPT**

```text
overhead close-up of an antique bronze feng shui compass on a weathered wooden table, multiple engraved concentric rings with celestial characters, scattered ochre talisman papers marked with cinnabar symbols, burnt edges, dried candle wax and scratches on the wood, a single candle at the frame edge giving warm low-angle light against deep shadow, dust motes floating, 50mm lens, cinematic photorealistic film still, 35mm anamorphic, natural volumetric light, muted jade-teal and aged-gold palette, ultra-detailed skin and fabric texture, subtle film grain
```

建议文件名：`PROP-02_compass-talismans.jpg`
