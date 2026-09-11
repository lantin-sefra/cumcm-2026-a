"""fig_convergence — 交付网格收敛性：t_end 随 N 的收敛 + 质量残差随 N 的量级。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, M, load_json, newfig, panel, finish  # noqa: E402

v = load_json('validation')
blk = v['evidence_section9']['X_C1_face_mode_convergence']
Ns = np.array([20.0, 40.0, 80.0])
tend = np.array([float(blk['arith_tend_h'][str(int(n))]) for n in Ns])
resid = np.array([float(blk['arith_mass_resid'][str(int(n))]) for n in Ns])
rel40_80 = float(blk['arith_N40_vs_N80_rel']) * 100.0
tol_mass = float(v['evidence_section9']['9_1_mass_budget']['tol'])

fig = newfig(6.4, 3.3, width_fraction=0.96)
gs = fig.add_gridspec(1, 2, wspace=0.30)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# (a) t_end(N)：交付网格 N=40 与参照 N=80 的相对变化落在 1% 判据内
ax1.plot(Ns, tend, color=C['blue_main'], lw=1.6, marker=M[0], ms=5.0,
               )
ax1.axhline(tend[-1], color=C['neutral_mid'], lw=0.9, ls=':')
ax1.plot([Ns[1]], [tend[1]], marker='D', ms=6.5, color=C['red_strong'],
         zorder=4)
ax1.set_xscale('log', base=2)
ax1.set_xlabel('径向控制体数 $N$（交付 $N$=40）')
# 轴标签只留量名与单位：并上"附录3 / 固定半径"后旋转标签高 217 pt、逼到画布顶缘
# 3.9 pt，几乎贯穿整个轴高。求解口径写进 caption。
ax1.set_ylabel('达标时间 $t_{end}$ (h)')
ax1.set_xlim(16.0, 100.0)
ax1.set_ylim(55.9, 57.34)
ax1.set_xticks(Ns)
ax1.set_xticklabels(['20', '40', '80'])
ax1.set_yticks(np.arange(56.0, 57.31, 0.3))
ax1.text(21.0, 57.05, '$N$=40 vs 80：%.3f%%' % rel40_80,
         color=C['neutral_black'])
ax1.text(21.0, 56.86, '判据 1%', color=C['neutral_dark'])
panel(ax1, '(a)')

# (b) 质量收支残差随 N：全部远低于 1e-10 容差
ax2.plot(Ns, resid, color=C['green_3'], lw=1.6, marker=M[1], ms=5.0,
               )
ax2.set_xscale('log', base=2)
ax2.set_yscale('log')
ax2.set_xlabel('径向控制体数 $N$')
ax2.set_ylabel('相对质量残差 (—)')
ax2.set_xlim(16.0, 100.0)
ax2.set_ylim(2e-15, 6e-14)
ax2.set_xticks(Ns)
ax2.set_xticklabels(['20', '40', '80'])
ax2.set_yticks([3e-15, 1e-14, 3e-14])
ax2.text(21.0, 3.4e-14, '低于容差 4 个量级', color=C['neutral_dark'])
panel(ax2, '(b)')

finish(fig, 'fig_convergence')
