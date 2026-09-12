"""Q4 χ=1/χ=0 的空间与时间步收敛探针；只打印 JSON，不写交付文件。"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np

import geometry
import params as P
import problem4


def run_case(N: int, dt: float, chi: int) -> dict:
    geom = geometry.MovingGeometry()
    started = time.perf_counter()
    res = problem4._run(
        f"q4_N{N}_dt{dt:g}_chi{chi}", 4, geom, chi, P.T_END_MAX_S,
        N=N, dt_policy="const", dt_const=dt,
    )
    if not res["reached"]:
        raise RuntimeError(f"Q4 未在 {P.T_END_MAX_H:g} h 内达到阈值")

    C_end = res["end_C"] if res["end_C"] is not None else res["final_C"]
    imax = int(np.argmax(C_end))
    xi_max = imax / N
    R_end_m = res["end_R"] if res["end_R"] is not None else float(geom.R(res["t_end_s"]))
    return {
        "N": N,
        "dt_s": dt,
        "chi": chi,
        "t_end_s": float(res["t_end_s"]),
        "t_end_h": float(res["t_end_h"]),
        "R_end_cm": float(R_end_m / P.CM_TO_M),
        "C_center": float(C_end[0]),
        "C_surface": float(C_end[-1]),
        "max_C": float(C_end[imax]),
        "max_index": imax,
        "max_xi": float(xi_max),
        "max_r_cm": float(xi_max * R_end_m / P.CM_TO_M),
        "elapsed_s": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--N", type=int, required=True)
    parser.add_argument("--dt", type=float, required=True)
    parser.add_argument("--chi", type=int, choices=(0, 1), default=1)
    args = parser.parse_args()
    print(json.dumps(run_case(args.N, args.dt, args.chi), ensure_ascii=False))


if __name__ == "__main__":
    main()
