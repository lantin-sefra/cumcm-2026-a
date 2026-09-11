"""为 22 张数据图准备真实数值场（复用 code/ 的交付求解器，不新造模型、不硬编码）。

产出 figures/_figdata/*.npz：
  p1.npz        问题1（附录2，1800 s，10 s 快照）温度/浓度全场 + 半解析 Duhamel 参照
  p2.npz        问题2（附录3，0-3 h，30 s 快照）温度/浓度全场
  p3.npz        问题3（附录3，全程至 t_end，60 s 快照）温度/浓度 + maxC + 体平均
  p4s2.npz      问题4 主用 S2（附录4 + R(t)，χ=0）节点场 + R(t)
  p4s3.npz      问题4 对照 S3（χ=1）maxC 时程
  conv.npz      网格/时间步收敛扫描（附录2，1800 s 终态场对参照解偏差）
  inputs.npz    附件1 环境时序（241 行）、附件2 半径时序（145 行，含单调化）
⛔ 本脚本不属于出图脚本（文件名不以 gen_fig 开头），只做一次性数值准备。
"""
from __future__ import annotations

import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, 'code')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import params as P            # noqa: E402
import geometry               # noqa: E402
import ambient as AMB         # noqa: E402
import props as PR            # noqa: E402
import driver as D            # noqa: E402
import validate as VAL        # noqa: E402

OUT = os.path.join(ROOT, 'figures', '_figdata')
os.makedirs(OUT, exist_ok=True)


def _log(msg):
    print('[prep] %s' % msg, flush=True)


def _vol_mean(nodes, N):
    """ξ 度量下的体平均（柱坐标 2πξ 权重，与 fvm.make_grid 一致）。"""
    import fvm
    xi, dxi, Vt = fvm.make_grid(N)
    w = Vt / np.sum(Vt)
    return nodes @ w


def run_p1():
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name='P1', appendix=2, geom=g, dt_policy='p1',
                       save_dt_s=10.0, t_max_s=P.P1_SAVE_DURATION_S,
                       detect_end=False, store_nodes=True)
    res = D.run(cfg)
    # 半解析参照（式29 阶跃响应 + 分段线性 Duhamel），中心/表面时程 + 1800 s 剖面
    alpha = P.APP2_K / (P.APP2_RHO * P.APP2_CP)
    Bi = P.H_CONV * P.R0_M / P.APP2_K
    lam = VAL.bessel_roots(Bi, P.BESSEL_ROOTS)
    amb = AMB.Ambient()
    r_cols_m = np.asarray(P.DIST_COLS_CM) * P.CM_TO_M
    t_ana = res['t'][1:]                                   # t=0 无 Duhamel 段
    ana_center = np.array([VAL.analytic_T_p1(0.0, tt, alpha, P.R0_M, Bi, lam,
                                             P.T0_C, amb) for tt in t_ana])
    ana_surf = np.array([VAL.analytic_T_p1(P.R0_M, tt, alpha, P.R0_M, Bi, lam,
                                           P.T0_C, amb) for tt in t_ana])
    ana_prof = np.array([VAL.analytic_T_p1(r, P.P1_SAVE_DURATION_S, alpha, P.R0_M,
                                           Bi, lam, P.T0_C, amb) for r in r_cols_m])
    np.savez_compressed(
        os.path.join(OUT, 'p1.npz'),
        t=res['t'], cols_cm=np.asarray(P.DIST_COLS_CM),
        Tcol=res['Tcol'], Ccol=res['Ccol'],
        Tcenter=res['Tcenter'], Ccenter=res['Ccenter'],
        Tsurf=res['Tsurf'], Csurf=res['Csurf'],
        T_air=amb.T_air(res['t']), C_air=amb.C_air(res['t']),
        t_ana=t_ana, ana_center=ana_center, ana_surf=ana_surf,
        ana_prof_1800=ana_prof, num_prof_1800=res['Tcol'][-1],
        mass_resid_rel=res['mass_resid_rel'],
        picard_max=res['picard_iters_max'])
    _log('p1 done: nt=%d  T_c@1800=%.4f  dev_center_max=%.2e℃'
         % (res['t'].size, res['Tcenter'][-1],
            np.max(np.abs(res['Tcenter'][1:] - ana_center))))


def run_p2():
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name='P2', appendix=3, geom=g, dt_policy='seg',
                       save_dt_s=30.0, t_max_s=3.0 * P.SEC_PER_HOUR,
                       detect_end=False, store_nodes=True)
    res = D.run(cfg)
    N = res['N']
    Cbar = _vol_mean(res['nodesC'], N)
    # 实现值物性（附录3）逐快照×节点
    rho, cp, k, Dc = PR.props(3, res['nodesC'], res['nodesT'])
    np.savez_compressed(
        os.path.join(OUT, 'p2.npz'),
        t=res['t'], cols_cm=np.asarray(P.DIST_COLS_CM),
        Tcol=res['Tcol'], Ccol=res['Ccol'],
        Tcenter=res['Tcenter'], Ccenter=res['Ccenter'],
        Tsurf=res['Tsurf'], Csurf=res['Csurf'], Cbar=Cbar,
        nodesC=res['nodesC'], nodesT=res['nodesT'],
        rho=rho, cp=cp, k=k, D=Dc,
        mass_resid_rel=res['mass_resid_rel'])
    _log('p2 done: nt=%d  T_c@3h=%.4f  C_c@3h=%.4f'
         % (res['t'].size, res['Tcenter'][-1], res['Ccenter'][-1]))


def run_p3():
    g = geometry.FixedGeometry(P.R0_M)
    cfg = D.CaseConfig(name='P3', appendix=3, geom=g, dt_policy='seg',
                       save_dt_s=P.P34_SAVE_DT_S, t_max_s=P.T_END_MAX_S,
                       detect_end=True, store_nodes=True)
    res = D.run(cfg)
    N = res['N']
    Cbar = _vol_mean(res['nodesC'], N)
    rho, cp, k, Dc = PR.props(3, res['nodesC'], res['nodesT'])
    np.savez_compressed(
        os.path.join(OUT, 'p3.npz'),
        t=res['t'], cols_cm=np.asarray(P.DIST_COLS_CM),
        Tcol=res['Tcol'], Ccol=res['Ccol'], maxC=res['maxC'],
        Tcenter=res['Tcenter'], Ccenter=res['Ccenter'],
        Tsurf=res['Tsurf'], Csurf=res['Csurf'], Cbar=Cbar,
        nodesC=res['nodesC'], nodesT=res['nodesT'],
        D=Dc, rho=rho, cp=cp, k=k,
        t_end_s=res['t_end_s'], t_end_h=res['t_end_h'],
        mass_resid_rel=res['mass_resid_rel'])
    _log('p3 done: nt=%d  t_end=%.4f h' % (res['t'].size, res['t_end_h']))


def run_p4():
    for name, chi, tag in (('S2', P.CHI_PRIMARY, 'p4s2'), ('S3', P.CHI_ALT, 'p4s3')):
        geom = geometry.MovingGeometry()
        cfg = D.CaseConfig(name=name, appendix=4, geom=geom, chi=chi,
                           dt_policy='seg', save_dt_s=P.P34_SAVE_DT_S,
                           t_max_s=P.T_END_MAX_S, detect_end=True,
                           store_nodes=(tag == 'p4s2'))
        res = D.run(cfg)
        payload = dict(t=res['t'], maxC=res['maxC'], R_m=res['R'],
                       Ccenter=res['Ccenter'], Csurf=res['Csurf'],
                       Tcenter=res['Tcenter'], Tsurf=res['Tsurf'],
                       cols_cm=np.asarray(P.DIST_COLS_CM),
                       Ccol=res['Ccol'], Tcol=res['Tcol'],
                       t_end_s=res['t_end_s'], t_end_h=res['t_end_h'],
                       mass_resid_rel=res['mass_resid_rel'])
        if tag == 'p4s2':
            payload['nodesC'] = res['nodesC']
            payload['nodesT'] = res['nodesT']
            payload['Cbar'] = _vol_mean(res['nodesC'], res['N'])
            payload['N'] = res['N']
        np.savez_compressed(os.path.join(OUT, '%s.npz' % tag), **payload)
        _log('p4 %s done: nt=%d  t_end=%.4f h  R_end=%.4f cm'
             % (name, res['t'].size, res['t_end_h'], res['R'][-1] / P.CM_TO_M))


def run_conv():
    """网格/时间步收敛扫描（附录2，1800 s 终态 21 列场对参照解的相对偏差 式28）。"""
    def fields(N, dt):
        g = geometry.FixedGeometry(P.R0_M)
        cfg = D.CaseConfig(name='c%d_%g' % (N, dt), appendix=2, geom=g, N=N,
                           dt_policy='const', dt_const=dt,
                           save_dt_s=P.P1_SAVE_DURATION_S,
                           t_max_s=P.P1_SAVE_DURATION_S, detect_end=False)
        r = D.run(cfg)
        return r['Tcol'][-1], r['Ccol'][-1]

    Tref, Cref = fields(P.REF_N_CV, P.REF_DT_S)
    Ts = max(np.max(np.abs(Tref)), 1.0)
    Cs = max(np.max(np.abs(Cref)), P.C_TH)

    Ns = np.array([10, 20, 40, 80])
    eT_N, eC_N = [], []
    for N in Ns:
        Ti, Ci = fields(int(N), P.DT_P1)
        eT_N.append(np.max(np.abs(Ti - Tref)) / Ts)
        eC_N.append(np.max(np.abs(Ci - Cref)) / Cs)

    dts = np.array([8.0, 4.0, 2.0, 1.0])
    Tref2, Cref2 = fields(P.N_CV, 0.25)
    Ts2 = max(np.max(np.abs(Tref2)), 1.0)
    Cs2 = max(np.max(np.abs(Cref2)), P.C_TH)
    eT_dt, eC_dt = [], []
    for dt in dts:
        Ti, Ci = fields(P.N_CV, float(dt))
        eT_dt.append(np.max(np.abs(Ti - Tref2)) / Ts2)
        eC_dt.append(np.max(np.abs(Ci - Cref2)) / Cs2)

    np.savez_compressed(os.path.join(OUT, 'conv.npz'),
                        Ns=Ns, eT_N=np.array(eT_N), eC_N=np.array(eC_N),
                        ref_N=P.REF_N_CV, ref_dt=P.REF_DT_S,
                        dts=dts, eT_dt=np.array(eT_dt), eC_dt=np.array(eC_dt),
                        ref_dt2=0.25, tol=P.GRID_TOL)
    _log('conv done: eT(N=40)=%.2e  eT(dt=1)=%.2e' % (eT_N[2], eT_dt[3]))


def run_inputs():
    amb = AMB.Ambient()
    t1 = amb._t.copy()
    geom = geometry.MovingGeometry()
    t2, R_mono_m = geom.R_data
    import pandas as pd
    df2 = pd.read_excel(P.ATTACH2, sheet_name=0)
    R_raw_cm = pd.to_numeric(df2.iloc[:, 1], errors='coerce').to_numpy(dtype=float)
    tt = np.linspace(t2[0], t2[-1], 1200)
    np.savez_compressed(os.path.join(OUT, 'inputs.npz'),
                        t_air=t1, T_air=amb._T.copy(), C_air=amb._C.copy(),
                        t_R=t2, R_raw_cm=R_raw_cm, R_mono_cm=R_mono_m / P.CM_TO_M,
                        t_dense=tt, R_dense_cm=geom.R(tt) / P.CM_TO_M,
                        Rdot_dense=geom.Rdot(tt))
    _log('inputs done: attach1=%d rows, attach2=%d rows' % (t1.size, t2.size))


if __name__ == '__main__':
    t0 = time.time()
    run_inputs()
    run_p1()
    run_conv()
    run_p2()
    run_p3()
    run_p4()
    _log('ALL DONE in %.1f s' % (time.time() - t0))
