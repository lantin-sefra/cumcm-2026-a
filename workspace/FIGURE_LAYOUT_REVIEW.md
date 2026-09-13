# 图表排版优化审阅方案

审阅对象：`cursor/drop-redundant-figures-9caa`（已删图 10/16/18）上的 Codex「保守型 LaTeX 图表排版」提示词。
当前编译：`paper/main.pdf` 共 **85 页**。摘要第 1 页，正文约第 2–40 页，附录自第 43 页起。参考上限 30 页，正文仍大约超 10 页。

结论先讲：

> **Codex 的问题判断对，施工配方不能照单全收。**
> 页尾空白的主因是几乎所有图、表都用了 `[H]`：下一张表或图略高一点就整块跳页，上一页留下 200–330 pt 白边。
> 真正该做的是：给**结果图**松绑浮动，并加上 `flafter` 防止图跑到「见图」之前。
> **不要**把结果表改成 `longtable`，**不要**用 Codex 那组更保守的浮动比例覆盖现有设置，**第一轮不要缩图**。

| Codex 建议 | 本方案 | 理由 |
| --- | --- | --- |
| 非必要 `[H]` 改 `[!htbp]` | **部分改**：18 张结果图改；8 张方法图和 7 张结果表保留 `[H]` | 见表→表→解读不能拆；方法图必须贴着公式 |
| 一律可用 `[!htbp]` 的 `t` | 必须同时加 `flafter` | 否则图会顶到当页「见图 N」上面 |
| 长表改 `longtable` | **不做** | 结果表最多 10 行，已经能一页放下；符号表、文件清单已经是 `longtable` |
| 换成 Codex 的 top/text fraction | **不做** | 现有比例已经更激进，换过去会更难挤图 |
| 补浮动间距 10 pt | **做** | 导言区还没有 `textfloatsep` / `intextsep` |
| 个别图从 `1.00` 收到 `0.95/0.90` | **第一轮不做** | 结果图已经是 `0.90\textwidth`，再收到 0.88 只矮 4–8 pt，填不满 200 pt 白边 |

预估：只做浮动松绑，正文大约再收回 **2–4 页**。表造成的白边（第 14、18、23 页）会留下。到不了 30 页。

---

## 1. 空白是怎么来的

在已删三张图的 85 页 PDF 上，正文里明显稀疏的页是：

`9, 12, 14, 18, 21, 23, 24, 25, 29, 30, 34`（第 40 页是评价章收尾，不是图表问题）。

共同机制不是「图太大」，而是：

```
上文 +「见表/见图」→ [H] 图表略高于剩余高度 → 整块跳到下一页 → 本页留下三分之一白边
```

典型页：

- 第 14 页：表 1 放下后，表 2 差几十点上不来。
- 第 18 页：「见表 3 与表 4」停在页底，两表整组去第 19 页。
- 第 21 页：图 13 和解读写完，「见图 14」后面空一大块。
- 第 23 页：「见表 5」后面空一大块，表 5 在第 24 页。
- 第 25 页：图 15 和 8.3 节标题写完，图 16 整张跳走。
- 第 30 页：表 6 和解读写完，「见图 19」后面空一大块。

`[H]` 禁止后续正文回填这个洞。`[!htbp]` 的价值是：让**图后面的解说**抽回来填上一页，图自己去下一页顶。这只对「图后面还有足够正文」成立。

对「见表 1 与表 2」后面紧跟两张表的结构，把表改成浮动，会把**表后解读**抽到表前面。评委先看见数字解说、后看见表。结果表不能这样排。

---

## 2. 对 Codex 四条优先级的裁决

### 第一优先：`[H] → [!htbp]` — 有条件同意

同意松绑，但必须同时：

1. `\usepackage{flafter}`，禁止浮动体出现在源码位置之前。否则 `[t]` 会把图送到当页顶部，压在「见图 N」上面。Codex 第 9 节自己禁止这种漂移。
2. 保留 `\usepackage[section]{placeins}`，防止跨章。
3. 不要改所有 `[H]`。

**改成 `[!htbp]` 的 18 张结果图**

| 文件 | 标签 | 原因 |
| --- | --- | --- |
| `4_common_model.tex` | `fig:input_chamber` | 输入时程，后面有物性讨论可回填 |
| `5_problem1.tex` | `fig:q1_profiles` `fig:q1_center_surface` `fig:q1_validation` | 结果/校核图 |
| `6_problem2.tex` | `fig:q2_profiles` `fig:q2_spacetime` `fig:q12_contrast` `fig:q2_properties` | 第 21 页白边就是图 14 `[H]` 造成的 |
| `7_problem3.tex` | `fig:q3_drying_curve` `fig:q3_rate_curve` | 第 24、25 页白边 |
| `8_problem4.tex` | `fig:input_shrinkage` `fig:q4_moving_boundary` `fig:q4_triptych` `fig:q4_shrink_effect` `fig:chi_closure` `fig:q4_mass_consistency` | 第 30、34 页白边 |
| `9_validation.tex` | `fig:convergence` `fig:q3_sensitivity` | 普通验证图 |

**保留 `[H]` 的 8 张方法图**

这些图是「图本身就是这段推导的说明」，漂到下一小节会断读：

| 标签 | 紧贴的内容 |
| --- | --- |
| `fig:roadmap` | 四问依赖次序 |
| `fig:coupling_structure` | 双向耦合边 |
| `fig:property_maps` | 式 (6)(7)(8) 刚写完就对照 |
| `fig:cylinder_cv` | 三类控制体几何 |
| `fig:fv_stencil` | 两时间层模板 |
| `fig:pipeline` | Picard / 算子分裂流程 |
| `fig:landau_map` | Landau 变换几何 |
| `fig:effect_isolation` | `S0→S1→S2` 情景设计 |

**7 张结果表全部保留 `[H]`**

`tab:p1_T` `tab:p1_C` `tab:p2_T` `tab:p2_C` `tab:p3_C` `tab:p4_C` `tab:effect`

题目报表必须保持：见表 → 表 → 解读。第 14、18、23 页的白边是这个代价。用浮动去填，会把解读抽到表前，比留白更差。

若编译后表 1/表 2 仍是「差半行上不来」，允许只在这两张（以及同样成对的表 3/表 4）把 `\arraystretch` 从模板默认略收到 `0.95`。这是第二轮、且只动高度，不改数据、不改字号。

### 第二优先：长表 `longtable` — 否决

正文结果表行数：

| 表 | 数据行 | 一页能否放下 |
| --- | --- | --- |
| 表 1 / 表 2 | 7 | 能，已经单独成页过 |
| 表 3 / 表 4 | 6 | 能 |
| 表 5 | 10 | 能，整表在第 24 页 |
| 表 6 | 9 | 能，整表在第 30 页 |
| 表 7 | 5 | 能 |

它们跳页是因为 `[H]` 碰上页尾剩余高度不够，不是表本身超过一页。改成 `longtable` 会让 7–10 行的正式结果表从中间撕开，观感更差。

已经是 `longtable` 的不要动：

- `3b_symbols.tex` 符号表（还用了 `\addtocounter{table}{-1}` 避免占表号）
- `A_code.tex` 文件清单

`longtable` 宏包 cls 已加载，不要再 `\usepackage{longtable}`。

### 第三优先：浮动间距 — 同意补，不同意改比例

`main.tex` 已有：

```tex
\renewcommand{\topfraction}{0.92}
\renewcommand{\bottomfraction}{0.9}
\renewcommand{\textfraction}{0.06}
\renewcommand{\floatpagefraction}{0.72}
\setcounter{topnumber}{3}
\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{4}
```

Codex 草稿里的 `0.90 / 0.80 / 0.10 / 0.75` 比现在更保守：`textfraction` 从 0.06 提到 0.10，等于要求一页留下更多文字，图更难上去。覆盖现有设置是退步。

缺的是间距。默认 `\textfloatsep` 大约 20 pt。允许加上：

```tex
\setlength{\textfloatsep}{10pt plus 2pt minus 2pt}
\setlength{\floatsep}{8pt plus 2pt minus 2pt}
\setlength{\intextsep}{10pt plus 2pt minus 2pt}
```

不要收到 6 pt。不要重复定义 fraction。

### 第四优先：缩图 — 第一轮不做

结果图已经是 `width=0.9\textwidth,height=0.8\textheight,keepaspectratio`。绑定约束是宽度。`0.90 → 0.88` 只矮大约 4–8 pt，填不满 200–330 pt 的页尾洞。

少数本来就不是通栏的（`tikz_landau_map` 0.80、`tikz_cylinder_cv` 0.86）不要再收。

`fig:q1_validation` 最高（约 0.80 高宽比，0.90 栏宽时约 326 pt）。若第一轮浮动之后它仍然单独造成一页大空白，再单独收到 `0.88\textwidth`。不要先改。

---

## 3. 修改操作（按文件）

只允许改浮动参数、`\includegraphics` 的 width/height（本轮不改）、表格环境类型（本轮不改）、以及为此必需的宏包。不改正文句子、公式、题注、数据。

### 3.1 `paper/main.tex`

在已有宏包区、`float` 已由 cls 加载之后增加：

```tex
\usepackage{flafter}
```

在现有 `MH-FLOAT-TUNE` 块里**只追加**三行间距，不改现有 `\topfraction` 等：

```tex
\setlength{\textfloatsep}{10pt plus 2pt minus 2pt}
\setlength{\floatsep}{8pt plus 2pt minus 2pt}
\setlength{\intextsep}{10pt plus 2pt minus 2pt}
```

不要删 `\usepackage[section]{placeins}`。

### 3.2 把指定图的 `[H]` 改成 `[!htbp]`

只改 `\begin{figure}[H]` 这一处，caption / label / `\includegraphics` 不动。

```
4_common_model.tex
  改：fig:input_chamber
  留：fig:property_maps, fig:cylinder_cv, fig:fv_stencil, fig:pipeline

5_problem1.tex
  改：fig:q1_profiles, fig:q1_center_surface, fig:q1_validation
  留：tab:p1_T, tab:p1_C

6_problem2.tex
  改：fig:q2_profiles, fig:q2_spacetime, fig:q12_contrast, fig:q2_properties
  留：tab:p2_T, tab:p2_C

7_problem3.tex
  改：fig:q3_drying_curve, fig:q3_rate_curve
  留：tab:p3_C

8_problem4.tex
  改：fig:input_shrinkage, fig:q4_moving_boundary, fig:q4_triptych,
      fig:q4_shrink_effect, fig:chi_closure, fig:q4_mass_consistency
  留：fig:landau_map, fig:effect_isolation, tab:p4_C, tab:effect

9_validation.tex
  改：fig:convergence, fig:q3_sensitivity

2_analysis.tex
  全部保留 [H]
```

合计：`[H] → [!htbp]` **18** 处；保留 `[H]` **8 图 + 7 表**。

### 3.3 明确不做

- 不改任何 `table` 为 `longtable`
- 不改 `\includegraphics` 的 width/height
- 不改表格列宽、数据、`\small`
- 不改正文、公式、题注
- 不删图、不删表
- 不改 `figures/` 和 Python
- 不手工重编号

### 3.4 编译后才允许的第二轮（本方案默认不预做）

完整编译后，只处理「仍然稀疏、且能指出是哪一张图刚好超高」的个案：

1. 某张结果图仍造成整页大空白：该图 `0.90\textwidth` → `0.88\textwidth`，`keepaspectratio` 不变。同类图尽量一起改，避免一章里忽大忽小。
2. 表 1 与表 2（或表 3 与表 4）仍然「差半行」：只对这些表 `\renewcommand{\arraystretch}{0.95}`，编译后对照可读性，变挤就撤。
3. 某张改成 `[!htbp]` 的图跑到下一小节或出现在引用句之前：只把**这一张**改回 `[H]`，不要全局回滚。

若某项省了页但明显难看，撤该项。观感优先于页数。

---

## 4. 编译检查清单

改完后在完整稿上串行 `xelatex → bibtex → xelatex → xelatex`，核对：

1. 正文页数（现在约 2–40 页 / 总 85 页）
2. 第 21、24、25、30、34 页的页尾白边是否明显变短
3. 第 14、18、23 页允许仍然偏空（表保留 `[H]`）
4. 没有任何图出现在首次 `\ref` / 「见图」之前
5. 没有任何图跨到下一章（`placeins` 仍在）
6. 方法图仍紧跟对应公式
7. 图号连续，无 undefined reference
8. 无新空白页、无图文重叠、无越界
9. 未改任何正式数字

---

## 5. 对 Codex 施工提示词的修订

可以当底稿，但必须改这五处，否则会误伤：

1. 不要写「普通结果图和普通短表都优先 `[!htbp]`」。短结果表保留 `[H]`。
2. 增加强制：`\usepackage{flafter}`。
3. 删掉「把长表改 longtable」整节，或改成「本文没有需要跨页的结果表」。
4. 删掉用 Codex 那组 fraction 覆盖 `MH-FLOAT-TUNE` 的段落。只允许补间距。
5. 缩图改成「第一轮禁止；编译后仍有单图超高再动，且不低于 `0.88\textwidth`」。

修订后的施工范围：

```
允许修改：
  paper/main.tex          （只加 flafter 与三行间距）
  paper/sections/4_common_model.tex
  paper/sections/5_problem1.tex
  paper/sections/6_problem2.tex
  paper/sections/7_problem3.tex
  paper/sections/8_problem4.tex
  paper/sections/9_validation.tex
  以上文件中指定 figure 的 [H] → [!htbp]

禁止：
  改正文句子与公式
  改 caption / 数据 / 图源 / 代码
  改 table 环境类型
  改 includegraphics 尺寸（第一轮）
  覆盖已有 topfraction 等
  删图删表
```

---

## 6. 页数预期

| 动作 | 大约回收 | 对 30 页上限 |
| --- | --- | --- |
| 已删图 10/16/18 | 已发生，约 2 页（87→85） | 仍超 |
| 本方案第一轮（18 张图浮动 + 间距） | 约 2–4 页 | 正文大约仍 36–38 页 |
| 表造成的白边 | 0（有意保留） | — |
| 第一轮后再缩 1–2 张图 | 小于 0.5 页 | 可忽略 |

页数主因仍是图多、评价章重复，不是「再收 2% 图宽」。排版优化值得做，但不要指望它单独压到 30 页。
