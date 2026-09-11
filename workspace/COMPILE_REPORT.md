# 最终 PDF 编译报告

## 1. 编译方式与结果

严格串行编译，每趟等待真实退出后再执行下一趟，逐趟核对退出码。

| 顺序 | 命令 | 退出码 | 说明 |
|------|------|--------|------|
| 1 | `xelatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex` | 0 | 首趟生成 aux/引用键 |
| 2 | `bibtex8 --wolfgang main` | 1 | 唯一输出为「样式名 gbt7714-numerical 已弃用」告警；产出 `main.bbl` 6574 字节 / 19 条 `\bibitem` |
| 3 | `xelatex ...`（同上参数） | 0 | 接入参考文献 |
| 4 | `xelatex ...`（同上参数） | 0 | 交叉引用收敛，页数稳定 |

关于第 2 趟：MiKTeX 自带的 BibTeX 0.99e 在处理 `gbt7714-numerical.bst` 时容量溢出并崩溃
（退出 139、产出 0 字节 `.bbl`），已在 `_tmp/bibtest` 隔离确认为容量限制而非文件损坏
（`plain.bst` 可正常工作）。改用同一发行版的 `bibtex8 --wolfgang` 后正常，
模板的 `\bibliographystyle{gbt7714-numerical}` 未作改动。

**最终日志指标（第 4 趟 `main.log`）**

| 指标 | 数量 |
|------|------|
| LaTeX 错误 | 0 |
| Missing character（缺字） | 0 |
| Overfull hbox | 0 |
| Underfull hbox | 0 |
| Undefined reference / citation | 0 |
| 参考文献条目 | 19（全部被引用，无孤条目） |

## 2. 本轮修复项

### 2.1 数据真实性核对（编译前完成）

对照 `PAPER_DATA_CHECKLIST.md` 的 266 条 JSON 取值逐项核验正文数字。方法为构造
4738 个候选值池（含 0–6 位舍入变体与 ×3600 / ×100 / ×1000 单位换算），剥离 LaTeX 注释与命令后
比对全部章节，得 71 个未逐字命中项，再手工判定来源。**只改论文，未改任何 JSON。**

确认为真实错误并已修正 5 处：

| 位置 | 原值 | 改为 | 依据 |
|------|------|------|------|
| `5_problem1.tex:154` | 最大偏差 $1.97$ mK，$0.014\%$ | $1.16$ mK，$0.013\%$ | 原文自相矛盾（1.97 mK ≠ 0.0012 ℃）；实际 `max_dev_C=0.0011630` ℃，0.001163/8.7862=0.0132% |
| `3_assumptions.tex:5` | 端面占总换热面积 $8\%$ | $7.4\%$ | 侧面 2πRL=314.159、两端面 2πR²=25.133，占比 7.4074% |
| `3b_symbols.tex` | $C\in[0.15,2.55]$ | $[0.0525,2.55]$ | 全场最小含水率为末态表面 0.0525，非达标阈值 0.15 |
| `3b_symbols.tex` | $T_K\le323.4$；$w\ge0.130$ | $323.32$；$0.050$ | 50.165+273.15=323.315；w=C/(C+1) 在 C=0.0525 处为 0.0499 |
| `9_validation.tex:80` | 「放宽半个百分点」 | 「放宽 $0.05$~kg/kg」 | 0.15→0.20 kg/kg 是 +0.05 kg/kg（干基 5 个百分点），非半个百分点 |

其余 66 项经手工验算确认为合法派生量，包括 $Bi_h=1.389$、$Bi_m=3.241$、$\alpha/D=34.2$、
轴向/径向扩散时间比 $(12.5/2)^2=39.06$、附录 3/4 扩散系数区间 3.35e-10–1.36e-8 与
1.59e-10–2.52e-9（比值 0.186–0.476）、图内分箱物性均值、灵敏度导出百分比
（8.8%/10.6%/2.87%/7.47%/25.04 h）、干燥速率 0.6899 kg/(kg·h) 单调衰减（3404 点，
`argmax(rate)=0`，0 个上升步）。

### 2.2 缺字修复（150 → 0）

代码附录的 `\lstinputlisting` 落到 Latin Modern Mono（`lmmono9-regular`），
该字体缺希腊字母、箭头与数学算符，`code/*.py` 注释中的 44 个非 ASCII 字符整批丢字，
日志报 150 条 Missing character。

- 改 `\setmonofont{Consolas}`：覆盖 44 个字符中的 38 个（ξ χ λ ρ Σ ∫ Δ × ↑ ↓ → · § ℃ 以外的算符等）。
- 余下 6 个（⇒ ⛔ ℃ ∈ ≪ ⚠）无等宽字体覆盖。先试 `listings` 的 `literate`，无效；
  隔离测试确认根因：**listings 的字符分派表只处理码位 ≤255**，`é`（2 字节）可替换而
  `⇒`（3 字节）不能，与是否在注释中无关。
- 改用 `\newunicodechar` 兜底（cls 已加载该宏包，且 listings 不拦截 >255 的普通记号）：
  数学符号映射到 `\Rightarrow`/`\in`/`\ll`，`℃` 映射为 `$^\circ$C`（与正文既有 24 处写法一致），
  ⛔ ⚠ 取 Segoe UI Symbol 的对应码位。后两者在源码中用 TeX 的 `^^^^26d4` 记法书写，
  避免符号本体出现在正文源文件里。
- **未修改 `code/*.py`**（上游交付物）。

### 2.3 溢出修复（4 → 0）

- `4_common_model.tex` 式 `eq:prop_app3`、`eq:prop_app4`：单行四项超宽 14.58 pt / 8.68 pt，
  改用 `gathered` 将扩散系数式换到第二行。
- 式 `eq:cv`：超宽 13.59 pt，三项间距由 `\qquad` 收为 `\quad`。
- `code/main.py:73`（101 字符的 f-string）超宽 12.25 pt：`basicstyle` 由 `\small` 收为
  `\footnotesize`，并加 `columns=fullflexible`、`keepspaces=true`。

### 2.4 检查器损伤修复

`table_slim.py` 在上一步崩溃（`re.error: bad escape \i`，`inject_input` 行）前
已把 `A_code.tex` 的 24 行支撑材料清单截断为带 `$\vdots$` 的残表并留下悬空
`\ref{tab:full_A_code_0}`，同时写出孤立的 `A_tables.tex`（`main.tex` 未被注入 `\input`）。
已将清单恢复为完整 24 行 `longtable`，删除孤立文件。**未修改检查器本身。**

### 2.5 检查器 FAIL 项修复

- 图内字号：`tikz_cylinder_cv.pdf` 7.9 pt、`tikz_fv_stencil.pdf` 8.0 pt 低于 8 pt 印刷下限。
  两图契约标注的设计插入宽度为 0.86/0.92 `\textwidth`，而正文按 0.8/0.9 插入导致缩放偏小；
  已把插入宽度提到 0.94/0.98 `\textwidth`（未改图源画布与字号设置）。
- 措辞：`10_evaluation.tex` 与 `A_code.tex` 的「复用」改为「沿用」「共用的主求解流程」，
  `7_problem3.tex` 删去空话「换言之」。
- 包冲突告警属**误报**：检查器 grep 命中的是 `main.tex` 第 14 行「不要加 `\usepackage{cite}`」
  的注释文字，`cite` 宏包实际未加载（`main.log` 中 `cite.sty` 命中数为 0）。
  已改写该注释措辞消除误报，未加载/未卸载任何宏包。

## 3. 编译后检查

| 检查 | 结果 |
|------|------|
| `_utils/compile_check.sh paper/` | **exit 0**；缺字 0、Overfull 0、无 CJK 字体替换、85 页无内部空白页、公式全部编号、摘要检查通过、上标引用样式正确、图全部被引用、AI 痕迹措辞 0 处 |
| `_utils/writing_check.sh paper/ --supplemental` | **exit 0**；19 条文献对上 76 条检索留档，抽查 12 个 DOI，5 条因网络超时未能核实（非「确证不存在」） |
| `_utils/facts_audit.py --stage paper` | exit 2（**仅警告**）：45 个字段中 Schema / OCR 比对 / 派生值验算 / 正文结论一致性全部通过；抽样 30 个浮点数有 31 项未逐字命中，已手工归因（如 $-0.72$ 为灵敏度弹性、$0.92$ 为 `\topfraction` 排版参数，非结论数字） |
| `_utils/paper_claim_check.py` | **exit 0**；能力验收总账 16 条 PASS 16 / FAIL 0 / PENDING 0 |
| `build_ai_disclosure.py --check-only` | **exit 0**；首次运行报详情 PDF 早于论文改动，已重新生成 `AI工具使用详情.pdf`（70246 字节）后复验一致 |
| `pdf_snapshot_report.py sync` / `check` | **exit 0 / exit 0**；快照与最终 PDF 字节一致 |

**结构合规**

- 摘要单物理页：关键词落在第 1 页，正文「一、问题重述」自第 2 页起。
- 无目录页：源码中 `\tableofcontents` / `\listoffigures` / `\listoftables` 命中数为 0，
  且未生成 `main.toc` / `main.lof` / `main.lot`。
- 匿名化：`\schoolname` / `\membera-c` / `\baominghao` / `\supervisor` / `\tihao` 均处于注释状态。
- 代码附录存在：`\begin{appendices}` + 16 个 `\lstinputlisting`。
- 引用格式：全部 18 处统一用 `\upcite`（数字上标），无裸 `\cite`，无相邻未合并引用，
  多键引用由 `natbib` 的 `sort&compress` 处理。

**页数（仅报告，未据此增删正文）**

- 总 85 页 = 摘要 1 页 + 正文 2–44 页（43 页）+ 附录代码 45–85 页（41 页）。
- `SUBMISSION_PAGE_REFERENCE=30` 为参考值，按要求未为凑页数扩写或压缩任何正文内容。

## 4. 遗留告警（建议性，非已证缺陷）

- `fig_roadmap.pdf` 第 1 页 5 处文字「背景复杂，对比度需视觉复核」——检查器无法自动判定，
  需人工目视确认，未作改动。
- `3_assumptions.tex` 第 3 条假设偏长；题注偏长；均为写作建议。
- 5 个 DOI 因网络超时未能在线核实，检查器明确判为「非确证不存在」。
- 计划提到 TikZ 架构图但 `figures/tikz_architecture_examples.tex` 不存在——非本步交付物。

## 5. 未能签发的凭据

本轮**未生成** `paper_data_check.py --record-review` 回执：该脚本在本运行时的 `_utils/` 中
不存在，也未获得 `.mh/quality/data-review-ack-*.txt` 令牌。按质量门禁契约，
保持 pending 状态并如实报告，**未伪造回执**。已按要求在真实被 `main.tex` 收录的
`sections/10_evaluation.tex` 末尾写入 `% DATA_CHECK_PASSED` 标记。

## 6. 环境修复记录（为使编译可进行）

| 问题 | 处置 |
|------|------|
| 缺 7 个宏包（mdframed / placeins / needspace / tocloft / cleveref / newunicodechar / cprotect），`miktex packages install` 报「package is unknown」 | 先 `miktex packages update-package-database`；根因是 **MiKTeX 遇到任一未知包 ID 会整批中止**（本机 DB 中 `l3backend` 未知），改逐个安装后成功（装入 Roaming 根） |
| `ctex` 拒绝加载：`Support package 'expl3' too old`（2024-01-04） | 单独安装 `l3kernel`、`l3packages`，expl3 升至 2026-08-10 |
| `listings.sty` 1.11b 版本冲突（`listings.sty` 来自 Local\Programs，`lstpatch`/`lstmisc` 来自 Roaming） | `initexmf --update-fndb`，使二者从同一 tree 解析 |

<!-- MODEX_PDF_SNAPSHOT_BEGIN -->
## 最终 PDF 文件快照

> 以下仅证明文件版本、页数与哈希一致，不代表其他质量检查已通过。此前检查结论保留，是否仍适用需核对其输入版本。

- 文件：`C:/Users/asus/AppData/Roaming/MHAgent/workspaces/0c13ab9d36d4/paper/main.pdf`
- 实际总页数：**85 页**
- 文件大小：3397709 字节
- SHA-256：`6e86aa09c7ca32182e39121f214b0cf31d8b81def3d6744950b8dbbfa5fc24af`
- 快照时间（UTC）：2026-09-11T09:36:56+00:00

<!-- MODEX_PDF_SNAPSHOT_V1 {"bytes":3397709,"captured_at":"2026-09-11T09:36:56+00:00","pages":85,"pdf":"C:/Users/asus/AppData/Roaming/MHAgent/workspaces/0c13ab9d36d4/paper/main.pdf","sha256":"6e86aa09c7ca32182e39121f214b0cf31d8b81def3d6744950b8dbbfa5fc24af"} -->
<!-- MODEX_PDF_SNAPSHOT_END -->
