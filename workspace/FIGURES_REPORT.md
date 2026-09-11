# 数据图交付报告（nature-figure，步骤 4/8）

赛题：2026 CUMCM A 题「药材的烘干问题」
交付物：`figures/*.pdf`（22 张）+ `figures/latex_includes.tex`（必需产物）+ 本报告

## 一、交付清单

22 张 DATA 图全部落盘为矢量 PDF，一图一脚本（`figures/gen_fig_<name>.py`），共享底座
`figures/_figcommon.py`（不以 `gen_fig` 开头，只被 import，不单独出图）。

| # | 图名 | 面板 | 图型 | 来源 |
|---|---|---|---|---|
| 1 | fig_input_chamber | single | 双轴图 | 附件1 |
| 2 | fig_input_shrinkage | single | 折线+渐变填充 | 附件2 |
| 3 | fig_q1_profiles | 2 | 多面板径向剖面 | 问题1 |
| 4 | fig_q1_spacetime | 2 | Hovmöller | 问题1 |
| 5 | fig_q1_center_surface | single | 双轴图 | 问题1 |
| 6 | fig_q1_validation | 4 | 残差诊断四合一 | 验证 |
| 7 | fig_q2_profiles | 2 | 多面板径向剖面 | 问题2 |
| 8 | fig_q2_spacetime | 2 | Hovmöller | 问题2 |
| 9 | fig_q2_properties | single | 平行坐标 | 附录3 |
| 10 | fig_q2_coupling_scatter | single | 散点+KDE | 问题2 |
| 11 | fig_q12_contrast | 2 | 背靠背柱状 | 问题1+2 |
| 12 | fig_q3_drying_curve | single | 折线+渐变填充 | 问题3 |
| 13 | fig_q3_rate_curve | 2 | 面积图 | 问题3 |
| 14 | fig_q3_ridgeline | single | 山脊图 | 问题3 |
| 15 | fig_q3_sensitivity | single | 龙卷风图 | 灵敏度 |
| 16 | fig_q4_moving_boundary | single | 等高线 | 问题4 |
| 17 | fig_q4_triptych | 3 | 三联图 | 问题4 |
| 18 | fig_q4_shrink_effect | 2 | 发散柱状 | 效应隔离 |
| 19 | fig_q4_mass_consistency | 2 | 配对点图 | INC1 诊断 |
| 20 | fig_chi_closure | single | 双线对比 | S2/S3 |
| 21 | fig_convergence | 2 | 收敛性折线 | validation.json |
| 22 | fig_property_maps | 2 | 双面板热力图 | 附录3/4 |

DRAWIO（3）、TIKZ（4）、GPTIMG（1）不属本步骤，由后续步骤产出。

## 二、门禁结果

两道阻塞门禁均通过，视觉 QC 22 张全 PASS：

- `bash _utils/figure_check.sh` → **exit 0**，0 违规 + 0 可升级 + 0 配方问题；
  图内标注体检 24 个脚本全过。
- `_utils/figure_pdf_quality_check.py figures` → **exit 0**，
  「字体嵌入、最终印刷字号、文字边界、留白和对比度检查通过」。
- 步骤 3.5 视觉 QC（`MH_DATA_FIG_VISION=1`）：**22/22 PASS**。
  该检查器按 PNG 逐图调用（`data_fig_vision_check.py <image.png>`），
  而 LaTeX 模式只出 PDF，故先用 PyMuPDF 按 200 dpi 渲成临时 PNG 再送检。

**这一轮门禁的可信度比上一轮高一个量级，原因是修掉了一个使门禁形同虚设的缺陷。**
matplotlib 默认往 PDF 里嵌 Type 3 字体，而 Type 3 的中文字形没有 ToUnicode 映射 ——
实测从改前的 PDF 里 `get_text()` 提取到 **0 个汉字**。也就是说 PDF 体检脚本此前只查过
数字与拉丁字符，**全部中文标签的重叠、字号、边界、对比度一项都没被检查过**。
在 `_figcommon.py` 里改嵌 TrueType（`pdf.fonttype = 42`）后中文可提取、可搜索，
体检才真正覆盖中文。改完立刻暴露出一个真实缺陷：`fig_q1_validation` 的
「相对偏差」超出页面边界 3.1 pt —— 这个缺陷一直存在，只是被 Type 3 藏住了。

中文仍有一处结构性盲区：**相邻 CJK 刻度标签在 PDF 里会并成同一个文本行**，
而相撞判据比较的是两个文本行的 bbox，因此 CJK 之间的重叠原理上测不到。
本轮改为用 `get_text('rawdict')` 取逐字符 bbox 直接量，测出并修掉 4 处真实重叠
（见第五节第 6 条）。

## 三、口径与风格

- LaTeX 模式：只出矢量 PDF，不产 PNG 副本；网格/分层填充底图 `rasterized=True`
  （实测嵌入 350 dpi，高于 300 dpi 下限），等值线、坐标轴与全部文字仍是矢量。
- PDF 字体嵌 TrueType（`pdf.fonttype = 42`），中文可提取、可搜索、可复制。
- 取色全部经 `nature_palette()`，无 hex 字面量（白色底衬除外，属背景而非配色）。
- 图内中文，仅符号/SI 单位保留拉丁字母；结论性文字一律写进 `latex_includes.tex` 的 caption。
- `setup_style(palette='nature')` 全篇一次；每张图建好后立即 `set_paper_placement`；
  `layout='constrained'` + GridSpec，未混用 `tight_layout`/`subplots_adjust`。
- 插图宽度统一 `0.90\textwidth`（22 张长宽比同属 ≤0.80 档，显示缩放 0.914）。

## 四、caption 数值复核

`latex_includes.tex` 的每一处数值都对着 `figures/_figdata/*.npz`、`output/*.json`、
`output/*.csv` 逐条核过。查出并改正 5 处事实错误：

| 图 | 原文错误 | 实测值 |
|---|---|---|
| fig_q2_properties | 引用了问题 2 的物性区间，且称 $\rho$ 与 $D$ 反向 | 24 箱均值：$C$ 2.5285→0.1309，$\rho$ 973.7→666.8，$c_p$ 3411→1765，$k$ 0.4823→0.2538，四项同向下降 |
| fig_input_chamber | 平台自 0.67 h 起 | 49 ℃ 在 1.367 h，50.0 ℃ 在 2.183 h，峰值 50.246 ℃ 在 2.95 h |
| fig_q3_rate_curve | 峰值在升温段末 | 峰值 0.6899 kg/(kg·h) 在 $t=0$，此后单调衰减 |
| fig_q1_profiles / fig_q1_spacetime | 中心降幅「不足 $10^{-5}$」；变化限于 $r\gtrsim1.8$ cm | 中心 $\Delta C=1.006\times10^{-5}$；$r=1.5$ cm 处 0.174，$r=0.7$ cm 处 $<1.5\times10^{-3}$ |
| fig_q12_contrast | 中心相差「三个量级（0 对 $1\times10^{-4}$）」 | 中心 $1.0\times10^{-5}$ 对 $7.9\times10^{-5}$，约一个量级；表面 $r=2$ cm 处符号反转（1.039 对 0.901） |

其余 17 张的 caption 数值经核对与真算一致，包括：$t_{end}$ 各口径
（P3 56.709 h、P4-S2 52.190 h、P4-S3 50.694 h、S1 128.594 h）、
加性分解 $+71.885/-76.404/-4.519$ h 与残差 $7.11\times10^{-15}$、
$\chi$ 闭合差 $-1.496$ h（$-2.87\%$）、$N$=40 vs 80 相对变化 $0.458\%$、
质量残差 $10^{-15}$ 量级、INC1 的 $2.4131$ vs $2.7871$（13.42%）与 1.1980 vs 1.2875 cm、
$D_3\in[3.35\times10^{-10},1.35\times10^{-8}]$、$D_4\in[1.59\times10^{-10},2.50\times10^{-9}]$、
比值 $0.186$–$0.476$、耦合散点 14801 个节点、半解析偏差 $\le1.97$ mK。

## 五、遗留事项与环境限制

**1. 视觉 QC 已完成，22/22 PASS。** 早前一次判定「接口不可用（HTTP 502 → `NO_VISION_API`）」
是错的：502 是瞬时故障，重试即通；真正的调用失败原因是 `READ_FAIL: cannot read image` ——
检查器只吃 PNG，而 LaTeX 模式不产 PNG。改为先渲临时 PNG 再送检后，全部 22 张送检。
首轮扫图报出 5 张有问题，逐张按 PDF 实测复核：**3 张确有真实缺陷已修，2 张是模型误报**。

| 图 | 模型报告 | 实测复核 | 处理 |
|---|---|---|---|
| fig_q2_properties | 平行坐标的轴量程标签相撞 | 真实：`0.254–0.482` 与 `5.7e-10–1.16e-08` 只隔 0.61 pt；`1.77e+03–3.41e+03` 与下一条重叠 2.3 pt | 量程端点改标到各轴两端（平行坐标常规做法），刻度只留符号与单位；相邻间距 25–47 pt |
| fig_q3_sensitivity | `-25.0 h` 压住 y 刻度；图例盖住末几行小柱 | 真实：读数 x 区间 170.7–218.2 与刻度 34.7–178.3 重叠 7.6 pt | 读数移到该行零轴右侧空白；图例移出数据区 |
| fig_convergence | y 轴标签被裁；`判据 1%%` 双百分号 | 双百分号真实（普通字符串里的 `%%` 不会被转义）；y 标签未出界，但高 217 pt、逼到顶缘 3.9 pt | 改单 `%`；口径说明移入 caption |
| fig_q3_ridgeline | 左右脊线处次刻度连成黑带 | 真实：主轴 65 个次刻度、间距 5.4 pt / 长 1.5 pt；副轴 30 个 | y 轴（基线序，次刻度无意义）关次刻度 |
| fig_q4_mass_consistency | 注释越过 y 轴脊线、右端被截断 | **误报**：注释 x 区间 69.9–168.8，面板左脊约 33 pt、右缘约 245 pt，两端都在轴内 | 未按报告改；但无量纲量的单位位原写作末尾一个「—」，读起来像截断残字，已留空 |
| fig_q1_spacetime | (b) 深色区一片竖向「梳齿」条纹，压住等值线 | 真实：181×21 网格在 PDF 里是 3801 个独立填充路径（整图 7742 个），相邻格元间留发丝缝 | 底图 `rasterized=True`（350 dpi 图像层，等值线/文字仍矢量，路径数 7742→140）；色标暗端截断使黑等值线在高值区可见 |

同一条接缝缺陷对所有网格/分层填充图成立，因此同步修了 `fig_q2_spacetime`
与 `fig_q4_moving_boundary`（`fig_property_maps` 原本已 `rasterized=True`）。
修完 6 张重新送检全部 PASS。

**2. `recipe_audit` 对 fig_q1_center_surface 的告警是工具假阳性，不阻塞。**
审计要求该图出现 `3d`/`plot_surface`。原因是它把关键词表匹配到含图名自身的描述串上，
而图名里的 `center_surface` 命中了 `surface` 关键词。规划图型是双轴图 (basic #10)，
代码用 `twinx` 实现，规划与产物一致，未作改动。

**3. `figure_check.sh` 报 4 个 MISSING 属预期。**
`fig_coupling_structure`、`fig_pipeline`、`fig_roadmap`（DRAWIO）与 `fig_scene`（GPTIMG）
是其他步骤的交付物，本步骤只负责 DATA。

**4. 已同步规划文档一处口径。** `MODELING_REPORT.md` 的 delta 表原将 `fig_convergence`
的数据来源写作 $e_T,e_C$ 的网格/时间步收敛，但该内容已由 `fig_q1_validation` 的 (c)(d)
承担；交付图实际画 $t_{end}(N)$ 与相对质量残差。已改表述使规划=产物。

**5. 时空图的等值线标注改法（对比度）。** Hovmöller 图的 inline `clabel` 只掏空等值线本身，
字仍坐在热力图底色上，落到色标暗端时对比度实测仅 1.x:1；加白底衬需要约 3 倍字高的补丁，
印刷观感笨重。最终改为等值线只留线、层级读数移到色标刻度（白底区），
既消除对比度风险也不遮挡场值，两张图的 caption 已相应说明。

**6. 为可读性缩短的图内文字，完整口径都在 caption 里。** 逐字符实测出 4 处 CJK 重叠
（相撞门禁看不到，理由见第二节），按"图内只留短锚点、解释进 caption"处理：

| 图 | 原文 | 实测 | 改为 |
|---|---|---|---|
| fig_q4_shrink_effect | `换物性`/`加收缩`/`净差` | 三个标签并成一个 71.8 pt 的文本行 | `物性`/`收缩`/`净差`，间距 4.66 pt |
| fig_q4_mass_consistency | `干物质表观密度比`/`末态半径` | 重叠 −13.11 pt；8 字标签顶到画布左缘（x=0.46 pt） | 刻度压到 `干物质密度比`/`末态半径`，读数移到配对点右侧；完整口径 $\rho_s(C_{th})/\rho_s(C_0)$ 写进 caption |
| fig_convergence | y 标签并入`附录3 / 固定半径` | 旋转后高 217 pt（画布 237.6 pt），逼到顶缘 3.9 pt | 轴标签只留量名与单位，求解口径进 caption |
| fig_q3_sensitivity | 图内`基准 56.18 h` | 顶部图例让位后行距变窄，该注释越出第 0 行行带 | 基准读数并入 x 轴标签 |

**7. `shared_legend` 与落盘期字号放大的冲突（已绕开，值得后续注意）。**
`shared_legend` 提交图例车道时会 `set_layout_engine('none')` 冻结轴位，
而落盘阶段的 `_ensure_final_print_font` 会把字号抬到最终印刷字号 —— 版面引擎已冻结，
撑宽的标签无法重排。`fig_q3_sensitivity` 的中文 y 刻度标签很长
（`表面边界条件改 Dirichlet` 等），实测 y 轴标签被挤到 x=−4.4 pt（出界）。
改用 constrained layout 自己的外置图例槽位（`loc='outside upper center'`）后版面引擎保持在线，
可随字号重排。**结论：图例需要独立车道、同时侧标签又很长时，优先用外置槽位而非 `shared_legend`。**

## 六、本轮复核（运行时重新部署后的重跑）

本轮开始时 `_utils/` 被重新部署（manifest 版本
`68fae6f4c774…`，落盘时间 09:45），**晚于全部 22 张 PDF 的生成时间（08:53–09:38）**。
也就是说仓库里的 PDF 是用另一份 `plot_utils.py` 产出的，未经证实能在当前运行时复现。
同时 `_tmp/` 下的视觉 QC 账本随之丢失，缓存全部失效。因此本轮不是"确认上轮结论"，
而是**在当前运行时下重跑一遍出图与三道门禁**：

- 22 个 `gen_fig_*.py` 全部重跑，**0 个失败**，PDF 全部重新落盘。
- `bash _utils/figure_check.sh` → **exit 0**（0 违规 + 0 可升级 + 0 配方问题）。
- `_utils/figure_pdf_quality_check.py figures` → **exit 0**。
- 视觉 QC 按新字节重新送检 **22/22 PASS**（旧 PASS 记录按 SHA-256 判定已失效，未复用）。

### 本轮修掉的真实缺陷：fig_q4_triptych 阈值标注压线

视觉 QC 报出 (a) 面板的 `0.15 kg/kg` 与 $y=0.15$ 的点线重叠、且紧贴左脊线。
按 PDF 实测复核**确认是真缺陷**，并查清了成因 —— 不是标注位置写错，而是**写了一个放不下的位置**：

脚本把它放在 `xytext=(1.30, 0.40)`（收缩域外的空白带，本身选点合理），但
`0.15 kg/kg` 渲染宽约 51.7 pt ≈ **1.17 个数据单位**，从 $x=1.30$ 起排会越过
`xlim=2.05` 溢出到 (b) 面板。`save_fig` 的解重叠因此把它挪走，落点是左下角
（实测终位 `anncoords='axes fraction'`、`(0.002, −0.006)`），而那里正好被阈值点线横穿。
探针见 `_tmp/probe_ann.py`：标注在 `annotate` 与 `shared_legend` 之后仍是 `data (1.3, 0.4)`，
**只有 `save_fig` 之后变成 axes-fraction 左下角**，定位到位移发生在落盘期。

改法按 SKILL「解释图上元素 → 走图例」：删掉该 `annotate`，把阈值线的身份交给
`axhline(..., label='达标阈值 0.15 kg/kg')`（只在 (a) 挂 label，避免三个面板产生重复图例项），
`shared_legend` 由 `ncol=5` 改 `ncol=6`。实测图例单行占 x 60.6–451.7 pt，
在 460.8 pt 画布内不溢出；图内不再有该标注，压线消失，重新送检 PASS。

**这条对其他图也成立：图内标注选点必须连"文字渲染宽度放不放得下"一起算。**
只看空白区在不在，会得到一个必然被落盘期解重叠搬走的位置，而搬到哪里不受控。

### 规划=产物 已对齐

`PROBLEM_ANALYSIS.md` 的 FIGURE_MANIFEST 原记 DATA=19，实际交付 22 张，
多出的 `fig_chi_closure`、`fig_convergence`、`fig_property_maps` 三张均有真算数据源
（分别为 S2/S3 闭合对照、`validation.json` 网格收敛、附录 3/4 物性公式），
属真实证据而非冗余，故**补进 manifest 而不是删图**；总数改为 DATA=22 / ALL=29。
同时改正 `fig_q4_triptych` 的面板数（原记 single，实为 3-panel）。

对账口径需注意：manifest 是**管道表**，而 SKILL 第 5 步的 awk 只认
`- fig_xxx` 列表式，对本文件提取结果为空、恒报"跳过对账"。本轮改按 `|` 分隔取
DATA 行的图名列对账，结果规划 19 张**全部命中**、缺失 0。

### 环境差异一处

视觉检查器本轮以 `_utils/data_fig_vision_check.pyc`（字节码）形式部署，
而 SKILL 第 3.5 步的 `$DFV` 查找表只列 `.py` 路径，按原样会找不到检查器而整段跳过。
Python 可直接执行 `.pyc`，故本轮改为指向该 `.pyc`，**未替换或改写检查器**。
另有 1 次 `fig_q4_moving_boundary` 的 `Vision API error: read timed out`，重试即通，属瞬时故障。

### caption 复核（本轮抽验）

`figures/latex_includes.tex` 22 个 `figure` 环境、22 个 `\caption`、22 个 `\label`，
全部 `[H]`，引用图名与落盘 PDF **1:1 无悬挂**。抽验 `fig_q4_triptych` 的
"末态半径 1.200 cm""(c) 触及阈值线"：实测 `R_end=1.200` cm、末态剖面
`max C=0.1500`（阈值 0.15），与 caption 一致。
