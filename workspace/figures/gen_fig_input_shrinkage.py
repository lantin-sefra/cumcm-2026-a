"""fig_input_shrinkage — 附件2 药材半径收缩时序（145 行全量）折线图+渐变填充。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import (C, load, newfig, finish, auto_legend, R0_CM,  # noqa: E402
                        SEC_PER_HOUR)

d = load('inputs')
t_h = d['t_R'] / SEC_PER_HOUR
R = d['R_mono_cm']
td = d['t_dense'] / SEC_PER_HOUR
Rd = d['R_dense_cm']
Rdot_cm_h = d['Rdot_dense'] / 1e-2 * SEC_PER_HOUR      # m/s → cm/h

fig = newfig(6.4, 3.6, width_fraction=0.9)
ax = fig.add_subplot(1, 1, 1)
ax2 = ax.twinx()

# 渐变填充：把 R(t) 下方按 20 层薄带叠出深浅过渡（每层都有配对曲线，见下 plot）
n_band = 20
for i in range(n_band):
    lo = R0_CM * i / n_band
    hi = R0_CM * (i + 1) / n_band
    ax.fill_between(td, np.clip(Rd, lo, hi), lo, where=Rd > lo,
                    color=C['blue_secondary'], alpha=0.05, lw=0)
ln0, = ax.plot(td, Rd, color=C['blue_main'], lw=1.7, label='PCHIP 保形插值 $R(t)$')
ln1, = ax.plot(t_h, R, ls='none', marker='o', ms=2.6, mfc='none', mew=0.7,
               color=C['neutral_dark'], label='附件2 实测半径（145 点）')
ln2, = ax2.plot(td, Rdot_cm_h, color=C['red_strong'], lw=1.2, ls='--',
                label='收缩速率 $\\dot{R}(t)$')

ax.axhline(R0_CM, color=C['neutral_mid'], lw=0.8, ls=':')
ax.annotate('$R_0$=2.00 cm', xy=(1.0, R0_CM), xytext=(1.0, 2.06),
            color=C['neutral_dark'])
ax.annotate('%.3f cm' % R[-1], xy=(t_h[-1], R[-1]), xytext=(t_h[-1] - 15.0, 1.13),
            color=C['blue_main'])

ax.set_xlabel('时间 $t$ (h)')
ax.set_ylabel('药材半径 $R$ (cm)')
ax2.set_ylabel('收缩速率 $\\dot{R}$ (cm/h)', color=C['red_strong'])
ax2.tick_params(axis='y', colors=C['red_strong'])
ax.set_xlim(0, t_h[-1])
ax.set_ylim(1.0, 2.22)
ax2.set_ylim(-0.35, 0.05)
ax.set_xticks(np.arange(0, 73, 12))
auto_legend(ax, handles=[ln0, ln1, ln2], loc='lower left')

finish(fig, 'fig_input_shrinkage')
