# 2026 数学建模 A 题（药材烘干）

三人协作请先看 [GITHUB协作指南.md](GITHUB协作指南.md)。仓库为私有，比赛期间不要公开。

工作目录是 `workspace/`，不要 `cd` 进 `code/`。

## 1. 正式论文

`workspace/paper/main.pdf`

## 2. 正式计算结果

- `workspace/output/result1.xlsx`
- `workspace/output/result2.xlsx`（问题二前 3 h：1～10800 s）
- `workspace/output/result3.xlsx`
- `workspace/output/result4.xlsx`

## 3. 正式最终诊断

`workspace/output/final_diagnostics/`

- `q3_sensitivity_final.csv`
- `q4_effect_isolation_final.csv`
- `q4_chi0_timeseries.csv`
- `q4_chi0_summary.csv`

## 4. 历史诊断（不要当终稿）

`workspace/output/legacy/` 保存早期粗网格 / 旧 χ 关系诊断：

- `validation.json`
- `sensitivity.csv`
- `effect_isolation.csv`

仅供追溯，**不代表最终论文结果**。不要用 legacy 替代 `final_diagnostics`。

`workspace/` 根下的 `RESULTS.md`、`MODELING_REPORT.md` 等流水线报告也是早期记录，数字可能过时。

## 5. 正式计算配置

| 问题 | 配置 |
|---|---|
| Q1 | N=160，dt=0.125 s |
| Q2 / Q3 | N=2560，dt=0.25 s |
| Q4 | N=1280，dt=0.25 s，χ=1 |

对应正式口径：

- Q1 1800 s：中心 33.5755 ℃，表面 36.7856 ℃
- Q2 3 h：49.8495 ℃，49.9664 ℃，1.7662，1.0081
- Q3：57.4716 h
- Q4（χ=1 正式）：51.0869 h，R=1.2000 cm
- Q4（χ=0 交叉验证）：52.6476 h；差 1.5607 h（3.0550%）
- 4 h 后环境长期平台：50.0000 ℃，0.0500 kg/kg

## 6. χ 关系

- **χ=1**：材料随动 ALE，正式主模型（相对对流项抵消）
- **χ=0**：Eulerian/Landau 交叉验证（保留相对对流项）

## 7. 提醒

- 正式图在 `workspace/figures/fig_*.pdf`。下列脚本已接到 `result*.xlsx` / `final_diagnostics/`，可以重跑：`gen_fig_q4_shrink_effect.py`、`gen_fig_chi_closure.py`、`gen_fig_q3_sensitivity.py`、`gen_fig_q2_properties.py`。
- 不要重跑 `figures/prep_figdata.py`，不要重跑 Q1–Q4。
- `code/validate.py` 是 LEGACY DIAGNOSTIC，不会随正式 `main.py` 自动执行。
- 项目结构细节见 [README_STRUCT.md](README_STRUCT.md)。
