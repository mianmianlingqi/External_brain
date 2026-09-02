# Research: new-bmp/MCUS

调研对象：[https://github.com/new-bmp/MCUS](https://github.com/new-bmp/MCUS)  
调研日期：2026-09-02  
一手来源：GitHub API、仓库 `main`（`6d928f97`，tag `v1.0.2`）、release tag `v1.1-weeklypatch1`（`478cb20d`）、克隆后的源码与目录快照。未使用二手评测或转述。

## 结论

MCUS 是一个 **离线 MCU 选型目录**，不是固件管理工具（与 Nordic/Mynewt 的 McuManager 无关），也不是学习平台。它把厂商官方选型器、CMSIS-Pack、数据手册和工具链元数据收成一份可检索的目录，用 Android WebView 壳和 Cloudflare 静态包两套前端共用同一份 JS 快照。作者自称「离线 AI 选型助手」，源码里这是 **确定性中文槽位解析 + 目录硬约束**，没有神经网络，也没有把 prompt 送出设备。

产品本质是 **一张（规范化过的）大表，加上扫表的 UI**。运行时没有 SQLite/Room/索引服务：`app.js` 把 `window.MCU_CATALOG.devices`（13,377 行）读进内存，搜索是拼好的 `_q` 字符串 `includes`，筛选是 `Array.filter`，助手是槽位解析后再扫同一数组。Catalog README 写「可导入 SQLite/Room」，客户端没有做。不是知识图谱，不是问答库，也没有运行时厂商 API（询价关闭）。工程量在表怎么做成：三级标识、来源、不臆造、校验；不在表之上另有一层智能。

截至 2026-08-29 的最新 GitHub Release 是 `1.1~weeklypatch1`：17 家厂商、13,377 个器件变体、20,418 个已核验完整订货号。`main` 停在 `1.0.2`，根 README 仍写 `1.0.1` / 7,916 器件，文档与代码不同步。

本仓库（External Brain Seed）里没有任何 MCUS 引用。若 Owner 把 MCU 当作 Direction，MCUS 是选型工具，不是教材；它的「不臆造、保留未知、订货号不排列组合」纪律，可以对照 Brain 里 Point / Proposal 的验收规则。

## 本质：大表

是。交付给工程师的东西就是器件行。

- 落盘：`device-variants.csv` / `device-capabilities.csv` / `device-scores.csv` 各 13,378 行（含表头），一对一打平。
- 进 App：`generate_catalog.py` 合成单文件 `catalog.js`（约 34 MB），挂到 `window.MCU_CATALOG.devices`。
- 查询：`filtered()` 对数组做子串 + 列过滤；`aiRecommend()` 先解析槽位，再 `devices.filter` / 打分。`localStorage` 只存对比 ID 和助手对话，不存目录。
- 目录页的「厂商 → 系列 → 产品线」是同一数组的 `group()`，不是另一份图数据。

表的 schema 比 Excel 选型表讲究（产品线 / 变体 / 订货号分开，ADC 三义，待核验 vs 已确认）。那是 **怎么填这张表**，不是第二种产品。Catalog README 提到的 SQLite/Room 仍是「适合导入」的设想，Android 源码只有 WebView + 内存数组。

## 身份

| 项 | 值 | 来源 |
|---|---|---|
| 仓库 | `new-bmp/MCUS`，公开，Apache-2.0 | GitHub API `repos/new-bmp/MCUS` |
| 描述 | 「安卓平台的 MCU 选型工具，包含 13000+ 款 MCU 数据，并具备横向对比与离线选型助手功能」 | 同上 `description` |
| Topics | `android`, `esp32`, `mcu`, `mcu-apps`, `mcu51` | 同上 `topics` |
| 创建 | 2026-08-13 | 同上 `created_at` |
| 最新 push（`main`） | 2026-08-25 | 同上 `pushed_at` |
| 最新 Release | 2026-08-29 `v1.1-weeklypatch1` | GitHub Releases API |
| Stars / forks | 39 / 1 | GitHub API（调研当日） |
| 语言占比 | Python 543966、JavaScript 27514、PowerShell 7269、HTML 6038、Java 4141、CSS 454 | `repos/new-bmp/MCUS/languages` |
| 包名 | `com.newbmp.mcus` | `mcu-l-android/AndroidManifest.xml` |
| 作者 | GitHub `new-bmp`，显示名 `new.bmp`，北京 / BUCEA，邮箱 `new.bmp@outlook.com` | `users/new-bmp`；tag 提交作者 |

作者另外三个公开仓库：`AliceSim`（STM32F103 教学/仿真）、`A4091-armbian-toolkit`、`Alicepose-21points`。MCUS 的 merge 报告路径是 `C:\Users\confl\Desktop\alice blue\mcu-l-catalog\...`，和 AliceSim 同一工作区命名。MCUS 与 AliceSim 相邻，但仓库之间没有代码依赖。

没有 Play Store 条目、没有 homepage、没有 GitHub Pages。可安装物是 GitHub Release 上的 debug APK 和静态 zip。

## 版本与发布状态

Git 上有两套「当前」：

1. **默认分支 `main`** = `6d928f97` = tag `v1.0.2`（2026-08-25）。Android README、`catalog.js` meta、`CURRENT_SNAPSHOT.md`、校验报告都是这一档。
2. **Release `v1.1-weeklypatch1`** = `478cb20d`（2026-08-29）。这是 **无父提交的孤立快照**（`git rev-list --parents` 只有自身；与 `main` 无 merge-base）。根 README 在这个 tag 上才改成 `1.1~weeklypatch1` / 13,377 器件。器件规模与 `main` 相同，增量主要是文档、封装示意图、助手模型 v0.7.0、询价开关文案。

`main` 根 README 仍写 Android `1.0.1`、7,916 器件、4,811 订货号，落后于同分支的 Android README 和 `CURRENT_SNAPSHOT.md`。`release/` 目录在 `main` 上只放到 `MCUS-1.0.1-debug.apk`；1.0.2 APK 在 `mcu-l-android/dist/`，1.1 APK 只在 Release 附件里。

| Tag | 日期 | 器件变体 | 订货号 | 要点 |
|---|---|---:|---:|---|
| v0.8.1 | 2026-08-13 | 7,603 | 4,534 | 沁恒外设；首次静态 Web |
| v0.8.2 | 2026-08-14 | 7,677 | 4,572 | 先楫 HPM |
| v1.0.0 | 2026-08-23 | 7,694 | 4,589 | 正式版 |
| v1.0.1 | 2026-08-24 | （雅特力 AT32） | | 助手输入框随键盘；AT32 |
| v1.0.2 | 2026-08-25 | 13,377 | 20,418 | 瑞萨六大家族；询价关闭 |
| v1.1-weeklypatch1 | 2026-08-29 | 13,377 | 20,418（README 写 20,585） | 封装图、手册链接；助手 v0.7.0 |

1.1 根 README 写「20,585 个官方订货号」，同 tag 的 Android README 和校验报告仍是 20,418。应以 `validation-report.json` 为准。

贡献者只有 `new-bmp`（14 commits on `main`）。从 0.6.0 到 1.0.2 是约两周的单人迭代。

## 用户能做什么

六个底栏页，定义在 `mcu-l-android/assets/index.html` 与 `app.js`：

- **目录**：厂商 → 系列大类 → 产品线 → 器件变体 → 完整订货号。
- **搜索**：型号 / 系列 / 产品线 / 订货号 / 外设名；厂商、核心、外设种类与最少数量筛选。
- **助手**：中文口语描述约束，返回「满足 / 近似」候选。见下文「选型助手」。
- **对比**：最多 4 款；数值领先且有差异的格子标绿。
- **数据**：快照日期、覆盖率、厂商表、可信度规则。
- **作者**：指向本 GitHub 仓库。

器件详情展示核心、存储、FPU、TIM、ADC 单元/通道/原始参数分栏、GPIO、串行、CAN、USB 角色、Ethernet、来源外设清单、已确认加速器 vs 待核验候选、选型指数拆解、官方订货号。ADC 引脚数故意不用作选型指标（`generate_catalog.py` 跳过 `adcexternalpins`；`feature-taxonomy.csv` 与 README 同步写明）。

`v1.1` 增加：按封装名/引脚数画 QFP/QFN/BGA 等示意（不是精确焊盘图）；HTTPS 手册可外开。

## 架构

三个并列目录，没有后端业务库：

```
mcu-l-catalog/   Python 采集、合并、校验、打分 → CSV/JSON 快照
mcu-l-android/   同一份 Web UI + 一层 Java WebView
mcu-l-web/       把 Android assets 切成静态分片 + Cloudflare Worker
```

### Android

`MainActivity.java` 是单 Activity WebView：加载 `file:///android_asset/index.html`，JS 开启，非 `file://` 链接丢给系统浏览器。`usesCleartextTraffic=false`。minSdk 24、targetSdk 35、versionName `1.0.2`（`build.ps1`）。构建不走 Gradle：本机 JDK 17 + Android SDK 35 + aapt2/d8/zipalign/apksigner，PowerShell `build.ps1`。产物是 debug 签名 APK。

`catalog.js` 在 `main` 上约 34 MB 明文 JS；gzip 约 778 KB。APK：`dist/MCUS-1.0.2-debug.apk` 915 KB；Release `MCUS-1.1-debug.apk` 1,083,437 字节。目录随包装进 APK，离线可用。

### Web

`build_staticfiles.py` 把 `catalog.js` 拆成 `catalog-base.js` + `catalog-part-001.js` …（默认每片 300 器件），避免单文件上传失败。`wrangler.toml`：Workers Static Assets，SPA fallback。Worker `src/index.js` 提供 `/health` 和关闭中的 `/api/quotes`。没有已部署的公开 URL。

Android 与 Web 共用 `app.js` / `assistant-model.js` / 同一快照。对比状态、助手历史存在 `localStorage`。

## 数据模型

目录刻意拆开三个标识（`mcu-l-catalog/README.md`）：

1. **产品线** — 例如 `STM32F103`
2. **器件变体** — 例如 `STM32F103C8`（保留厂商变体码 `C8`）
3. **订货号** — 例如 `STM32F103C8T6` / `STM32F103C8T6TR`

订货号 **只在官方页面出现完整字符串时才入库**，禁止后缀笛卡尔积。`validate_catalog.py` 拒绝 `*` / `?` 通配订货号、重复主键、断裂父级、负数规格、无来源订货号。

能力表把 ADC 转成三列：`adc_unit_count`、`adc_channel_count`、`adc_source_quantity` + `adc_quantity_semantics`（converter / channels / unspecified）。缺失字段留空，不按同系列补。

厂商专有 IP 保留原名（HPMicro 的 PLA/PLB/SEI/MMC/PSEC/FFA/MTG；ST 的 Chrom-ART、CORDIC、FMAC）。未逐器件确认的进 `pending_feature_candidates_json`，界面标「待核验」，不参与已确认特性。

采集器 `OfficialFetcher`（`vendor_import_common.py`）只允许 HTTPS + 白名单 host，记录 sha256 与观察时间。User-Agent：`MCU-L-Catalog/0.4`。

### 流水线

```
各厂商 import_*/augment_*  → vendor-packs/<vendor>/
merge_catalog.py           → data/combined/
enrich_catalog.py          → device-capabilities.csv + device-scores.csv
validate_catalog.py        → validation-report.json
generate_catalog.py        → Android assets/catalog.js
build_staticfiles.py       → Web 分片
```

29 个脚本。厂商适配器覆盖：ST CubeMX、TI CMSIS、Microchip ATDF、GigaDevice、沁恒、STC32、Espressif Product Selector + IDF `soc_caps.h`、先楫选型表、全志 XRadio 数据手册、瑞萨六选型器、英飞凌 ModusToolbox `device-db`、雅特力 CMSIS、以及独立的 `MicroPy MCU` 生态条目。

`merge_catalog.py` 会跳过 `vendor-packs/ti`（若 `texas-instruments` 存在），避免 TI 双目录撞车。`ti/` 报告把 MSP432 的 `http://` PDSC 标成 `unapproved_source`；`texas-instruments/` 用 HTTPS 收了同一批包。

## 覆盖（2026-08-25 快照）

来源：`mcu-l-catalog/CURRENT_SNAPSHOT.md` 与 `data/combined/validation-report.json`（status `ok`，0 error / 0 warning）。

| 厂商 | 系列 | 产品线 | 器件变体 | 完整订货号 |
|---|---:|---:|---:|---:|
| Renesas | 33 | 147 | 5,461 | 15,607 |
| STMicroelectronics | 27 | 231 | 2,778 | 303 |
| Infineon | 79 | 164 | 1,734 | 1,487 |
| Nuvoton | 11 | 111 | 1,058 | 0 |
| Microchip | 45 | 60 | 767 | 2,318 |
| GigaDevice | 12 | 33 | 388 | 0 |
| Espressif | 16 | 99 | 319 | 319 |
| Artery | 5 | 26 | 222 | 222 |
| MindMotion | 18 | 44 | 157 | 0 |
| Geehy | 9 | 28 | 153 | 0 |
| Qinheng | 35 | 35 | 90 | 97 |
| Puya | 6 | 41 | 87 | 0 |
| HPMicro | 9 | 41 | 74 | 39 |
| Texas Instruments | 15 | 26 | 63 | 0 |
| MicroPy MCU | 2 | 6 | 9 | 9 |
| STC | 2 | 9 | 9 | 9 |
| Allwinner | 1 | 5 | 8 | 8 |
| **合计** | **325** | **1,106** | **13,377** | **20,418** |

平均评分字段覆盖率 97.38%；≥90% 覆盖 12,350 款；FPU 已核验 13,163 款。

读这张表时要注意：

- 瑞萨约占器件数 41%、订货号 76%。规模跳变（7.6k → 13.3k）主要来自瑞萨，不是全面厂覆盖。
- ST 有 2,778 变体但只有 303 订货号（快照举例：STM32F103 有 29 变体 / 133 订货号）。Nuvoton、GigaDevice、MindMotion、Geehy、Puya、TI 订货号为 0。
- 全志只收 8 个独立 XR 无线 MCU；A/T/MR/V/R SoC 和 XR 连接芯片排除。瑞萨 RZ MPU/SoC 排除。
- `MicroPy MCU` 是生态桶，不是硅厂商：RP2040/RP2350/RP2354、K210、CanMV K230/K230D；K510 无官方 MicroPython，未知字段留空。
- CMSIS-Pack 对 PIC、AVR、8051、RL78、RX、C2000 等不能单独当完整目录。README 自己写了这条边界。

下一步（作者写在 `CURRENT_SNAPSHOT.md`）：NXP / Silicon Labs / Nordic；Microchip PIC/AVR/dsPIC 官方目录；TI MSP430/C2000/TM4C/Hercules 与订货号；其余 STM32 系列订货号；把 `orderable_part_count=0` 的厂清零。

已知上游失败 9 条（`import-errors.csv`）：Geehy 7（XML 损坏或 HTTP 405）、Infineon AIROC 超时、Puya PY32F3xx 404。未计入「已覆盖」。

## 选型指数

文档 `SCORING_MODEL.md` 称 V1；代码常量是 `mcu-l-selection-index-v2`（`enrich_catalog.py`）。公式在代码里：

- 计算 35%：主频对数归一（8–800 MHz）60% + 核心代际表 40%（M0=18 … M4=60 … M85=100）。RISC-V / 8051 / 青稞不在 `core_rank` 表里，该分量缺失。
- 存储 25%：Flash 55%（16–4096 KB 对数）+ RAM 45%（4–1024 KB 对数）。
- 外设 25%：定时器、ADC 通道、DAC、串行合计、CAN、USB、Ethernet、GPIO 分段封顶后相加。
- 加速器 15%：FPU 35% + 加速器名启发式 65%（NPU=100，CORDIC/FMAC=75，图形=65，AES/crypto=50）。

缺维时对剩余维重归一，并降低 `score_coverage_percent`。界面同时显示指数和覆盖率。CoreMark / DMIPS / ULPMark 列为空，`benchmark_status=not_imported`；禁止由主频推算。

这是排序启发式，不是性能测量。同频 IPC、实时性、功耗不能从指数读出。

## 选型助手

`assistant-model.js` 开头写明：紧凑、确定性；词表理解 MCU 语言，目录字段执行电气/资源约束；「No prompt leaves the device。」

`main` 上模型版本 **0.6.0**，类型 `natural-language-slot-constraint`。`v1.1` README 写 **0.7.0**，增加「核心 A 或核心 B」。

实现是加权词表 + 正则：厂商/核心别名、中文数量词、软偏好（低功耗、国产、小封装）、场景 profile（电机、无线、显示、工业 CAN 等）、否定（「别带无线」）。`app.js` 的 `aiParse` → `aiEvaluate` → `aiHardScope`：硬约束（核心、厂商、明确外设下限）在近似推荐时也不放宽；未知核心不跨核心猜测。结果带「满足 / 近似」和理由条。

这不是 LLM。口语覆盖取决于词表。Quick prompts 写死在 UI：Cortex-M4+CAN、Wi-Fi+蓝牙、MicroPython+摄像头。

## 询价（关闭）

`quote-config.js`：`MCUS_QUOTES_ENABLED=false`。Worker `QUOTES_ENABLED=false`，`/api/quotes` 返回 404 `feature_disabled`。测试 `mcu-l-web/test/quotes.test.js` 锁住这一行为。

保留的实现是淘宝开放平台 `taobao.tbk.dg.material.optional`（联盟物料），不是云汉。过滤：标题精确包含完整订货号、排除开发板/模块/套件/烧录器/二手、每店一条、按价格取 3 条。`v1.1` Android README 提到「云汉芯城试接代码由服务端开关控制」，`main` 的 Worker 源码里没有云汉调用。合规与数据源未完成，作者选择整段关闭。

Android debug 构建即使传入 Worker 地址也不启用询价（`build.ps1` 把 `MCUS_QUOTES_ENABLED` 写成 false）。`v1.1` 才允许 `-EnableQuotes`。

## Issues

两个未关：

- [#1](https://github.com/new-bmp/MCUS/issues/1)（2026-08-13）「可以搞个小程序或者 web 版的吗？」作者回复「正在做」。Web 静态包已随 0.8.1 发布，issue 未关。
- [#2](https://github.com/new-bmp/MCUS/issues/2)（2026-08-24）助手页键盘遮挡输入框。作者在 1.0.1 称已修（`windowSoftInputMode=adjustResize` + `installKeyboardViewport`），issue 仍 OPEN。

无 Discussions、无 CI、无测试目录（除 Web 询价单测）。构建脚本绑定 Windows 路径与本机 `.tools\android-build`。

## 质量立场（作者自己写的）

反复出现的规则，源码与文档一致：

- 能力优先官方选型器 / CMSIS-Pack / 官方设备库 / 工具链元数据。
- 缺失 = 未知，不按兄弟型号填。
- 订货号不组合生成。
- ADC 单元 ≠ 通道 ≠ 引脚。
- 加速器保留原厂名；待核验与已确认分开。
- 选型指数 ≠ benchmark。
- 覆盖声明只覆盖「本次成功索引的来源」，不是全历史目录。

这套纪律是仓库最强的工程信号。弱项是发布卫生：根 README 过期、1.1 tag 不在 `main`、订货号计数 20,418 vs 20,585、Issues 不关、debug APK、无自动化校验入 CI。

## 和本 Seed 的关系

`CONTEXT.md` 的工作是 Owner 在若干 Direction 下学习（Point、Question、Task、Drill、Graph、Plan、View）。MCUS 做的是器件检索与比较。

可借鉴的只有方法，不是产品：

- 三个标识分开 ≈ 一个事实一个家（产品线 / 变体 / 订货号互不顶替）。
- Proposal 未接受不入库 ≈ 待核验加速器不进已确认字段。
- 未知显式保留 ≈ 空 Point 不是 Clear。
- 覆盖率与指数分开显示 ≈ Review 用计数而不是散文。

不要把 MCUS 当 MCU Direction 的内容源直接灌进 Brain：它是快照目录，没有「先学什么」的 Link，也没有 Question。AliceSim 更接近教学，但仍是另一套产品。

Agent 接入走附属 Skill `mcus`（`.agents/skills/mcus/`），不是向量检索，也不经 Brain 接口。命令是 lookup / select / compare / coverage，硬约束遇空字段即失败。见 ADR-0016。

## 不建议先做向量检索

选型查询是约束，不是近义文档。助手示例是「120MHz 以上、2 个 UART、CAN、64KB RAM 的 Cortex-M4」和「别带无线」。这类条件要的是阈值、有无、否定；向量近邻会把「差不多」的芯片拉回来，正好踩他们已经写死的硬约束（`aiHardScope`：硬范围在近似推荐时也不放宽）。

13,377 行已经全表扫描，没有召回规模问题。行本身是数字和枚举，再 embed 一遍只是把已有列涂糊。他们也没有把数据手册正文收进目录，向量检索真正吃得开的语料不在库里。

更值得做的仍是填表和结构化邻居：缺的厂和订货号、显式国产替代/兼容映射、「像这颗」用列距离而不是余弦。若以后 ingest 手册，也是 **先过滤行，再对剩余文档做向量**，不能用向量替换选型。

未向 MCUS 仓库提 issue 或评论。

## 来源

- 仓库元数据、语言、license、topics：`GET https://api.github.com/repos/new-bmp/MCUS`
- 作者：`GET https://api.github.com/users/new-bmp`
- Releases / tags：GitHub Releases API；附件 `MCUS-1.1-debug.apk`、`MCUS-staticfiles.zip`
- Issues #1、#2 及作者评论
- `README.md`（`main` 与 `v1.1-weeklypatch1` 对照）
- `mcu-l-catalog/README.md`、`CURRENT_SNAPSHOT.md`、`SCORING_MODEL.md`、`feature-taxonomy.csv`
- `data/combined/validation-report.json`、`merge-report.json`、`coverage-manifest.csv`、`import-errors.csv`、`device-scores.csv`、`device-variants.csv`
- `mcu-l-catalog/scripts/{enrich_catalog,validate_catalog,merge_catalog,vendor_import_common,import_ti_official}.py`
- `mcu-l-android/{AndroidManifest.xml,build.ps1,src/.../MainActivity.java,assets/{index.html,app.js,assistant-model.js,quote-config.js},scripts/generate_catalog.py}`
- `mcu-l-web/{README.md,wrangler.toml,src/index.js,scripts/build_staticfiles.py,test/quotes.test.js}`
- 作者相关仓库：`new-bmp/AliceSim` API
