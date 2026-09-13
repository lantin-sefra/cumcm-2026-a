# 论文数据真实性核对清单（数据原料）

**模式**: PDF
**JSON 源**: all_results.json, problem_1_results.json, problem_2_results.json, problem_3_results.json, problem_4_results.json
**JSON 数据条目**: 266

---

## 自检步骤（请你按以下顺序执行）

**重要原则**：本工作区的实验/分析阶段已经把所有真实数据存到 `figures/*.json`，
并由 paper-figure 步骤渲染成 `figures/TABLE_*.tex|md`。
**论文数据应能追溯到这些文件或题设，并允许有明确计算依据的派生量、单位换算及舍入。未直接匹配不等于编造。**

### 第 1 步：识别论文中的「数据性数字」

打开你的论文文件，逐章扫描：

- ✅ **需要核对的**：表格里的所有单元格数字、正文里引用实验结果的数字（如 "RMSE 达到 0.023"、"准确率 94%"、"最优解 295.83"、"R² 为 0.94"）
- ⏭️ **不需要核对的**（叙述里自然出现的数字）：
    - 章节编号、列号、引用 [1][2,3]、图编号「图 3-1」
    - 年份「2024 年」、日期「3 月 5 日」
    - 公式中的常数（在 `$...$` 或 `$$...$$` 内）
    - 算法描述里的步骤数「分 5 步」
    - 文献综述里别人论文的数字

### 第 2 步：对每个「数据性数字」核对

对照下方的 JSON 数据清单和 TABLE 文件全文：

1. **能在数据清单/TABLE 文件里找到完全一致的数字** → ✅ 真实，跳过
2. **数据清单里有但论文写错了**（如 RMSE 真实是 0.023，论文写的 0.999） → 改正文，**禁止反向操作**（禁止改 JSON）
3. **数据清单里没有这个数字** → 两种可能：
   - **AI 编造**（最常见）→ 删除该说法或从清单中找正确数据补充
   - **从其他来源算出来的合理派生量**（如百分比 = 子集/总数 ×100）→ 检查派生公式是否合理

### 第 3 步：表格优先用预生成的 TABLE 文件

如果论文里手抄了表格内容，**优先改成** `\input{figures/TABLE_*.tex}` 引入（已经从 JSON 渲染好，不会出错）。

### 第 4 步：自检完成后登记独立回执

后置自检使用本轮任务指定的 `.mh/quality/data-review-ack-*.txt` 和确认值；不要将确认值写入论文。
如果本轮写作上下文仍明确要求兼容旧注释，必须在最终编译之前完成；编译之后不得为登记状态再次改源码。
没有本轮确认值时不要复制旧回执或自行编造；系统只接受与当前内容绑定的有效核对。

**判断原则**：
- 以 JSON 为准修论文，禁止反向修 JSON
- 不必把 JSON 中的每个数字都搬到论文里——只关心论文里出现的数字是否真实
- 不确定某个数字是不是数据 → 当成数据核对一遍，确认能找到来源就行

---

## 图表来源与论断对应（并入本次核对，不启动额外模型轮次）

数字出现过不等于支持当前论断。逐图核对数据所属问题、场景、参数、样本量和统计量；
跨问题引用允许，但必须解释可迁移的结论。一个概率水平的收敛曲线不能直接证明另一个临界点可靠。
下面仅列静态识别的真实文件引用，不代表已经验证数学结论；动态路径请按生成脚本补查。

| 图 | 生成脚本 | 可观察的数据来源 |
|---|---|---|
| fig_chi_closure | figures/gen_fig_chi_closure.py | 动态来源，需按脚本定位 |
| fig_convergence | figures/gen_fig_convergence.py | 动态来源，需按脚本定位 |
| fig_input_chamber | figures/gen_fig_input_chamber.py | 动态来源，需按脚本定位 |
| fig_input_shrinkage | figures/gen_fig_input_shrinkage.py | 动态来源，需按脚本定位 |
| fig_property_maps | figures/gen_fig_property_maps.py | 动态来源，需按脚本定位 |
| fig_q12_contrast | figures/gen_fig_q12_contrast.py | 动态来源，需按脚本定位 |
| fig_q1_center_surface | figures/gen_fig_q1_center_surface.py | 动态来源，需按脚本定位 |
| fig_q1_profiles | figures/gen_fig_q1_profiles.py | 动态来源，需按脚本定位 |
| fig_q1_spacetime | figures/gen_fig_q1_spacetime.py | 动态来源，需按脚本定位 |
| fig_q1_validation | figures/gen_fig_q1_validation.py | 动态来源，需按脚本定位 |
| fig_q2_coupling_scatter | figures/gen_fig_q2_coupling_scatter.py | 动态来源，需按脚本定位 |
| fig_q2_profiles | figures/gen_fig_q2_profiles.py | 动态来源，需按脚本定位 |
| fig_q2_properties | figures/gen_fig_q2_properties.py | 动态来源，需按脚本定位 |
| fig_q2_spacetime | figures/gen_fig_q2_spacetime.py | 动态来源，需按脚本定位 |
| fig_q3_drying_curve | figures/gen_fig_q3_drying_curve.py | 动态来源，需按脚本定位 |
| fig_q3_rate_curve | figures/gen_fig_q3_rate_curve.py | 动态来源，需按脚本定位 |
| fig_q3_ridgeline | figures/gen_fig_q3_ridgeline.py | 动态来源，需按脚本定位 |
| fig_q3_sensitivity | figures/gen_fig_q3_sensitivity.py | 动态来源，需按脚本定位 |
| fig_q4_mass_consistency | figures/gen_fig_q4_mass_consistency.py | 动态来源，需按脚本定位 |
| fig_q4_moving_boundary | figures/gen_fig_q4_moving_boundary.py | 动态来源，需按脚本定位 |
| fig_q4_shrink_effect | figures/gen_fig_q4_shrink_effect.py | 动态来源，需按脚本定位 |
| fig_q4_triptych | figures/gen_fig_q4_triptych.py | 动态来源，需按脚本定位 |

## JSON 真实数据清单

### `all_results.json`（39 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | `2026-CUMCM-A-herb-drying` |
| `delivery_grid.N` | 40 |
| `delivery_grid.dt_P1_s` | 1 |
| `delivery_grid.dt_P234` | `seg(2->4)s` |
| `headline.P1_center_C_1800s` | 2.54999 |
| `headline.P3_t_end_h` | 56.7063 |
| `headline.P4_t_end_h_chi0_primary` | 52.1896 |
| `headline.P4_t_end_h_chi1_alt` | 50.694 |
| `headline.P4_chi_closure_uncertainty_rel` | -0.0286573 |
| `headline.effect_isolation_h.property_swap` | 71.885 |
| `headline.effect_isolation_h.shrinkage` | -76.4041 |
| `headline.effect_isolation_h.net_P4_minus_P3` | -4.51913 |
| `validation_all_pass` | True |
| `radius_frozen` | False |
| `logic_probes.bounds[0].quantity` | `t_end_hours_P4_chi0_primary` |
| `logic_probes.bounds[0].claim` | `upper` |
| `logic_probes.bounds[0].probe_delta_sign` | 0 |
| `logic_probes.bounds[0].note` | `§7.4 冻结半径使 t_end 偏上界方向；但 S2 达标 52.19h < 附件2 数据 72h，冻结未触...` |
| `logic_probes.monotonic[0].of` | `t_end` |
| `logic_probes.monotonic[0].wrt` | `hm` |
| `logic_probes.monotonic[0].more` | `hm` |
| `logic_probes.monotonic[0].then` | `t_end` |
| `logic_probes.monotonic[0].observed_sign` | -1 |
| `logic_probes.monotonic[0].expect_sign` | -1 |
| `logic_probes.monotonic[0].expect_dir` | `better` |
| `logic_probes.monotonic[1].of` | `t_end` |
| `logic_probes.monotonic[1].wrt` | `D_prefactor` |
| `logic_probes.monotonic[1].more` | `D_prefactor` |
| `logic_probes.monotonic[1].then` | `t_end` |
| `logic_probes.monotonic[1].observed_sign` | -1 |
| `logic_probes.monotonic[1].expect_sign` | -1 |
| `logic_probes.monotonic[1].expect_dir` | `better` |
| `logic_probes.monotonic[2].of` | `t_end` |
| `logic_probes.monotonic[2].wrt` | `C_th` |
| `logic_probes.monotonic[2].more` | `C_th` |
| `logic_probes.monotonic[2].then` | `t_end` |
| `logic_probes.monotonic[2].observed_sign` | -1 |
| `logic_probes.monotonic[2].expect_sign` | -1 |
| `logic_probes.monotonic[2].expect_dir` | `better` |

### `problem_1_results.json`（67 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 1 |
| `summary.problem` | 1 |
| `summary.appendix` | 2 |
| `summary.N` | 40 |
| `summary.dt_s` | 1 |
| `summary.chi` | `n.a.(fixed)` |
| `summary.center_T_1800` | 33.5765 |
| `summary.center_C_1800` | 2.54999 |
| `summary.surface_T_1800` | 36.7862 |
| `summary.surface_C_1800` | 1.51076 |
| `summary.mass_resid_rel` | 7.413e-16 |
| `summary.resid_step_max` | 6.815e-16 |
| `summary.picard_iters_max` | 3 |
| `summary.picard_nonconv` | 0 |
| `summary.floor_trunc_steps` | 0 |
| `summary.table1_T[0][0]` | 28.0001 |
| `summary.table1_T[0][1]` | 28.0004 |
| `summary.table1_T[0][2]` | 28.0043 |
| `summary.table1_T[0][3]` | 28.0332 |
| `summary.table1_T[0][4]` | 28.1803 |
| `summary.table1_T[1][0]` | 28.0416 |
| `summary.table1_T[1][1]` | 28.0643 |
| `summary.table1_T[1][2]` | 28.1523 |
| `summary.table1_T[1][3]` | 28.369 |
| `summary.table1_T[1][4]` | 28.8493 |
| `summary.table1_T[2][0]` | 28.455 |
| `summary.table1_T[2][1]` | 28.5377 |
| `summary.table1_T[2][2]` | 28.8054 |
| `summary.table1_T[2][3]` | 29.317 |
| `summary.table1_T[2][4]` | 30.1659 |
| `summary.table1_T[6][0]` | 33.5765 |
| `summary.table1_T[6][1]` | 33.7731 |
| `summary.table1_T[6][2]` | 34.3652 |
| `summary.table1_T[6][3]` | 35.363 |
| `summary.table1_T[6][4]` | 36.7862 |
| `summary.table1_T[...]` | `<3 项省略>` |
| `summary.table2_C[0][0]` | 2.55 |
| `summary.table2_C[0][1]` | 2.55 |
| `summary.table2_C[0][2]` | 2.55 |
| `summary.table2_C[0][3]` | 2.55 |
| `summary.table2_C[0][4]` | 2.2555 |
| `summary.table2_C[1][0]` | 2.55 |
| `summary.table2_C[1][1]` | 2.55 |
| `summary.table2_C[1][2]` | 2.55 |
| `summary.table2_C[1][3]` | 2.549 |
| `summary.table2_C[1][4]` | 2.0545 |
| `summary.table2_C[2][0]` | 2.55 |
| `summary.table2_C[2][1]` | 2.55 |
| `summary.table2_C[2][2]` | 2.55 |
| `summary.table2_C[2][3]` | 2.5349 |
| `summary.table2_C[2][4]` | 1.8789 |
| `summary.table2_C[6][0]` | 2.55 |
| `summary.table2_C[6][1]` | 2.5497 |
| `summary.table2_C[6][2]` | 2.5381 |
| `summary.table2_C[6][3]` | 2.3757 |
| `summary.table2_C[6][4]` | 1.5108 |
| `summary.table2_C[...]` | `<3 项省略>` |
| `summary.report_times_s[0]` | 100 |
| `summary.report_times_s[1]` | 300 |
| `summary.report_times_s[2]` | 600 |
| `summary.report_times_s[6]` | 1800 |
| `summary.report_times_s[...]` | `<3 项省略>` |
| `summary.report_radii_cm[0]` | 0 |
| `summary.report_radii_cm[1]` | 0.5 |
| `summary.report_radii_cm[2]` | 1 |
| `summary.report_radii_cm[3]` | 1.5 |
| `summary.report_radii_cm[4]` | 2 |

### `problem_2_results.json`（65 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 2 |
| `summary.problem` | 2 |
| `summary.appendix` | 3 |
| `summary.N` | 40 |
| `summary.dt_s` | 1 |
| `summary.chi` | `n.a.(fixed)` |
| `summary.report_window_h` | 3 |
| `summary.process_end_h` | 56.7063 |
| `summary.mass_resid_rel` | 1.551e-14 |
| `summary.picard_iters_max` | 3 |
| `summary.picard_nonconv` | 0 |
| `summary.floor_trunc_steps` | 0 |
| `summary.table3_T[0][0]` | 32.1908 |
| `summary.table3_T[0][1]` | 32.3836 |
| `summary.table3_T[0][2]` | 32.9673 |
| `summary.table3_T[0][3]` | 33.962 |
| `summary.table3_T[0][4]` | 35.4141 |
| `summary.table3_T[1][0]` | 40.3817 |
| `summary.table3_T[1][1]` | 40.5536 |
| `summary.table3_T[1][2]` | 41.0606 |
| `summary.table3_T[1][3]` | 41.8785 |
| `summary.table3_T[1][4]` | 42.998 |
| `summary.table3_T[2][0]` | 45.8462 |
| `summary.table3_T[2][1]` | 45.9343 |
| `summary.table3_T[2][2]` | 46.1925 |
| `summary.table3_T[2][3]` | 46.6047 |
| `summary.table3_T[2][4]` | 47.1398 |
| `summary.table3_T[5][0]` | 49.8495 |
| `summary.table3_T[5][1]` | 49.8553 |
| `summary.table3_T[5][2]` | 49.8745 |
| `summary.table3_T[5][3]` | 49.9101 |
| `summary.table3_T[5][4]` | 49.9664 |
| `summary.table3_T[...]` | `<2 项省略>` |
| `summary.table4_C[0][0]` | 2.5499 |
| `summary.table4_C[0][1]` | 2.5488 |
| `summary.table4_C[0][2]` | 2.5254 |
| `summary.table4_C[0][3]` | 2.326 |
| `summary.table4_C[0][4]` | 1.6486 |
| `summary.table4_C[1][0]` | 2.5255 |
| `summary.table4_C[1][1]` | 2.4946 |
| `summary.table4_C[1][2]` | 2.3578 |
| `summary.table4_C[1][3]` | 2.0231 |
| `summary.table4_C[1][4]` | 1.471 |
| `summary.table4_C[2][0]` | 2.3859 |
| `summary.table4_C[2][1]` | 2.3255 |
| `summary.table4_C[2][2]` | 2.1344 |
| `summary.table4_C[2][3]` | 1.802 |
| `summary.table4_C[2][4]` | 1.3475 |
| `summary.table4_C[5][0]` | 1.7662 |
| `summary.table4_C[5][1]` | 1.7166 |
| `summary.table4_C[5][2]` | 1.5702 |
| `summary.table4_C[5][3]` | 1.3332 |
| `summary.table4_C[5][4]` | 1.008 |
| `summary.table4_C[...]` | `<2 项省略>` |
| `summary.report_times_h[0]` | 0.5 |
| `summary.report_times_h[1]` | 1 |
| `summary.report_times_h[2]` | 1.5 |
| `summary.report_times_h[5]` | 3 |
| `summary.report_times_h[...]` | `<2 项省略>` |
| `summary.report_radii_cm[0]` | 0 |
| `summary.report_radii_cm[1]` | 0.5 |
| `summary.report_radii_cm[2]` | 1 |
| `summary.report_radii_cm[3]` | 1.5 |
| `summary.report_radii_cm[4]` | 2 |
| `summary.n_rows_result2` | 204143 |

### `problem_3_results.json`（49 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 3 |
| `summary.problem` | 3 |
| `summary.appendix` | 3 |
| `summary.N` | 40 |
| `summary.dt_s` | 1 |
| `summary.chi` | `n.a.(fixed)` |
| `summary.t_end_h` | 56.7063 |
| `summary.t_end_s` | 2.041e+05 |
| `summary.maxC_at_end` | 0.15 |
| `summary.mass_resid_rel` | 1.551e-14 |
| `summary.picard_iters_max` | 3 |
| `summary.picard_nonconv` | 0 |
| `summary.floor_trunc_steps` | 0 |
| `summary.table5_C[0][0]` | 1.0156 |
| `summary.table5_C[0][1]` | 0.9869 |
| `summary.table5_C[0][2]` | 0.9006 |
| `summary.table5_C[0][3]` | 0.7546 |
| `summary.table5_C[0][4]` | 0.5334 |
| `summary.table5_C[1][0]` | 0.4548 |
| `summary.table5_C[1][1]` | 0.4419 |
| `summary.table5_C[1][2]` | 0.402 |
| `summary.table5_C[1][3]` | 0.329 |
| `summary.table5_C[1][4]` | 0.1641 |
| `summary.table5_C[2][0]` | 0.2979 |
| `summary.table5_C[2][1]` | 0.2906 |
| `summary.table5_C[2][2]` | 0.2678 |
| `summary.table5_C[2][3]` | 0.2244 |
| `summary.table5_C[2][4]` | 0.0847 |
| `summary.table5_C[8][0]` | 0.153 |
| `summary.table5_C[8][1]` | 0.1506 |
| `summary.table5_C[8][2]` | 0.1427 |
| `summary.table5_C[8][3]` | 0.1266 |
| `summary.table5_C[8][4]` | 0.0528 |
| `summary.table5_C[...]` | `<5 项省略>` |
| `summary.table5_end_row_C[0]` | 0.15 |
| `summary.table5_end_row_C[1]` | 0.1476 |
| `summary.table5_end_row_C[2]` | 0.14 |
| `summary.table5_end_row_C[3]` | 0.1244 |
| `summary.table5_end_row_C[4]` | 0.0525 |
| `summary.report_times_h[0]` | 6 |
| `summary.report_times_h[1]` | 12 |
| `summary.report_times_h[2]` | 18 |
| `summary.report_times_h[8]` | 54 |
| `summary.report_times_h[...]` | `<5 项省略>` |
| `summary.report_radii_cm[0]` | 0 |
| `summary.report_radii_cm[1]` | 0.5 |
| `summary.report_radii_cm[2]` | 1 |
| `summary.report_radii_cm[3]` | 1.5 |
| `summary.report_radii_cm[4]` | 2 |

### `problem_4_results.json`（46 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 4 |
| `summary.problem` | 4 |
| `summary.appendix` | 4 |
| `summary.N` | 40 |
| `summary.dt_s` | `seg(2→4)` |
| `summary.chi_primary` | 0 |
| `summary.t_end_h` | 52.1896 |
| `summary.t_end_s` | 1.879e+05 |
| `summary.t_end_label` | `S2 χ=0, N=40, Δt=seg(2→4)s → t_end=52.190 h` |
| `summary.maxC_at_end` | 0.150012 |
| `summary.radius_frozen` | False |
| `summary.R_at_end_cm` | 1.2 |
| `summary.mass_resid_rel` | 7.515e-16 |
| `summary.picard_iters_max` | 3 |
| `summary.picard_nonconv` | 0 |
| `summary.floor_trunc_steps` | 0 |
| `summary.effect_isolation.t_S0_h` | 56.7087 |
| `summary.effect_isolation.t_S1_h` | 128.594 |
| `summary.effect_isolation.t_S2_h` | 52.1896 |
| `summary.effect_isolation.t_S3_h` | 50.694 |
| `summary.effect_isolation.t_S4_h` | 47.4146 |
| `summary.effect_isolation.prop_swap_h` | 71.885 |
| `summary.effect_isolation.shrink_h` | -76.4041 |
| `summary.effect_isolation.net_h` | -4.51913 |
| `summary.effect_isolation.identity_lhs` | -4.51913 |
| `summary.effect_isolation.identity_rhs` | -4.51913 |
| `summary.effect_isolation.identity_resid_h` | 7.105e-15 |
| `summary.chi_closure.S2_chi0_h` | 52.1896 |
| `summary.chi_closure.S3_chi1_h` | 50.694 |
| `summary.chi_closure.diff_h` | -1.49561 |
| `summary.chi_closure.diff_rel` | -0.0286573 |
| `summary.inc1.ratio_actual` | 2.4131 |
| `summary.inc1.ratio_required` | 2.78706 |
| `summary.inc1.rel_diff` | 0.134178 |
| `summary.inc1.R_consistent_cm` | 1.28749 |
| `summary.inc1.R_measured_end_cm` | 1.198 |
| `summary.report_times_h[0]` | 6 |
| `summary.report_times_h[1]` | 12 |
| `summary.report_times_h[2]` | 18 |
| `summary.report_times_h[7]` | 48 |
| `summary.report_times_h[...]` | `<4 项省略>` |
| `summary.report_radii_cm[0]` | 0 |
| `summary.report_radii_cm[1]` | 0.5 |
| `summary.report_radii_cm[2]` | 1 |
| `summary.report_radii_cm[3]` | 1.5 |
| `summary.report_radii_cm[4]` | 2 |
