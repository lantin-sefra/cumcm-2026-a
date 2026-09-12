"""交付编排入口（MODELING_REPORT §11 落盘清单）。

顺序：问题1 → 问题2/3（共用附录3连续主解）→ 问题4（χ=1主模型及χ=0交叉验证）
     → §9 验证与灵敏度（复用已算 P1/P3/P4 结果）→ figures/*.json 汇总。
⛔ 不绘图（图表阶段负责）；所有数值真算，不硬编码。
运行：python _utils/run_compute.py code/main.py
"""
from __future__ import annotations

import json

import numpy as np

import params as P
import problem1
import problem2
import problem3
import problem4
import master_p23
import validate


def _jsonable(x):
    """np 标量/数组 → 原生类型；NaN/inf → None（JSON 安全）。"""
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating, float)):
        xf = float(x)
        return xf if np.isfinite(xf) else None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    return x


def _write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_jsonable(obj), f, ensure_ascii=False, indent=2)


def main():
    P.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    P.FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    # ---- 问题1（附录2，1 s → 1800 s）----
    r1, s1 = problem1.solve(write=True)
    print(f"[P1] center_C@1800={s1['center_C_1800']:.4f} "
          f"mass_resid={s1['mass_resid_rel']:.2e}")

    # ---- 问题2/3（同一次从 t=0 至首达的连续积分）----
    r_master = master_p23.run_master()
    r2, s2 = problem2.solve(res=r_master, write=True)
    r3, s3 = problem3.solve(res=r_master, write=True)
    print(f"[P2] process_end={s2['process_end_h']:.3f}h rows_result2={s2['n_rows_result2']}")
    print(f"[P3] t_end={s3['t_end_h']:.3f}h maxC@end={s3['maxC_at_end']:.4f} "
          f"mass_resid={s3['mass_resid_rel']:.2e}")

    # ---- 问题4（附录4 + R(t)；χ=1主模型，χ=0仅交叉验证）----
    r4, s4 = problem4.solve(write=True)
    ei = s4["effect_isolation"]
    print(f"[P4] t_end(S2,χ=1)={s4['t_end_h']:.3f}h  net={ei['net_h']:+.3f}h "
          f"(换物性{ei['prop_swap_h']:+.3f} 加收缩{ei['shrink_h']:+.3f}) "
          f"χ闭合差={s4['chi_closure']['diff_rel']*100:+.2f}%")

    # ---- §9 验证 + §10 灵敏度（复用 P1/P3/P4）----
    validation, probes = validate.run_all(
        shared={"p1": r1, "p3": r3, "p4": r4, "p4_summary": s4})
    print(f"[VAL] all_pass={validation['all_pass']} "
          f"bessel_dev={validation['evidence_section9']['9_3_bessel_duhamel_P1']['max_dev_C']:.4f}℃ "
          f"K18={validation['constraints']['K18_moving_reduces_fixed']}")

    # ---- figures/*.json（下游论文阶段读取；含 logic_probes）----
    _write_json(P.FIGURE_DIR / "problem_1_results.json",
                {"problem": 1, "summary": s1})
    _write_json(P.FIGURE_DIR / "problem_2_results.json",
                {"problem": 2, "summary": s2})
    _write_json(P.FIGURE_DIR / "problem_3_results.json",
                {"problem": 3, "summary": s3})
    _write_json(P.FIGURE_DIR / "problem_4_results.json",
                {"problem": 4, "summary": s4})

    bounds_probes = [
        {"quantity": "t_end_hours_P4_chi1_primary", "claim": "upper",
         "probe_delta_sign": 0,
         "note": "§7.4 冻结半径使 t_end 偏上界方向；但 S2 在附件2数据范围内已达标，"
                 "冻结未触发(radius_frozen=False)，交付 t_end 不受冻结抬升，故探针符号=0(不绑定)"}
    ]
    all_results = {
        "problem": "2026-CUMCM-A-herb-drying",
        "delivery_grid": {
            "P1": {"N": P.N_P1_CV, "dt_s": P.DT_P1},
            "P2_P3": {"N": P.N_P23_CV, "dt_s": P.DT_P23,
                      "output_dt_s": P.P2_SAVE_DT_S},
            "P4": {"N": P.N_P4_CV, "dt_s": P.DT_P4}},
        "headline": {
            "P1_center_C_1800s": s1["center_C_1800"],
            "P3_t_end_h": s3["t_end_h"],
            "P4_t_end_h_chi1_primary": s4["t_end_h"],
            "P4_t_end_h_chi0_crosscheck": s4["chi_closure"]["S3_chi0_crosscheck_h"],
            "P4_chi_closure_uncertainty_rel": s4["chi_closure"]["diff_rel"],
            "effect_isolation_h": {
                "property_swap": ei["prop_swap_h"], "shrinkage": ei["shrink_h"],
                "net_P4_minus_P3": ei["net_h"]},
        },
        "validation_all_pass": validation["all_pass"],
        "radius_frozen": validation["radius_frozen"],
        "logic_probes": {"bounds": bounds_probes, "monotonic": probes},
    }
    _write_json(P.FIGURE_DIR / "all_results.json", all_results)

    print("[DONE] outputs in output/ and figures/. validation.json all_pass:",
          validation["all_pass"])
    return validation["all_pass"]


if __name__ == "__main__":
    ok = main()
    raise SystemExit(0 if ok else 1)
