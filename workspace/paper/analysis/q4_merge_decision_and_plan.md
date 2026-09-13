# 问题四：是否换用物质坐标思路——审核结论与合并方案

- 审核基准分支：`codex/paper_commit_202609131226`（工作分支 `cursor/q4-merge-review-6aa4`）
- 对照实现：`cursor/q4-lagrangian-review-8b5c`
- 历史稿：`main`
- 补充资料：`problem4_boundary_methods_comparison.md`、`handover_conversation_archive.md`
- 本文件只做审核与方案；**不改论文正文、不改求解核、不重跑 51 h 仿真**

---

## 0. 一句话结论

**应当换用 Lagrangian 分支的“物质坐标叙事”，但不得换用该分支的离散核、粗网格数字、\(2\times 2\)/Shapley/β 新结构，也不得换用参考文献里带 \(\rho_{\mathrm{dry}}^2\) 的干基质量守恒方程。**

更精确的合并口径：

| 层 | 决策 |
|---|---|
| 连续物理 | 采用物质坐标解释：仿射骨架 \(v_s=r\dot R/R\) 下，\(\chi=1\) 的 Landau 方程与 \(\eta=(r/R)^2\) 方程是同一条经验扩散方程 |
| 离散实现 | **冻结** `paper_commit`：均匀 \(\xi\) 网格 FVM，\(N=1280\)，\(\Delta t=0.25\,\mathrm{s}\)，\(\chi=1\) 主算、\(\chi=0\) 交叉验证 |
| 交付数字 | **冻结** `paper_commit`：\(t_{\mathrm{end}}=51.0869\,\mathrm{h}\) 及现有表、效应链、交叉验证区间 |
| 行文 | 用物质坐标讲清“对流项为何消失”，\(\chi\) 降为交叉验证标签，以兼容已烘焙进图中的 \(\chi\)/\(S_0\)–\(S_4\) 字样 |
| 图表 | 不新制图、不改样式与外表；不重绘现有 PDF |
| 结果簿 | `result4.xlsx` 已与论文表一致，**不必因换思路重算**；`table6_problem4.csv` 仍是旧的 \(52.190\,\mathrm{h}\)，属发表级交付物错误，必须从 `result4.xlsx` 重写 |

---

## 1. 三套东西必须分开（本轮最容易写错的点）

| 名称 | 坐标 | 连续方程特征 | 本仓库谁在用 | 交付时长 |
|---|---|---|---|---|
| A. `paper_commit` 主模型 | 均匀 \(\xi=r/R(t)\)，\(\chi=1\) | 经验 Fick，无对流，无 \(\rho_d^2\) | 当前正式核 | \(51.0869\,\mathrm{h}\) |
| B. Lagrangian 分支主模型 | 均匀 \(\eta=(r/R)^2\) | **同一条**经验 Fick，无对流，无 \(\rho_d^2\) | `q4-lagrangian-review-8b5c` | \(50.780\,\mathrm{h}\)（\(N=40\)，分段 \(2\)–\(4\,\mathrm{s}\)） |
| C. 参考文献拉格朗日法 | \(s=\int_0^r\rho_{\mathrm{dry}}r'\,\mathrm{d}r'\) | \(\partial_t C=\partial_s(\rho_{\mathrm{dry}}^2 r^2 D\partial_s C)\) | **本仓库从未实现** | 约 \(50.8625\,\mathrm{h}\)（外源转述） |

B 的代码注释把 \(\eta\) 误写成“干基质量坐标 \(s=\int\rho_d r\,\mathrm{d}r\)”。那是 C，不是 B。下一任**禁止**把 C 的 \(\rho_d^2\) 方程写进正文，也禁止用 B 的注释去命名 A/B。

用户已确认：`main` 在 \(\chi=1\) 时的方程与 `paper_commit` 本质一致。本审核同意。`paper_commit` 相对 `main` 的保留点是：正式网格 \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)，以及把 \(\chi=1\) 升为主模型、\(\chi=0\) 降为交叉验证。

---

## 2. 为何“应当换叙事、不换核”

### 2.1 连续方程：A 与 B 等价

仿射收缩 \(v_s(r,t)=r\dot R/R\) 下，物质点满足 \(\xi=\mathrm{const}\)，因而 \(\eta=\xi^2=\mathrm{const}\)。此时

\[
\left.\frac{\partial C}{\partial t}\right|_{\xi}
=\left.\frac{\partial C}{\partial t}\right|_{\eta}
=\text{物质导数}.
\]

把 \(\eta=\xi^2\) 代入 Landau \(\chi=1\) 方程

\[
\frac{\partial C}{\partial t}
=\frac{1}{R^2}\frac{1}{\xi}\frac{\partial}{\partial\xi}\Bigl(\xi D\frac{\partial C}{\partial\xi}\Bigr)
\]

得

\[
\frac{\partial C}{\partial\xi}=2\xi\frac{\partial C}{\partial\eta},
\qquad
\frac{1}{\xi}\frac{\partial}{\partial\xi}\Bigl(\xi D\frac{\partial C}{\partial\xi}\Bigr)
=4\frac{\partial}{\partial\eta}\Bigl(\eta D\frac{\partial C}{\partial\eta}\Bigr).
\]

故

\[
\frac{\partial C}{\partial t}
=\frac{4}{R^2}\frac{\partial}{\partial\eta}\Bigl(\eta D\frac{\partial C}{\partial\eta}\Bigr).
\]

表面 Robin 同样等价：\(\xi=1\) 处 \(\partial_\xi C=2\partial_\eta C\)，于是

\[
-\frac{D}{R}\frac{\partial C}{\partial\xi}\Big|_{\xi=1}
=-\frac{2D}{R}\frac{\partial C}{\partial\eta}\Big|_{\eta=1}.
\]

能量方程同理。因此：**B 并不是另一种物理，只是 A 的换元写法。**

`main` / `paper_commit` 用开关 \(\chi\) 来表达同一件事：\(\chi=1\) 让物质点与计算坐标同步，对流抵消。物质坐标叙事的好处是：对流项的消失是坐标选择的推论，而不是“把一项关掉”。这正是应当吸收的“更好思路”。

### 2.2 离散层：A 与 B 并不相同，且 A 更应保留

| 项目 | `paper_commit`（A） | Lagrangian 分支（B） |
|---|---|---|
| 节点分布 | \(\xi\) 均匀 \(\Leftrightarrow\) 瞬时物理半径均匀 | \(\eta\) 均匀 \(\Leftrightarrow\) 表面更密 |
| 控制体权重 | 柱坐标面积 \(2\pi\xi\Delta\xi\)（与前三问同一套） | \(\eta\) 区间长度（无 \(2\pi\)） |
| 时间步 | 恒定 \(0.25\,\mathrm{s}\) | 分段 \(2\to 4\,\mathrm{s}\) |
| 网格 | \(N=1280\) | \(N=40\) |
| 环境平台 | \(50.0000^\circ\mathrm{C}\)、\(0.0500\,\mathrm{kg/kg}\) | \(50.165^\circ\mathrm{C}\)、\(0.04986\,\mathrm{kg/kg}\) |
| 达标定位 | `event_each_step=True` | 默认按输出步 |
| 效应结构 | \(S_0\)–\(S_4\) 链 | \(2\times 2\) + Shapley + \(\beta(t)\) |

有限 \(N\) 下两套网格给出不同数字，是预期现象，不是谁算错。\(N\to\infty\) 时收敛到同一连续解。

保留 A 的理由：

1. 均匀 \(\xi\) 在仿射收缩下**本身就是物质网格**（每个 \(\xi_i=i/N\) 跟着物质点走）。不必另建 \(\eta\) 网格才能称为物质坐标。
2. A 与问题一至三共用同一 FVM 装配，\(R\equiv\mathrm{const}\) 时精确退化。换 B 的 \(\eta\) 核会破坏“四问同一离散核”。
3. 用户要求合并后答案接近 `paper_commit`，并保留 \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)。
4. 现有图（`fig_chi_closure`、`fig_q4_shrink_effect`、`tikz_effect_isolation`、`tikz_landau_map`）已按 \(\chi\) 与 \(S_0\)–\(S_4\) 烘焙标签。换 \(2\times 2\) 或换核都会迫使改图或使图文打架。

### 2.3 为何不采用参考文献 C

C 把水分方程改写成带 \(\rho_{\mathrm{dry}}^2 r^2\) 的干基守恒型。`4_common_model.tex` 的式 `(eq:moisture)` 明确采用不含密度因子的经验扩散，前三问全部建立在这条式子上。若第四问单独改成 C，必须重写前三问或承认第四问换了一套水分方程——二者都超出“只改 Q4”的范围，也不是 B 实际实现的东西。

### 2.4 为何不整支合并 Lagrangian 数字

\(50.780\,\mathrm{h}\) 来自 \(N=40\)、分段 \(2\)–\(4\,\mathrm{s}\)、平台 \(50.165/0.04986\)、且问题三仍是旧的 \(56.706\,\mathrm{h}\)。它与 `paper_commit` 的 \(51.0869\,\mathrm{h}\) / \(57.4716\,\mathrm{h}\) 不在同一数值口径上。把 B 的表、Shapley、\(\beta\) 直接贴进 `paper_commit` 会制造跨问不一致。

---

## 3. 数据源核实（已在本机核对，下一任不得改这些数）

### 3.1 附件

| 数据 | 实测 | 使用口径 |
|---|---|---|
| 附件 1 | \(241\) 行；末点 \(t=14400\,\mathrm{s}\)，\(T=50.165^\circ\mathrm{C}\)，\(C=0.04986\,\mathrm{kg/kg}\)；末 \(30\) 点均值 \(50.0105^\circ\mathrm{C}\)、\(0.049982\,\mathrm{kg/kg}\) | `paper_commit` **有意**取稳态外推 \(50.0000^\circ\mathrm{C}\)、\(0.0500\,\mathrm{kg/kg}\)，并在 `4_common_model.tex` 写明末采样点不是平台值。此选择覆盖问题二至四，**本轮不改** |
| 附件 2 | \(145\) 点；\(t\in[0,259200]\,\mathrm{s}=72\,\mathrm{h}\)；\(R:2.000\to 1.198\,\mathrm{cm}\)；累积最小偏差 \(0\)（本身已单调） | PCHIP 保形插值。\(R(6\,\mathrm{h})=1.374\,\mathrm{cm}\)，\(R(51.0869\,\mathrm{h})=1.2000\,\mathrm{cm}\)，均在覆盖内 |

### 3.2 正式结果簿 vs 论文表

`output/result4.xlsx` 末行时刻 \(183912.7498\,\mathrm{s}=51.0868749\,\mathrm{h}\)，中心 \(C=0.1500\)，表面 \(0.05262\)。与 `8_problem4.tex` 表 `tab:p4_C` 逐格对照，四位小数一致（最大舍入差 \(5\times 10^{-5}\)）。

`output/final_diagnostics/q4_effect_isolation_final.csv`：

| 情景 | \(t_{\mathrm{end}}\) (h) | \(N\) | \(\Delta t\) |
|---|---|---|---|
| \(S_0\) | \(57.4693\) | \(1280\) | \(0.25\,\mathrm{s}\) |
| \(S_1\) | \(129.8423\) | \(1280\) | \(0.25\,\mathrm{s}\) |
| \(S_2\)（主） | \(51.0869\) | \(1280\) | \(0.25\,\mathrm{s}\) |
| \(S_3\)（\(\chi=0\)） | \(52.6476\) | \(1280\) | \(0.25\,\mathrm{s}\) |
| \(S_4\) | \(47.7985\) | \(1280\) | \(0.25\,\mathrm{s}\) |

INC1：\(\rho_s(C_{\mathrm{th}})/\rho_s(C_0)=2.4131\)，\((R_0/R_{\mathrm{end}})^2=2.7871\)，差 \(13.42\%\)；密度反演末半径 \(1.2875\,\mathrm{cm}\) vs 实测 \(1.1980\,\mathrm{cm}\)。

### 3.3 发表级不一致（必须修）

`output/table6_problem4.csv` **仍是旧稿**：结束时刻写成 \(52.190\,\mathrm{h}\)，\(6\,\mathrm{h}\) 中心 \(1.9357\)。这是 `main` 粗网格 \(\chi=0\) 的数，与现行 `result4.xlsx` / 论文表冲突。竞赛支撑材料若提交该 CSV，即数据源错误。

修复方式：由 `result4.xlsx` 按现有 `problem4.py::_write_table6` 规则重写，**禁止重跑求解**。

### 3.4 过期文件（禁止当数据源，本轮不必为它们改图）

下列文件**没有**被 `main.tex` 输入，但仍写着旧口径（\(\chi=0\) 主用、\(N=40\)、\(52.190\,\mathrm{h}\)）：

- `workspace/figures/problem_4_results.json`
- `workspace/figures/all_results.json`
- `workspace/figures/latex_includes.tex`
- `workspace/figures/_figdata/p4s2.npz` / `p4s3.npz`（图脚本已改读 `result4.xlsx` 与 `q4_chi0_*.csv`）

下一任若读这些文件来填表，会把论文写回 `main`。**只允许**下列正式源：

1. `workspace/paper/sections/8_problem4.tex` 现有数字（冻结）
2. `workspace/output/result4.xlsx`
3. `workspace/output/final_diagnostics/q4_effect_isolation_final.csv`
4. `workspace/output/final_diagnostics/q4_chi0_summary.csv`
5. `workspace/output/mass_consistency.csv`
6. 附件 1 / 附件 2 原始 xlsx

---

## 4. 修改范围（硬边界）

### 4.1 允许改

只改**问题四的建模表述**，以及摘要、分析、符号、评价、验证、附录清单中**明确在讲问题四**的句子。语言风格对齐 `paper_commit`（四位小时、完整句子、克制语气），不要写成 Lagrangian 分支那种短句体。

### 4.2 禁止改

- 问题一、二、三的模型、数字、表、图、`result1/2/3.xlsx`
- 图表样式、配色、线型、布局、尺寸；不新制任何图；不重跑 `gen_fig_*.py` 去“更新外表”
- 环境平台 \(50.0000/0.0500\)（跨问选择，不是 Q4 专有错误）
- \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)
- `result4.xlsx` 中的场数据（已与论文表一致）
- 把主方程改成 \(\rho_d^2\) 型
- 把效应隔离改成必须新画的 \(2\times 2\) / Shapley / \(\beta(t)\) 图
- 把 Lagrangian 的 \(50.780\)、\(56.706\)、\(128.906\)、\(25.088\) 写入正文

### 4.3 唯一的“发表级例外”

`table6_problem4.csv` 与论文表冲突，必须修。这是 Q4 交付物，不是“改其他问”。

`8_problem4.tex` 里“INC1 对时长影响预计小于 \(3.0550\%\)”是无计算支撑的断言。Lagrangian 稿写得更诚实：坐标交叉验证的几个百分点**不能**代替 INC1 对时长的影响。本轮应删掉或改成“未另算、不并入交付区间”。这仍属 Q4 文本，不是改其他问。

---

## 5. 文件清单：改什么、为何、改到什么程度

### 5.1 必须改（论文 Q4 叙事）

| 文件 | 改什么 | 为何 | 改到哪里为止 |
|---|---|---|---|
| `workspace/paper/main.tex` | 摘要中“针对问题四”一段；关键词可加“物质坐标”，保留“移动边界” | 摘要仍把 \(\chi=1\) 写成开关，未说明物质点 | 只动问题四句。问题一至三摘要数字一字不改 |
| `workspace/paper/sections/2_analysis.tex` | `\subsection{问题四的分析}` | 现在只讲“网格结点不固定 + 表观对流”，没有物质场 | 该小节内。路线图 `fig_roadmap` 不改 |
| `workspace/paper/sections/3b_symbols.tex` | 增 \(\eta\)、\(v_s\)；\(\xi\)、\(\chi\) 保留 | 正文要用 \(\eta\)；图里仍有 \(\chi\) | 只增行/改 \(\chi\) 的“含义”列，不删 \(\xi\) |
| `workspace/paper/sections/8_problem4.tex` | 建模小节按第 6 节重写；**结果数字、表、图环境全部冻结** | 这是换叙事的主战场 | 见第 6 节。禁止改 `eq:p4_answer`、`tab:p4_C`、`tab:effect` 中的小时与浓度 |
| `workspace/paper/sections/10_evaluation.tex` | 创新点三、局限二、结论里 Q4 句 | 仍把 \(\chi\) 写成“题面未给定的自由开关” | 只改这些句子的**表述**，数字不变 |
| `workspace/paper/sections/9_validation.tex` | 退化段“\(\chi=0\) 与 \(\chi=1\)”的解释句 | 可改成“实验室系与物质坐标在 \(\dot R=0\) 时恒等” | 不改残差、\(N\)、\(51.0869\)、灵敏度数字 |
| `workspace/paper/sections/A_code.tex` | `result4.xlsx` 那一行的 \(\chi=1\) 说明 | 与新叙事对齐 | 一行说明。**不要**改代码清单内容 |

### 5.2 必须改（交付 CSV）

| 文件 | 改什么 | 为何 |
|---|---|---|
| `workspace/output/table6_problem4.csv` | 用 `result4.xlsx` 重写，结束行 \(51.0869\,\mathrm{h}\)，浓度与论文表四位小数一致 | 现文件是 \(52.190\,\mathrm{h}\) 旧稿 |

### 5.3 可以改、但只许改注释/口径说明（算法禁止动）

| 文件 | 允许 | 禁止 |
|---|---|---|
| `workspace/code/fvm.py` | 注释写明：\(\chi=1\) 即物质坐标 / 仿射随动，连续极限等于 \(\eta\) 方程 | 增 `step_lagrange` 并改主路径；改 `FACE_MODE`、迎风、体积权重 |
| `workspace/code/driver.py` | 文件头说明问题四正式 `chi=1` | 改 `event_each_step`、步长策略、插值 |
| `workspace/code/problem4.py` | 模块说明与情景名注释 | 改 `_run` 的 \(N\)、`dt`、`chi`、几何 |
| `workspace/code/params.py` | `CHI_P4_PRIMARY` 旁注释 | 改 `N_P4_CV`、`DT_P4`、`TA_PLATEAU` |

若只改注释仍嫌越界，可以**完全不改 `.py`**。求解核已经正确。

### 5.4 默认不改

| 文件 | 理由 |
|---|---|
| `1_restatement.tex` | 问题四段只说“动域 + 换物性”，不错。不必为物质坐标改重述 |
| `3_assumptions.tex` | 假设（4）平台值、假设（5）径向不可逆收缩均正确且跨问 |
| `4_common_model.tex` | 式 `(eq:energy)(eq:moisture)(eq:bc_surface)` 是前三问根基。问题四网格句已写 \(N=1280\)。其中“干物质不迁移故水分方程不含密度因子”是经验扩散的公共前提，第四问用物质坐标消化它，不要回头改公共章 |
| `5/6/7_problem*.tex` | 非 Q4 |
| 全部 `workspace/figures/*.pdf` 与 `gen_fig_q4_*.py` | 禁新图、禁改外表。正文必须迁就图中已有的 \(\chi\)、\(S_0\)–\(S_4\) |
| `tikz_landau_map.tex` / `tikz_effect_isolation.tex` | 源里已写 \(\chi\) 与 \(S_2=\chi=1\)。改源再编译即改图外表，禁止 |
| `result4.xlsx`、`q4_*_final.csv`、`q4_chi0_*.csv`、`mass_consistency.csv` | 已与论文一致 |
| `result1.xlsx`–`result3.xlsx` | 非 Q4 |

### 5.5 明确不要从 Lagrangian 分支搬来的文件/结构

- `fvm.make_s_grid` / `step_lagrange` / `driver.frame='lagrange'` 作为交付路径
- `2\times 2\) 表 \(t_{00},t_{10},t_{01},t_{11}\) 与 Shapley 公式作为正式表（现图是 \(S_0\)–\(S_4\)）
- \(\beta(t)\) 曲线图
- `output/shrinkage_beta.csv`
- 任何把主方程写成 \(\partial_s(\rho_d^2 r^2 D\partial_s C)\) 的段落

---

## 6. `8_problem4.tex` 应如何写（与现图兼容的章节骨架）

保持现节名 **「问题四：收缩移动边界模型与收缩效应的定量隔离」**，以延续 `paper_commit` 语气。不要改成 Lagrangian 分支的短标题。

建议顺序（数字与 `\includegraphics` 一行不换）：

### 6.1 「相对问题三的两处改动」——保留开口，补一句物质场

保留“物性替换 + 域替换、判据/插值/边界形式沿用”。在“困难在于网格结点物理位置不固定”之前或之后加：干基含水率以干物质为基准，收缩时骨架携带结合水内移，故 \(C\) 首先是物质点上的场。坐标变换的目的是让计算坐标跟着物质点，而不是在缩小的物理网格上重划插值。

### 6.2 「物质坐标与归一化坐标」——替换原「归一化坐标下的控制方程」+「骨架运动学」的论证，但**保留 Landau 公式编号**

必须同时交代三件事，否则与 `tikz_landau_map`（图上是 \(\xi\) 与 \((1-\chi)\) 对流项）打架：

1. 仿射闭合 \(v_s=r\dot R/R\) 是使 \(\xi=r/R(t)\)（及 \(\eta=\xi^2\)）对每个干物质质点不变的径向速度。
2. 在定 \(\xi\) 的物质导数下，前三问经验扩散变成现有式 `(eq:landau_C)` 在 \(\chi=1\) 时的形式（无对流）。可加一条编号或随文写出 \(\eta\) 等价式，并写明 \(\eta=\xi^2\) 的换元，**不要宣称换了一套水分方程**。
3. 若改在实验室系写同一经验方程，再变到 \(\xi\)，才出现 \((1-\chi)\) 表观对流。\(\chi=0\) 是交叉验证，不是主模型。

公式建议：

- **保留** `(eq:landau)`、`(eq:chain)`、`(eq:landau_T)`、`(eq:landau_C)`、`(eq:landau_bc)` 的编号与现有符号，以免后文与验证章 `\eqref{eq:landau_T}` 断链。
- **新增** `(eq:eta)`、`(eq:vs)`，以及一句“\(\chi=1\) 时 `(eq:landau_C)` 与 \(\eta\) 方程等价”。
- 正式主模型用语：优先“物质坐标 / 材料随动（\(\chi=1\)）”，不要只写“把对流项关掉”。
- 仍用“ALE / Landau”指**计算域固定**这件事，因为图题就是 Landau 映射。

迎风、Péclet、三对角装配：保留，它们解释的是 \(\chi=0\) 交叉验证，且图注里有。

### 6.3 「半径时程的构造」——基本不改

附件 2 → 累积最小 → 保形三次（Fritsch 1980）已核实。\(2.000\to 1.198\,\mathrm{cm}\)、单调化偏差、\(R(t_{\mathrm{end}})=1.2000\,\mathrm{cm}\) 保留。

### 6.4 「烘干时长与含水率分布」——数字与图表全冻

冻结：

- \(t_{\mathrm{end}}=51.0869\,\mathrm{h}\)
- 表 `tab:p4_C` 全部格子
- 对问题三 \(57.4716\,\mathrm{h}\) 的 \(6.3847\,\mathrm{h}\) / \(11.1094\%\)
- \(6\,\mathrm{h}\) 中心 \(1.7188\) vs 问题三 \(1.0170\) 等对照句
- `fig_q4_moving_boundary`、`fig_q4_triptych` 的插入与尺寸参数

可改的只是领句：把“以主用闭合 \(\chi=1\) 的材料随动 ALE 求解”改成“在物质坐标（\(\chi=1\)）下，正式配置 \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)”。

### 6.5 「收缩效应的定量隔离」——保留 \(S_0\)–\(S_4\)，不换 \(2\times 2\)

`tikz_effect_isolation` 与 `fig_q4_shrink_effect` 的面板结构就是 \(S_0\to S_1\to S_2\) 加 \(S_3,S_4\)。换成 \(t_{00}/t_{01}\) 会与图矛盾。

冻结表 `tab:effect` 五个时长与分解 \(+72.3731/-78.7554/-6.3824\,\mathrm{h}\)。领句可写“物质坐标主模型对应 \(S_2\)”。

### 6.6 「闭合方式与数据自洽」——数字冻，删无依据估计

冻结 \(51.0869\) vs \(52.6476\)、差 \(1.5607\,\mathrm{h}=3.0550\%\)、区间 \([51.0869,52.6476]\,\mathrm{h}\)、INC1 \(13.42\%\) / \(7.47\%\)。

删除或改写：“对烘干时长的影响预计小于闭合方式带来的 \(3.0550\%\)”。改为：不相容度只作诊断，不修正 \(R(t)\)，不并入上述区间；其对时长的影响需另算，本文未另算。

`fig_chi_closure`、`fig_q4_mass_consistency` 不换。

---

## 7. 摘要 / 分析 / 评价的具体写法

### 7.1 摘要（只替换问题四句）

现句把主模型说成“Landau 变换 + 表观对流 + \(\chi=1\)”。建议改为（数字不动）：

> 针对问题四，外边界随失水内移。由附件 2 全部 \(145\) 个半径数据经单调化与 PCHIP 保形插值给出 \(R(t)\)。干基含水率是物质点上的场；在均匀仿射收缩下取物质坐标 \(\xi=r/R(t)\)（等价于 \(\eta=(r/R)^2\)），计算域固定且方程不再含表观对流。正式配置 \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)，物质坐标主模型得时长 \(51.0869\,\mathrm{h}\)、末态半径 \(1.2000\,\mathrm{cm}\)；实验室系 Landau（保留对流）交叉验证为 \(52.6476\,\mathrm{h}\)，相差 \(1.5607\,\mathrm{h}\)（\(3.0550\%\)）。

关键词保持五词左右。可写成：`热-质耦合 有限体积法 移动边界 物质坐标 烘干时长预测`。不要为加词而删“烘干时长预测”。

### 7.2 问题分析

现段“采用归一化坐标……代价是表观对流”改为：先物质场，再说明仿射闭合使 \(\xi\) 成为物质坐标，主方程无对流；实验室系写法才出现对流，用作交叉验证。归因段（换物性 vs 加收缩、INC1 不修正半径）保留。

### 7.3 评价章

创新点三：不要写成“题面无法判定 \(\chi\) 所以两个都算再随便交一个”。应写成：主模型由“\(C\) 是物质点上场 + 仿射骨架”闭合；\(\chi=0\) 是把同一经验方程写在实验室系的交叉验证；差 \(3.0550\%\) 说明运动学口径是次要不确定度。

局限二：同样改表述，数字不动。不要把主模型说成“在两个端点中选了 \(\chi=1\)”而不给物质坐标理由。

---

## 8. 语言与版式约束

- 对齐 `paper_commit`：长句、四位小时、百分数四位（\(11.1094\%\)、\(3.0550\%\)）。
- 不要用 Lagrangian 稿的三位小时（\(50.780\)）或“无需再引入 \(\chi\)”——图上还有 \(\chi\)，删掉符号会造成图文不一致。
- 所有 `\includegraphics[...,height=0.8\textheight,keepaspectratio]` 以及现有 width 分数保持原样。
- 不新增 `figure` 环境，不新增表（CSV 修复不算新表）。
- 公式编号：旧编号不删不挪；新公式只加在问题四建模段。

---

## 9. 代码与结果：本轮默认不重跑

重跑第四问（\(N=1280\)、内部 \(0.25\,\mathrm{s}\)、约 \(51\,\mathrm{h}\)）昂贵，且 `result4.xlsx` 已与论文一致。

只有在下一任**擅自改了离散核**之后才需要重跑。本方案禁止改核，因此：

- 不重写 `result4.xlsx`
- 不重算 \(S_0\)–\(S_4\)
- 只用 `result4.xlsx` 修复 `table6_problem4.csv`
- 若改了 `.py` 注释，不必因注释重跑

若有人坚持把 `step_lagrange` 接到交付路径：必须在 **同一** \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)、同一平台值、同一 `event_each_step` 下重跑，并证明 \(t_{\mathrm{end}}\) 与 \(51.0869\,\mathrm{h}\) 的相对差足够小；即便如此，现图标签仍是 \(\chi\)，仍不能改图。**本方案不采纳这条路径。**

---

## 10. 验收清单（给下一任自检）

1. `8_problem4.tex` 能从物质点讲到 \(\chi=1\) 与 \(\eta\) 等价，且仍引用 `(eq:landau_C)`。
2. 全文检索：交付时长只出现 \(51.0869\)，交叉验证只出现 \(52.6476\)，问题三只出现 \(57.4716\)。不得出现 \(50.780\)、\(52.190\)、\(50.694\)、\(56.706\)。
3. 无 \(\rho_{\mathrm{dry}}^2\) / \(\rho_d^2\) 作为主方程。
4. 无新的 `figure`，现有 `\includegraphics` 路径与可选参数不变。
5. `tab:p4_C`、`tab:effect` 数字与本文件第 3.2 节一致。
6. `table6_problem4.csv` 结束行约 \(51.0869\,\mathrm{h}\)，\(6\,\mathrm{h}\) 中心约为 \(1.7188\) 而非 \(1.9357\)。
7. 问题一至三 tex 的 diff 为空（或仅有无关空白，应避免）。
8. `params.py` 中 `N_P4_CV=1280`、`DT_P4=0.25`、`TA_PLATEAU=50.0` 未改。
9. INC1 段不再声称“对时长影响小于 \(3.0550\%\)”。
10. 编译通过；正文页数变化仅来自问题四建模段加长，不靠删图缩页。

---

## 11. 给实施 agent 的提示词位置

完整、可粘贴的实施提示词见同目录：

`workspace/paper/analysis/q4_merge_implementation_prompt.md`
