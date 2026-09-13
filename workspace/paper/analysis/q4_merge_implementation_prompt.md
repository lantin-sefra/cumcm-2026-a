# 实施提示词（下一任 agent 直接粘贴）

你在仓库 `lantin-sefra/cumcm-2026-a` 上工作。实施底稿改为

`origin/cursor/drop-redundant-figures-9caa`

该分支比 `codex/paper_commit_202609131226` 只少了三张前三问图，问题四数字未改。
先 `git fetch origin cursor/drop-redundant-figures-9caa`，再从该提交拉出新分支。
不要以 `main` 或 `cursor/q4-lagrangian-review-8b5c` 为写作底稿。
当前实施分支为 `cursor/q4-material-narrative-6aa4`（若已存在则在该分支上继续）。

先读：

1. `workspace/paper/analysis/q4_merge_decision_and_plan.md`（本轮审核结论，以它为准）
2. 当前 `workspace/paper/sections/8_problem4.tex`
3. 当前 `workspace/paper/main.tex` 摘要里“针对问题四”一段
4. **不要**把 `cursor/q4-lagrangian-review-8b5c` 的 `8_problem4.tex` 整段覆盖过来
5. **不要**使用 `workspace/figures/problem_4_results.json`、`all_results.json`、`latex_includes.tex`、`table6_problem4.csv`（修之前）里的旧数字

回复用简体中文。

---

## 任务

把问题四的**行文**改成物质坐标叙事，使读者明白：`paper_commit` 已经在算的 \(\chi=1\) 材料随动，就是仿射收缩下的物质坐标，与 \(\eta=(r/R)^2\) 连续等价。

**不是**换物理模型，**不是**换网格，**不是**重算 `result4.xlsx`，**不是**采用参考文献的 \(\partial_s(\rho_{\mathrm{dry}}^2 r^2 D\partial_s C)\)。

---

## 硬约束（违反任一条即失败）

1. 不要改图表样式、外表、配色、线型、尺寸、`height=...` / `width=...`。不新制图，不重跑 `gen_fig_*.py`，不重编译 `tikz_*.tex` 去替换 PDF。
2. 修改集中在问题四以及摘要/分析/符号/评价/验证/附录清单中**与问题四直接有关**的句子。除非发表级错误，不改问题一至三。
3. 保持 `codex/paper_commit_202609131226` 的语言风格：完整句子、四位小时、克制语气。不要写成 Lagrangian 分支的短句体。
4. 不生成新图表、不新增 `figure` 环境、不新增结果表。
5. 正式网格与步长保持 \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)。
6. 交付数字必须与现状逐字一致（见下方冻结表）。禁止写入 \(50.780\)、\(52.190\)、\(50.694\)、\(56.706\)、\(128.906\)、\(25.088\)。
7. 禁止把主方程改成带 \(\rho_d^2\) 或 \(\rho_{\mathrm{dry}}^2\) 的守恒型。
8. 禁止把效应隔离改成正式 \(2\times 2\) / Shapley / \(\beta(t)\) 表或图。现图是 \(S_0\)–\(S_4\) 与 \(\chi=0/1\)。
9. 禁止改 `TA_PLATEAU` / `CA_PLATEAU`（现为 \(50.0\) / \(0.0500\)）。这是跨问选择，已在 `4_common_model.tex` 写明。
10. 禁止改 `result1.xlsx`、`result2.xlsx`、`result3.xlsx`、`result4.xlsx` 的场数据。
11. 均匀 \(\xi\) 网格 + \(\chi=1\) 已是物质坐标的合法离散。不要把 `step_lagrange` / `make_s_grid` 接到交付路径。
12. Lagrangian 分支注释里的“干基质量坐标 \(s=\int\rho_d r\,\mathrm{d}r\)”是**命名错误**。那个积分是另一篇参考文献的坐标。本仓库实现的是 \(\eta=(r/R)^2\) 经验扩散。禁止把两套名字混成一套。

---

## 冻结数字（必须原样出现，禁止重算替换）

来源：当前 `8_problem4.tex` + `result4.xlsx` + `q4_effect_isolation_final.csv` + `q4_chi0_summary.csv` + `mass_consistency.csv`。本机已核对 `result4.xlsx` 与论文表四位小数一致。

| 量 | 值 |
|---|---|
| 问题四交付时长 | \(51.0869\,\mathrm{h}\) |
| 末态半径 | \(1.2000\,\mathrm{cm}\) |
| 结束时刻 \(\max C\) | \(0.1500\,\mathrm{kg/kg}\) |
| 问题三正式时长 | \(57.4716\,\mathrm{h}\) |
| 问四相对问三 | 短 \(6.3847\,\mathrm{h}\)，\(11.1094\%\) |
| \(\chi=0\) 交叉验证 | \(52.6476\,\mathrm{h}\) |
| 闭合差 | \(1.5607\,\mathrm{h}\)，\(3.0550\%\) |
| 报告区间 | \([51.0869,\,52.6476]\,\mathrm{h}\) |
| \(S_0\) | \(57.4693\,\mathrm{h}\)（共同网格诊断，不是正式问题三） |
| \(S_1\) | \(129.8423\,\mathrm{h}\) |
| \(S_2\) | \(51.0869\,\mathrm{h}\) |
| \(S_3\) | \(52.6476\,\mathrm{h}\) |
| \(S_4\) | \(47.7985\,\mathrm{h}\) |
| 换物性 / 加收缩 / 净效应 | \(+72.3731\) / \(-78.7554\) / \(-6.3824\,\mathrm{h}\) |
| INC1 | \(2.4131\) vs \(2.7871\)，\(13.42\%\)；反演半径 \(1.2875\,\mathrm{cm}\) vs \(1.1980\,\mathrm{cm}\)，\(7.47\%\) |
| 网格 | 问题四 \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)；问题二/三 \(N=2560\)、\(\Delta t=0.25\,\mathrm{s}\) |
| 表 `tab:p4_C` | 以当前 tex 为准（\(6\,\mathrm{h}\) 中心 \(1.7188\)，表面 \(0.4205\)，……，结束行 \(0.1500,0.1413,0.1081,\mathrm{---},\mathrm{---},0.0526\)） |

附件事实（可写，勿改口径）：附件 1 共 \(241\) 点，末点 \(50.165^\circ\mathrm{C}\)、\(0.04986\,\mathrm{kg/kg}\)，正文平台仍用 \(50.0000/0.0500\)；附件 2 共 \(145\) 点，\(2.000\to 1.198\,\mathrm{cm}\)，\(72\,\mathrm{h}\) 覆盖，\(R(6\,\mathrm{h})=1.374\,\mathrm{cm}\)，单调化偏差 \(0\)（论文写 \(2.2\times10^{-16}\,\mathrm{cm}\) 可保留原文）。

---

## 建模上必须写清的等价关系（可写入正文，不得写反）

仿射速度 \(v_s=r\dot R/R\) 使物质点的 \(\xi=r/R(t)\) 与 \(\eta=\xi^2=(r/R)^2\) 均不随时间变。因此 \(\partial_t|_{\xi}=\partial_t|_{\eta}\)。

\(\chi=1\) 的 Landau 水分方程

\[
\partial_t C=\frac{1}{R^2}\frac{1}{\xi}\partial_\xi(\xi D\partial_\xi C)
\]

换元后即

\[
\partial_t C=\frac{4}{R^2}\partial_\eta(\eta D\partial_\eta C).
\]

边界 \(-\frac{D}{R}\partial_\xi C|_{\xi=1}=h_m(C-C_{\mathrm{air}})\) 与 \(-\frac{2D}{R}\partial_\eta C|_{\eta=1}=h_m(C-C_{\mathrm{air}})\) 等价。能量方程同理。

这与前三问是**同一套经验扩散**，只改自变量。不是新的干基质量守恒方程。

离散上：现核在均匀 \(\xi\) 上做柱坐标 FVM，\(\chi=1\) 时不装配对流项。每个 \(\xi_i=i/N\) 在仿射收缩下跟着物质点走，故该核已经是物质坐标方法。不要另写“我们必须改用 \(\eta\) 均匀网格”。

\(\chi=0\)：同一经验方程写在实验室系后再作 Landau 变换，对流项用一阶迎风。只作交叉验证。

---

## 必须修改的文件与改法

### A. `workspace/paper/main.tex`

只改摘要“针对问题四……”到该句结束，以及 `\keywords`。

- 先写物质场与仿射物质坐标，再写时长。
- 保留 \(51.0869\,\mathrm{h}\)、\(1.2000\,\mathrm{cm}\)、\(52.6476\,\mathrm{h}\)、\(1.5607\,\mathrm{h}\)、\(3.0550\%\)。
- 关键词建议：`热-质耦合\quad 有限体积法\quad 移动边界\quad 物质坐标\quad 烘干时长预测`
- 问题一至三摘要数字禁止动。

### B. `workspace/paper/sections/2_analysis.tex`

只改 `\subsection{问题四的分析}`。

- 开口仍是“同时改物性与求解域”。
- 把“归一化坐标的代价是表观对流”改成：主叙述是物质坐标，对流只在实验室系对照中出现。
- 保留归因警告与 INC1 不修正半径。
- 不要改 `fig_roadmap`。

### C. `workspace/paper/sections/3b_symbols.tex`

在 \(\xi\)、\(\chi\) 附近增加：

- \(\eta\)：归一化物质坐标 \((r/R(t))^2\)，范围 \([0,1]\)
- \(v_s\)：固相仿射速度 \(r\dot R/R\)，单位 \(\mathrm{m\cdot s^{-1}}\)

\(\chi\) 的含义改为“实验室系对照开关：\(1\) 物质坐标主模型，\(0\) 保留表观对流”。不要删除 \(\xi\) 或 \(\chi\)（图上有）。

### D. `workspace/paper/sections/8_problem4.tex`（主改）

节名保持：`问题四：收缩移动边界模型与收缩效应的定量隔离`。

**保留且不得改数字的块：**

- `\begin{equation}\label{eq:p4_answer}` 及后文 \(51.0869\)
- 表 `tab:p4_C` 全部内容
- 表 `tab:effect` 全部内容
- 所有 `\includegraphics{../figures/fig_q4_*.pdf}`、`fig_input_shrinkage`、`fig_chi_closure`、`fig_q4_mass_consistency`、`tikz_landau_map`、`tikz_effect_isolation`
- 各图 `\caption` 可微调措辞，但不要改到与图内已烘焙文字（\(\chi=1\) 材料随动 ALE、\(S_0\)–\(S_4\)）矛盾
- 式编号 `(eq:landau)` `(eq:chain)` `(eq:landau_T)` `(eq:landau_C)` `(eq:landau_bc)` `(eq:decomp)` 必须保留，因为 `9_validation.tex` 引用了 `eq:landau_T`、`eq:landau_C`

**应重写的块：**

1. 「相对问题三的两处改动」：保留两处改动清单；补上 \(C\) 是物质点上场。
2. 把「归一化坐标下的控制方程」+「骨架运动学的闭合」改写成「物质坐标与归一化坐标」：
   - 定义 \(\xi=r/R(t)\)、\(\eta=(r/R)^2\)、\(v_s=r\dot R/R\)
   - 说明 \(\chi=1\) 时 `(eq:landau_C)` 即物质导数下的经验扩散，并写出与 \(\eta\) 方程等价（可新编号）
   - 说明 \(\chi=0\) 是实验室系交叉验证
   - 保留迎风 / Péclet / 三对角，作为 \(\chi=0\) 与图 `tikz_landau_map` 的解释
   - 不要写“题目无法确定 \(\chi\) 所以我们任意选 \(1\)”。应写：主模型由物质场 + 仿射骨架闭合；\(\chi=0\) 用于量化把同一方程写在实验室系的差异
3. 「半径时程」基本不动。
4. 「烘干时长」只改领句，数字与表不动。
5. 「效应隔离」保持 \(S_0\)–\(S_4\) 与 `(eq:decomp)`。不要引入 \(t_{01}\) / Shapley。
6. 「不确定度与 INC1」：数字不动；**删除**“对烘干时长的影响预计小于 \(3.0550\%\)”。改为：不相容只作诊断，不修正半径，不并入 \([51.0869,52.6476]\,\mathrm{h}\)；该影响需另算，本文未另算。

### E. `workspace/paper/sections/10_evaluation.tex`

只改与问题四运动学/创新点三/局限二/结论 Q4 句有关的表述。所有小时数保持上表。不要改潜热 \(10.35\%\)、灵敏度弹性、问题一/二读数。

创新点三建议逻辑：主模型有物质坐标理由；\(\chi=0\) 是交叉验证；差 \(3.0550\%\) 说明口径次要。不要写成“两个端点随便交一个”。

### F. `workspace/paper/sections/9_validation.tex`

只许改“令 \(\dot R\equiv 0\) 则 \(\chi=0\) 与 \(\chi=1\) 相同”那几句的解释（可写成物质坐标与实验室系在无收缩时恒等）。禁止改残差、收敛图读数、\(51.0869\)、平台 \(50.0000/0.0500\)、灵敏度。

### G. `workspace/paper/sections/A_code.tex`

只改清单中 `result4.xlsx` 那一行说明，例如改为“问题四物质坐标主模型（\(\chi=1\)）收缩域水分浓度全网格”。不要改 `\lstinputlisting` 列表。

### H. `workspace/output/table6_problem4.csv`（发表级修复）

当前文件是旧稿 \(52.190\,\mathrm{h}\)、\(6\,\mathrm{h}\) 中心 \(1.9357\)。必须用 `result4.xlsx` 按现有 `problem4.py::_write_table6` 规则重写：

- 行：\(6,12,\ldots,48\,\mathrm{h}\) + 末行「烘干结束时间 \(51.087\,\mathrm{h}\)」或与现函数一致的 \(51.0869\) 格式（现函数用 `{t_end_s/3600:.3f}h`，会得到 `51.087h`；**若要与论文表 `51.0869 h` 完全一致，允许把该处格式改为四位小数，这仍算 Q4 交付物修复**）
- 列：`0,0.5,1,1.5,2,药材表面`；域外空
- 数值与 `tab:p4_C` 四位小数一致
- 禁止重跑 `driver.run`

可用短 Python 从 `result4.xlsx` 抽取，不要调用完整 `problem4.solve()`。

---

## 默认不要改的文件

`1_restatement.tex`，`3_assumptions.tex`，`4_common_model.tex`，`5_problem1.tex`，`6_problem2.tex`，`7_problem3.tex`，全部 figure PDF，全部 `gen_fig_*.py`，`tikz_landau_map.tex`，`tikz_effect_isolation.tex`，`params.py` 的数值常量，`fvm.py` / `driver.py` / `problem4.py` 的算法，`result4.xlsx`，`q4_effect_isolation_final.csv`，`q4_chi0_*.csv`，`mass_consistency.csv`，`result1/2/3.xlsx`。

若只想让代码注释与论文一致，可在 `fvm.py` / `problem4.py` 文件头加一两句“\(\chi=1\) 即物质坐标，连续等价于 \(\eta=(r/R)^2\) 经验扩散”。不要因此改算法，不要接 `step_lagrange`。

---

## 明确不要做的“更好”

- 不要把 Lagrangian 分支的 \(2\times 2\)、交互项 \(-46.240\,\mathrm{h}\)、Shapley、\(\beta\) 均值 \(0.298\) 写入正文。那些数属于 \(N=40\) 旧平台，且现图不是那套结构。
- 不要为 \(\beta(t)\) 或 \(t_{01}\) 新做图。
- 不要把 `4_common_model.tex` 的水分方程改成守恒型去“对齐”物质坐标。
- 不要把环境平台改回 \(50.165/0.04986\)。
- 不要为了“更严谨”重跑 \(N=1280\) 的 \(\eta\) 均匀网格。

---

## 实施顺序

1. 从 `origin/codex/paper_commit_202609131226` 建分支（名称遵守仓库前缀规则）。
2. 先重写 `table6_problem4.csv`，用脚本对照 `result4.xlsx` 打印 diff，确认 \(6\,\mathrm{h}\) 中心变为约 \(1.7188\)。
3. 改 `8_problem4.tex` 建模段。
4. 改摘要、`2_analysis`、`3b_symbols`、`10_evaluation`、`9_validation` 的 Q4 句、`A_code` 一行。
5. `rg` 检查：正文与摘要不得出现 \(50.780|52.190|50.694|56.706|128\.906|25\.088|\rho_d\^2|\rho_{\mathrm{dry}}\^2\)。
6. `git diff --stat` 确认问题一至三 tex 无实质改动。
7. 若环境能编译 XeLaTeX，编译 `workspace/paper/main.tex` 并检查问题四交叉引用未断（尤其 `eq:landau_T`）。
8. 提交信息应说明：问题四改为物质坐标叙事，冻结 \(51.0869\,\mathrm{h}\) 与 \(N=1280\)，并修复过期 `table6`。

---

## 验收（做完必须自报）

- [ ] 物质坐标叙事成立，且写明与 \(\chi=1\) Landau / \(\eta\) 方程等价
- [ ] 未采用 \(\rho_d^2\) 方程
- [ ] 冻结数字全部仍在
- [ ] 无新图，旧图路径与几何参数未改
- [ ] `table6_problem4.csv` 已与 `result4.xlsx` / 论文表一致
- [ ] INC1 不再声称“影响小于 \(3.0550\%\)”
- [ ] 问题一至三未改
- [ ] \(N=1280\)、\(\Delta t=0.25\,\mathrm{s}\)、平台 \(50.0000/0.0500\) 未改
- [ ] 给出 diff 文件列表与 `rg` 检查结果
