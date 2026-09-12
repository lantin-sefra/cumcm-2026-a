# 项目地图 — 2026 CUMCM A 题「药材的烘干问题」

本仓库是 MHAgent「导出全部」工作区。赛题原件只保留在 `workspace/user_data/`（已删除顶层 `_Prob` 副本）。

**论文标题**：药材热风烘干过程的热-质耦合模型与收缩域烘干时长预测

**物理对象**：圆柱形药材（L = 25 cm，R₀ = 2 cm）热风烘干；一维径向热–质耦合非线性抛物方程组。四问递进：常物性预热 → 变物性全程 → 达标时长 → 收缩域移动边界。

运行代码必须在 `workspace/` 下，不要 `cd` 进 `code/`：

```text
cd workspace
python code/main.py
```

---

## 顶层

```
├── workspace/             # 项目工作区
├── README_STRUCT.md       # 本文件：项目结构
├── README.md              # 导出说明与运行方式
├── manifest.json          # 导出清单
└── workspace/             # 全部工作产物
```

---

## `workspace/` 总览

```
workspace/
├── user_data/             # 官方赛题（PDF、附件、OCR）
├── code/                  # 数值求解
├── paper/                 # CUMCM 论文（main.tex / 已编译 main.pdf）
├── figures/               # 绘图脚本与图
├── output/                # 四问交付表与验证结果
├── _utils/                # plot_utils.py
├── _tmp/                  # 编译/审校中间文件（勿当交付物）
├── AI工具使用详情.pdf
└── 流水线报告（md / json）
```

`_problem_file.txt` 指向 `user_data/A题.pdf`。

---

## 赛题数据 `workspace/user_data/`

代码读附件路径见 `code/params.py`：`user_data/附件/附件/`。

```
user_data/
├── A题.pdf
├── A题_extracted.txt          # OCR 题面
├── 附件.zip
└── 附件/附件/
    ├── 附件1.xlsx             # 烘房温湿时程，241 行
    ├── 附件2.xlsx             # 半径收缩 R(t)，145 行
    └── 附件3/                 # 提交模板
        ├── result1.xlsx
        ├── result2.xlsx
        ├── result3.xlsx
        └── result4.xlsx
```

---

## 代码 `workspace/code/`

入口 `main.py`：P1 → P2/P3 共用 master → P4 → §9 验证。无 `requirements.txt`。常量只放 `params.py`。

| 文件 | 职责 |
|---|---|
| `main.py` | 交付编排入口 |
| `driver.py` | 时间推进（Picard 耦合、达标判据） |
| `fvm.py` | 柱坐标有限体积 + Landau 对流项 |
| `params.py` | 几何 / 物性 / 阈值 / 路径 |
| `props.py` | 附录 2/3/4 物性 |
| `geometry.py` | 附件 2 半径 PCHIP 插值 |
| `ambient.py` | 附件 1 环境时程插值 |
| `problem1.py` … `problem4.py` | 四问求解与落盘 |
| `master_p23.py` | 问题 2/3 共用全程计算 |
| `validate.py` | 网格 / 时间步 / Bessel 对照 / 质量守恒 |
| `io_out.py` | xlsx / csv 写出 |
| `data_check.py` / `template_check.py` | 附件与模板核对 |

方法：全隐式 FVM、表面 Robin、轴心对称零通量、保序算子分裂。

---

## 论文 `workspace/paper/`

```
paper/
├── main.tex / main.pdf
├── cumcmthesis.cls
├── references.bib              # 19 条
├── simkai.ttf / simsun.ttc
└── sections/
    ├── 1_restatement.tex
    ├── 2_analysis.tex
    ├── 3_assumptions.tex
    ├── 3b_symbols.tex
    ├── 4_common_model.tex
    ├── 5_problem1.tex … 8_problem4.tex
    ├── 9_validation.tex
    ├── 10_evaluation.tex
    ├── A_code.tex
    └── Z_ai_disclosure.tex
```

---

## 交付 `workspace/output/`

| 文件 | 内容 |
|---|---|
| `result1.xlsx` … `result4.xlsx` | 四问完整网格（result2 约 20 万行） |
| `table1_2_problem1.csv` … `table6_problem4.csv` | 论文摘要表 |
| `validation.json` | §9 可信度，`all_pass=true` |
| `sensitivity.csv` | 灵敏度 SA1–SA10 |
| `effect_isolation.csv` | 问题 4 效应隔离 |
| `mass_consistency.csv` | 收缩域干物质守恒诊断 |

---

## 图表 `workspace/figures/`

- `gen_fig_*.py` → `fig_*.pdf`（时空场、干燥曲线、灵敏度、收缩等）
- TikZ：`tikz_cylinder_cv` / `tikz_fv_stencil` / `tikz_landau_map` / `tikz_effect_isolation`
- HTML 结构图：`fig_pipeline` / `fig_roadmap` / `fig_coupling_structure`
- 摘要：`problem_{1–4}_results.json`、`all_results.json`
- 预计算：`_figdata/*.npz`

公共样式在 `_figcommon.py`，插图 TeX 片段在 `latex_includes.tex`。

---

## 流水线报告（`workspace/` 根下）

| 阶段 | 文件 |
|---|---|
| 审题 | `PROBLEM_ANALYSIS.md`、`PROBLEM_FACTS.json`、`DATA_FACTS.json` |
| 建模 | `MODELING_REPORT.md`、`PARAMS_RAW.md`、`CROSS_PROBLEM_LEDGER.json` |
| 计算 | `RESULTS.md`、`DELIVERABLES.json`、`CAPABILITY_*.json` |
| 作图 | `FIGURES_REPORT.md`、`FIGURES_HTML_REPORT.md` |
| 论文 | `PAPER_REPORT.md`、`COMPILE_REPORT.md`、`PAPER_DATA_CHECKLIST.md` |
| 评审 | `COMP_REVIEW.md`、`AUDIT_REPORT.md` |

事实来源优先级：题面 `user_data/A题_extracted.txt` → `PROBLEM_FACTS.json` / `DATA_FACTS.json` → `MODELING_REPORT.md` → 代码 `params.py` → `output/` 真算结果。正文数字应与 JSON / `RESULTS.md` 一致，不要手改计算结果。

---

## 关键数值（已写入论文摘要）

- 问题 1（1800 s）：中心 33.577 ℃ / 2.5500 kg/kg；表面 36.786 ℃ / 1.511 kg/kg
- 问题 2（3 h）：中心含水率 1.766 kg/kg（热先于质）
- 问题 3：烘干时长 56.706 h
- 问题 4：收缩后时长 52.190 h，末态半径 1.20 cm
- 质量收支残差 ≤ 1.6×10⁻¹⁴；能力验收非 delivery 项均为 PASS
