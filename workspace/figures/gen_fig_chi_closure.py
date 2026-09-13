"""fig_chi_closure — 问题4 移动边界闭合双线对比（正式口径）。

χ=1 材料随动 ALE：output/result4.xlsx（正式主模型）
χ=0 Eulerian/Landau：output/final_diagnostics/q4_chi0_timeseries.csv（交叉验证）
禁止读 _figdata/p4s2.npz、p4s3.npz 或 prep_figdata.py 的旧 χ 缓存。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, M, load, load_formal_csv, newfig, finish,  # noqa: E402
                        auto_legend, C_TH, SEC_PER_HOUR, ROOT, describe_source)

# load('p4s2') 已接到 result4.xlsx，并打印 SHA；这里再核对 χ=1 时长。
s1 = load('p4s2')
t1 = s1['t'] / SEC_PER_HOUR
m1 = np.asarray(s1['maxC'], dtype=float)
e1 = float(s1['t_end_h'])

df0 = load_formal_csv('final_diagnostics/q4_chi0_timeseries.csv')
t0 = df0['time_h'].to_numpy(dtype=float)
m0 = df0['C_max'].to_numpy(dtype=float)
e0 = float(t0[-1])
describe_source(os.path.join(ROOT, 'output', 'final_diagnostics',
                             'q4_chi0_summary.csv'),
                chi=0, t_end_h='%.4f' % e0)

if abs(e1 - 51.0869) > 5e-4 or abs(e0 - 52.6476) > 5e-4:
    raise RuntimeError('χ 闭合时长偏离正式口径: χ1=%.6f χ0=%.6f'
                       % (e1, e0))
delta = e0 - e1
print('[source] χ=1 ALE t_end=%.4f h  χ=0 Landau t_end=%.4f h  Δ=%+.4f h (%.4f%%)'
      % (e1, e0, delta, delta / e1 * 100.0), flush=True)

fig = newfig(6.4, 3.6, width_fraction=0.92)
ax = fig.add_subplot(1, 1, 1)

l1, = ax.plot(t1, m1, color=C['blue_main'], lw=1.6, marker=M[0], ms=3.0,
              markevery=max(1, t1.size // 40),
              label='$\\chi=1$：材料随动 ALE（主模型）')
l0, = ax.plot(t0, m0, color=C['red_strong'], lw=1.6, ls='--', marker=M[1],
              ms=3.0, markevery=max(1, t0.size // 40),
              label='$\\chi=0$：Eulerian/Landau（交叉验证）')
ax.axhline(C_TH, color=C['neutral_dark'], lw=0.9, ls=':')
ax.axvline(e1, color=C['blue_main'], lw=0.8, ls='--')
ax.axvline(e0, color=C['red_strong'], lw=0.8, ls='--')
ax.plot([e1], [C_TH], marker='o', ms=5.0, color=C['blue_main'], zorder=4)
ax.plot([e0], [C_TH], marker='s', ms=5.0, color=C['red_strong'], zorder=4)

ax.set_xlabel('时间 $t$ (h)  |  $t_{end}$: %.4f h ($\\chi$=1) / %.4f h ($\\chi$=0)'
              % (e1, e0))
ax.set_ylabel('全域最大干基含水率 $C_{max}$ (kg/kg)')
ax.set_xlim(0, 58.0)
ax.set_ylim(0, 2.72)
ax.set_xticks(np.arange(0, 56.1, 8))
ax.set_yticks(np.arange(0, 2.71, 0.5))
ax.text(2.0, C_TH + 0.09, '$C_{th}$=0.15 kg/kg', color=C['neutral_dark'])
ax.text(22.0, 1.62, '$\\Delta t_{end}$=%+.4f h (%.4f%%)'
        % (delta, delta / e1 * 100.0), color=C['neutral_black'])
auto_legend(ax, handles=[l1, l0], loc='upper right')

finish(fig, 'fig_chi_closure')
