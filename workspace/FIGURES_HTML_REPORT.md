# 示意图交付报告（paper-figure-html，步骤 5/8）

本轮只产出**非数据类示意图**：HTML+CSS 转矢量 PDF 3 张 + TikZ 4 张，合计 7 张。
上一阶段的 22 张 DATA 图（脚本、配色、PDF/PNG）本轮**未改动一字节**，`diagram_style=mono`
只作用于本轮的流程图/示意图。

## 一、交付清单

| 图名 | 引擎 | 原生尺寸 pt | 高/宽 | 插入宽度 | 成图最小字号 |
|---|---|---|---|---|---|
| `fig_roadmap` | HTML+CSS | 713×492 | 0.69 | 0.98\textwidth | 8.2 pt |
| `fig_pipeline` | HTML+CSS | 812×539 | 0.66 | 0.96\textwidth | 8.1 pt |
| `fig_coupling_structure` | HTML+CSS | 608×327 | 0.54 | 0.90\textwidth | ≥8 pt |
| `tikz_cylinder_cv` | TikZ | 368×323 | 0.88 | 0.80\textwidth | 8.10 pt |
| `tikz_fv_stencil` | TikZ | 407×230 | 0.57 | 0.90\textwidth | 8.25 pt |
| `tikz_landau_map` | TikZ | 351×306 | 0.87 | 0.80\textwidth | 9.56 pt |
| `tikz_effect_isolation` | TikZ | 453×317 | 0.70 | 0.90\textwidth | 8.33 pt |

TikZ 图同时交付同名 `.tex` 源文件，文件头带图契约（purpose / topology / node_roles /
edge_roles / style_family / annotation_policy / result_policy / final_width / print_mode）。

全部 7 张：单页、0 位图、纯黑白线稿、图内无标题、图内无数值结果与结论措辞。
`result_policy` 逐图声明：几何/机理三图为 `none`，`tikz_effect_isolation` 为 `symbolic`
（只出现符号差 $t_{S2}-t_{S0}=(t_{S1}-t_{S0})+(t_{S2}-t_{S1})$，不出现任何小时数）。

## 二、门禁结果

| 门禁 | 结果 |
|---|---|
| `html_pdf_check`（3 张 HTML 图） | PASS |
| `--geom-check` / `--norm-check`（3 张 HTML 图） | PASS |
| `tikz_check.sh`（4 张 TikZ 图） | 0 CRITICAL，节点无重叠 |
| `fig_include_size.py --strict` | 尺寸已符合，无需改动 |
| `figure_pdf_quality_check.py figures` | OK（另有 5 项需视觉复核，见第四节） |
| `latex_includes.tex` 结构 | 29 figure / 29 唯一 label / 0 重复 / 0 悬空 ref / 29 PDF 均在 |
| 视觉门 | **未清洁通过**，见第五节 |

`latex_includes.tex` 现有 29 个 figure 块：上一阶段 22 张 + 本轮 7 张。口径与结论一律写在
caption 里，图面只留必要锚点。

## 三、本轮修掉的真实缺陷

### 1. 印刷字号不达标（2 张 TikZ 图，真实 FAIL）

`figure_pdf_quality_check.py` 按**字符数加权的 10% 分位**判印刷字号，下限 8 pt。数学下标默认
取基号 2/3，`\small` 基号 8.97 pt 下的下标仅 5.98 pt；`tikz_cylinder_cv` 与
`tikz_fv_stencil` 的下标字符占比达 31%–34%，把 p10 直接拉到 5.98 pt，按 0.8/0.9
\textwidth 插入后成图仅 6.1 / 6.2 pt。

修法是抬下标字号而非缩画布、也不删内容：

```latex
\DeclareMathSizes{9}{9}{8.4}{8.4}
```

改后 p10 = 7.97 pt，成图 8.10 / 8.25 pt，双双过线。另两张 TikZ 图下标占比仅 4%–8%，p10
本就落在 8.97 pt，加同一行只为口径一致。

### 2. 文字块重叠（4 张 TikZ 图，共 9 处）

PyMuPDF 把三类 LaTeX 排版结构拆成**多个行盒**，检查器按行盒相交面积比判重叠，于是同一公式
的组成部分互判重叠。按形态逐类改写，不动版面：

| 形态 | 出现处 | 改写 |
|---|---|---|
| 同一符号上下标并置 | `q_N^{\mathrm{out}}`、`\varphi_{i-1}^{n+1}`、`r_{N-1/2}^2` | 上标移入文字（「外向通量」）／时间层移到行首标号、结点只留空间下标／`V_N` 改因式分解写法 |
| 行分式 `\dfrac` | landau_map 的链式法则与表观对流项 | 改斜线形式 `(\partial\varphi/\partial t)_{r}` |
| `\underbrace` | effect_isolation 的加和恒等式 | 花括号删除，两项效应名改为恒等式下方说明行 |

改后 4 张图重叠数 0。`fig:cylinder_cv` 的 caption 同步跟改为 `q_N` 与 `V_N` 因式写法，
与图面一致。

### 3. caption 里的 Markdown 与字体外字符（真实缺陷，只在实编译后暴露）

本轮 7 段 caption 里残留 3 处 `**粗体**`（LaTeX 会原样打出星号）与 3 处 ⛔（宋体无此字形，
静默丢字）。已改为 `\textbf{}` 与「注意：」。实编译后的 PDF 抽取文字确认：`**` 0 处、
⛔ 0 处，「保序算子分裂」「渐进承接链」「双向环」「注意：」均正常出现。

这三处是**文件级检查查不出来的**——只有真正编译一遍再抽取 PDF 文字才会暴露，故第四节把这次
编译验证单列。

## 四、实编译验证（临时驱动，非交付文件）

用最小驱动 `_compile_check.tex` 把 `figures/latex_includes.tex` 整体 `\input` 进去，
XeLaTeX 连跑两遍：

```
PASS1=0  PASS2=0   21 页
! 错误 0   缺字 0   Overfull \hbox 4（最宽 31.7 pt）
```

29 张 `\includegraphics` 全部找到，29 个 `\ref` 全部解析。验证完即删驱动与中间文件。

过程中排掉三个**驱动侧**假问题，均不是 `latex_includes.tex` 的缺陷：

- **`\gtrsim` 未定义**——上一阶段 caption 用到，驱动缺 `amssymb`。加载即过。
  正文导言区必须有 `amssymb`。
- **86 处缺 em dash（U+2014）**——我第一版驱动只 `\usepackage{fontspec}` 而漏了
  `\setmainfont{SimSun}`，正文落回 Latin Modern，自然没有 U+2014。补上后缺字归零。
  一度据此判定「SimSun-fontspec 会丢 em dash」是错的。
- **CJKutf8 路线不可用**——为找中文断行方案试过 `CJKutf8`，纯中文段落测试通过（缺字 0、
  Overfull 2），但套到本文件即报 `Package CJK Error: Invalid character code`：caption
  大量「中文夹行内公式」，`$...$` 切换字体后双字节配对失效。已放弃该路线。

剩下 2 条 `LaTeX Font Warning: Font shape TU/SimSun(0)/b/n（及 /m/it）undefined`：宋体无
粗体与斜体变体，本轮 3 处 `\textbf` 与 caption 里的 `\emph` 在这个最小驱动下退化为正体。
文字不丢，只是强调看不出来。正文若用正规 CJK 方案（黑体做粗、或 `\CJKfamily` 切字族）即恢复；
**这是驱动限制，不是 caption 缺陷，不要据此删掉 `\textbf`。**

## 五、视觉门：未清洁通过（须知情）

| 图 | 视觉判定 | 依据 |
|---|---|---|
| 3 张 HTML 图 | 在**全局调用上限**处定稿 | 第 4 轮返回 `STOP_VISION_LOOP`，工具明示「用当前最新 PDF 定稿，不要再改坐标/重导出/重调 vision」 |
| 4 张 TikZ 图 | **skipped** | 两次 HTTP 502 后 `NO_VISION_API: No vision-capable LLM configured` |

回执写在 `_tmp/vision_passed.txt`、`_tmp/vision_unresolved.txt`、`_tmp/vision_skipped.txt`。

一条未闭环意见记在 `vision_unresolved.txt`：`fig_coupling_structure` 被指箭头未对中。我用像素
质心实测反驳（173.5 对框心 173.5；835.5 对 836），判为工具误报，未改图。

替代证据：四门静态检查 + PyMuPDF 逐 span 实测（单页、0 位图、0 真实重叠、0 出界）+ 上面的
实编译。**但这不等于视觉合格：这 7 张图没有任何模型、也没有人真正看过。**

## 六、三类结构性误报（如实报告，未按其修改）

1. **`tikz_check.sh` 的 CJK 宽度告警**（如「需要 31.4cm 但只有 9.2cm」）：把 `\\` 分隔的
   多行汉字累加成单行估宽。PyMuPDF 实测 0 重叠、0 出界。
2. **`tikz_check.sh` 不解析 `\tikzset` 样式别名**：其重叠估算只读节点方括号里的字面量，
   `minimum width` / `text width` 写进样式别名一律无效，必须逐节点内联。
   （`tikz_fv_stencil` 第一次修重叠就栽在这里。）
3. **`figure_pdf_quality_check.py` 对 `fig_roadmap` 的 5 条「背景复杂，对比度需视觉复核」**：
   汉字（解、题）笔画密集、墨量高，span 盒内主色占比低于 0.55 阈值。图是纯黑字透明底，
   不存在低对比度；检查器本身已把这类降级为 WARN 而非 FAIL。

这三类的自动建议若照改，会把本来正确的图改坏。判据是 PyMuPDF 逐 span 实测。

## 七、遗留事项

- **视觉门未清洁通过**（第五节）。若要补视觉复核，需配 `EDITOR_AI_API_KEY` 或
  `OPENAI_API_KEY`，且 DrawIO 视觉自检的工作区总调用上限换名也绕不过。
- **正文导言区**须有 `graphicx`、`float`、`amsmath`、`amssymb`，以及一个能处理
  「中文夹行内公式」的 CJK 方案（本机 `ctex`/`xeCJK` 因 expl3 为 2024-01-04 拒绝加载，
  `CJKutf8` 在夹公式场景报错，故本机只有 fontspec 直绑宋体一条路，代价是无粗体/斜体变体
  且中文不自动断行）。
- 14 处位图全部落在上一阶段的 6 张热图/散点图（`pcolormesh`、rasterized scatter 的正常用法），
  本轮 7 张图 0 位图。

