# Codex 审阅报告复核（`codex/paper-revision-0913`）

复核对象：

- Codex 技术六条（上传稿 `codex_____1_5aec.md`）
- Codex「国赛评委终审」长评（上传稿 `codex___2_6388.md`）

复核基准提交：`dbd6640`（`codex/paper-revision-0913` 当前头）。
对照材料：`workspace/paper/sections/*.tex`、`workspace/paper/main.pdf`（87 页）、`workspace/code/{fvm,driver,params,problem4}.py`、`output/final_diagnostics/q3_sensitivity_final.csv`、附件 1、`workspace/AI工具使用详情.pdf`、`GITHUB协作指南.md`。

**总判断：技术条目绝大部分成立，且都不需要重跑求解器。合规与超页是另一类问题，不能靠改公式解决。**

---

## 1. 技术六条

| # | Codex 判断 | 本复核 | 是否要改 | 要不要重算 |
|---|---|---|---|---|
| 1 | \(N\) 定义为控制体数，但公式/代码是 \(N+1\) 个节点 | **成立** | 必须改文字 | 否 |
| 2 | \(b_i\ge|a_i|+|c_i|\) 却称「严格对角占优」 | **成立** | 必须改一个符号（或改称呼） | 否 |
| 3 | Q1 写成「单向弱耦合」，实际两场完全解耦 | **成立** | 必须改表述 | 否 |
| 4 | Q3 不确定性已写够，不必再加「不代表物理精度」 | **同意，可不改** | 不改 | 否 |
| 5 | 4 h 后 \(50^\circ\mathrm{C},0.05\) 被写成「规定平台值」 | **成立** | 必须改假设/正文；灵敏度数字已有 | 否 |
| 6 | 摘要「潜热偏短约一成」未交代 \(\lambda=2.4\times10^6\) J/kg | **成立** | 建议改摘要（删「约一成」或补条件） | 否 |

### 1.1 \(N\) 定义

符号表 `3b_symbols.tex`：`$N$ & 径向控制体数`。
公共模型 `4_common_model.tex` 第 137 行：「划分为 \(N\) 个控制体」，紧接着式 `(eq:cv)` 出现 \(V_0,\ldots,V_N\)。
`fvm.make_grid`：`xi = np.linspace(0.0, 1.0, N + 1)`，`Vt` 长度 `N+1`。`driver.CaseConfig.N` 注释仍写「控制体数」。

真实口径是 **\(N\) 个径向区间、\(N+1\) 个节点控制体（两端半宽）**。不是算错，是论文定义与代码不一致。

### 1.2 严格对角占优

`4_common_model.tex` 第 191 行：`$b_i\ge|a_i|+|c_i|$，即严格对角占优`。
`fvm.step_implicit` 对角有正时间项 `cap * Vt / dt`，扩散导纳左右对消后对角仍多出该正项，矩阵确实满足 **严格** 不等式。公式写弱了，结论方向对。

### 1.3 Q1 耦合类型

附录 2：\(\rho,c_p,k\) 常数，\(D=D(C)\) 不含 \(T\)。`5_problem1.tex` 式 `(eq:p1_heat)` 不含 \(C\)、`(eq:p1_mass)` 不含 \(T\)。
因此不是「温度先求、水分再取用温度」，而是 **完全解耦**（水分方程自身因 \(D(C)\) 非线性）。

当前不一致：

- `4_common_model.tex` 110–111 行、「水分场再取用其结果」——应改。
- `5_problem1.tex` 第 20 行「单向的弱联系」，下一句又写「这一解耦」——自相矛盾，应改。
- `2_analysis.tex` 47–48 行「两条边同时断开，温度场因而可以独立求解」——已经接近正确，可顺手改成「两场均可独立求解」。
- 摘要 `main.tex` 101–102 行「温度可独立求解，扩散系数仍随含水率逐点更新」——没有说水分用了温度，可不动或改成「两场均可独立求解」。

### 1.4 Q3 精度措辞

`9_validation.tex` / `10_evaluation.tex` / 摘要已写 \(D_0\pm20\%\Rightarrow-8.43\sim+12.76\) h 且为最强不确定度。不必再塞「四位小数不代表物理精度」。**同意 Codex：这条不改。**

### 1.5 4 h 平台「规定」

附件 1：241 点，末点 \(t=14400\) s，\(T=50.165^\circ\mathrm{C}\)，\(C_\mathrm{air}=0.04986\)。题目未写 4 h 后固定为 \(50,0.05\)。
末 30 点均值 \(T=50.0105^\circ\mathrm{C}\)、\(C=0.049982\)，与 SA4/SA5 一致：时长变化 \(-0.0333\%\)、\(-0.00063\%\)。

「规定」出现在：

- `3_assumptions.tex` 假设 (4)
- `4_common_model.tex` 第 62 行

`9_validation.tex` **没有**把 SA4/SA5 这两句写进正文（图里有「空气温度/含湿平台值」条，但评委读不到 \(0.033\%\)）。应改「规定」为「稳态外推」，并把现成灵敏度写进 §9。

### 1.6 潜热「约一成」

摘要 `main.tex` 125–126 行。正式 Q3 \(57.4716\) h，SA8 \(63.4189\) h，\(+5.947\) h（\(10.35\%\)）。
`params.LATENT_HEAT_PROBE = 2.4e6`。正文 `9_validation.tex` 80–84 行只说「加入潜热汇会延长、诊断不作为正式结果」，**未报 \(\lambda\)**。
`10_evaluation.tex` 只强调方向。数字不是编的，但摘要把有条件的诊断写成无条件结论。

更稳：摘要删「约一成」，只留「偏短」。若保留百分比，必须在 §9 写明 \(\lambda=2.4\times10^6\) J/kg 仅为量级探查。

---

## 2. 长评中其余内容问题

| 优先级（Codex） | 问题 | 本复核 | 处理 |
|---|---|---|---|
| P0 | 正文约 41 页 / 全文 87 页 | **成立**。`main.pdf` 87 页：p.1 摘要，p.2–42 正文（重述到评价），p.43 AI+参考文献，p.45 起附录 | 压页；属排版，不改求解 |
| P0 | 支撑 ZIP ~45 MiB | **本环境未见那份 ZIP**。仓库约 152 MiB；`paper/simkai.ttf` 等字体很大。需按终包实测 | 重新打包，不改求解 |
| P0 | AI 声明只写 Kimi，协作文件写 Cursor/Codex | **成立**。`AI工具使用详情.pdf` 仅 Kimi K3、排版/调试；并写「13章、26公式、29图、9表、20参考文献」（`references.bib` 实为 **19** 条）。`GITHUB协作指南.md` 写明队员 A Cursor / B·C Codex | 按真实使用改声明；删易过期统计 |
| P0 | 赛期用 GitHub 传赛题 | **文件层面成立**（指南写了私有仓库 pull/push）。是否违规由学校/组委会认定，此处只确认文本存在 | 停止继续用该渠道传题；声明与事实对齐 |
| P1 | \(\chi\) 不是链式法则直接推出 | **成立**。`8_problem4.tex` 33 行「把链式法则代入……得到」后直接出现 \((1-\chi)\)。后文 60–72 行的物理说明是对的，但推导句不连续 | 只改推导过渡，不重算 |
| P1 | 「质量守恒 \(10^{-14}\)」过强 | **成立**。`driver.py` 用 \(\xi\) 度量 `Vt`：`C0_tot=sum(Vt*C)`。这是变换后离散方程的全局平衡，不是物理水质量。摘要 125 行写「四问质量收支残差」；`9_validation.tex` 18–20 行已降为「先期诊断、非正式数据源」，两处口径打架 | 改摘要/§9 措辞；不重算 |
| P1 | 效应分解路径依赖 | **成立**。加和恒等式对 **这一条** \(S_0\to S_1\to S_2\) 路径成立；文中已写「构造使然」。但仍称「换物性 / 加收缩」像唯一分解。补 \(2\times2\) 要新算一条「附录3+收缩」 | 先改称呼；\(2\times2\) 可选 |
| P1 | S4 称「下界」 | **部分成立**。表 `tab:effect` 与第 203 行仍写「下界参照」；第 237 行图说已改成「理想化细半径参照」 | 统一用「细半径参照」 |
| P2 | 四位小数量级 | 与六条第 4 条相同 | 不改 |
| P3 | 「\(1/R\) 使表面通量增强」 | **成立，属措辞**。物理 Robin 仍是 \(h\Delta T\)；\(1/R\) 是 \(\partial_r=(1/R)\partial_\xi\)。同一 \(\xi\) 梯度对应更陡物理梯度，不是 \(h\) 变大 | 改一句 |

关于 \(\chi\)：后文已经区分材料随动 / Eulerian，正式数 \(51.0869\) vs \(52.6476\) h 也在。缺的是 **「代入链式法则 ⇒ \((1-\chi)\)」这一跳**。改过渡段即可，不必推翻现有两套计算结果。

---

## 3. 建议修改顺序（仍不重跑正式四问）

1. 合规与页数（声明、打包、压正文）。
2. 只改文字的技术硬伤：\(N\)、对角占优、Q1 解耦、平台「规定」、潜热「约一成」、质量残差降级、\(\chi\) 推导句、S4 下界、效应分解「沿该路径」。
3. 可选：§9 补 SA4/SA5 现成数字；若要做 \(2\times2\) 再开新算。

---

## 4. 若修改：文件位置与是否重编译

**一律不要重跑** `python -m code.main` / `problem1`–`problem4`。正式 `result1.xlsx`–`result4.xlsx` 不动。

### 4.1 只改 TeX → 必须重新编译论文

在 `workspace/paper/` 跑你们现用的 XeLaTeX 流程，更新 `workspace/paper/main.pdf`。

| 文件 | 改什么 |
|---|---|
| `workspace/paper/sections/3b_symbols.tex` | \(N\)：径向网格区间数 |
| `workspace/paper/sections/4_common_model.tex` | \(N\) 划分句；对角占优 \(\ge\to>\)；Q1「完全解耦」；「规定平台值」→外推 |
| `workspace/paper/sections/5_problem1.tex` | 「单向弱联系」→完全解耦 |
| `workspace/paper/sections/2_analysis.tex` | 附录2：两场均可独立求解（可选对齐） |
| `workspace/paper/sections/3_assumptions.tex` | 假设 (4) 去掉「规定」 |
| `workspace/paper/sections/8_problem4.tex` | \(\chi\) 推导过渡；\(1/R\) 一句；S4「下界」；效应分解「沿路径的顺序边际」 |
| `workspace/paper/sections/9_validation.tex` | 质量残差降级；补 SA4/SA5；潜热若保留「一成」则补 \(\lambda\) |
| `workspace/paper/sections/10_evaluation.tex` | 仅当摘要/局限仍写「约一成」时同步 |
| `workspace/paper/main.tex` | 摘要：质量残差、潜热「约一成」 |

**同步改、但不必重算：**

- `workspace/code/driver.py` 第 31 行注释「控制体数」→「径向区间数」（避免以后再写错）。
- `workspace/code/fvm.py` 文档字符串已写 `N+1`，可不动。

**不要改：** `result*.xlsx`、`q3_sensitivity_final.csv`、`q4_effect_isolation_final.csv`、`mass_consistency.csv`。

### 4.2 图：上述文字修改 **不必重出图**

现有灵敏度图已含「空气温度/含湿平台值」条。只有改图内标注时才重跑：

- `workspace/figures/gen_fig_q3_sensitivity.py` → `fig_q3_sensitivity.pdf`
- `workspace/figures/gen_fig_q4_shrink_effect.py` → `fig_q4_shrink_effect.pdf`（仅当改 S4 图注）

然后再次编译 `main.pdf`。

### 4.3 可选：补「附录3 + 收缩」做成 \(2\times2\)

这才需要新计算。

| 位置 | 动作 |
|---|---|
| `workspace/code/problem4.py` | 增情景（附录3 + `MovingGeometry`） |
| `workspace/output/final_diagnostics/q4_effect_isolation_final.csv` | 写入新 \(t_\mathrm{end}\) |
| `workspace/figures/gen_fig_q4_shrink_effect.py` + `fig_q4_shrink_effect.pdf` | 重画 |
| `workspace/paper/sections/8_problem4.tex` 表 `tab:effect` | 改表 |
| `workspace/paper/main.pdf` | 重编译 |

正式 \(\chi=1\) 主模型不必重跑，除非改的是求解核本身。

### 4.4 合规（非建模）

| 文件 | 动作 |
|---|---|
| `workspace/AI工具使用详情.pdf` | 按真实工具重写；删 13章/26公式/20文献 等统计 |
| `workspace/paper/sections/Z_ai_disclosure.tex` | 与详情 PDF 一致 |
| `GITHUB协作指南.md` | 提交包是否纳入，必须与声明一致 |
| 支撑材料 ZIP | 去掉字体、中间报告、`_figdata`、历史诊断等，实测 < 20 MB |
| 正文压页 | 图迁附录：优先 `fig_property_maps`、`fig_pipeline`、TikZ 模板、Q2 散点、Q3 ridgeline/rate、Q4 triptych/χ/mass_consistency |

---

## 5. 明确不采纳或降级的建议

- **不要**为「四位小数不代表物理精度」再加一段。题目要四位，§9 灵敏度已经说明主导误差来自 \(D_0\)。
- **不要**为改这 crit 去重跑 Q1–Q4 正式配置。
- **不要**删 \(\chi\) 或合并两套时长。缺的是推导句，不是计算结果。
- ZIP 体积、GitHub 是否已违规：本复核只确认仓库内文件与 PDF 页数；45 MiB 那份压缩包不在本工作区，需你们用终包再称一次。
