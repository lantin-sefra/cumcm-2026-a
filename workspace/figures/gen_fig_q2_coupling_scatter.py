"""fig_q2_coupling_scatter — 问题2 全时空节点 (C, T) 散点 + KDE 等密度线，颜色编码 D。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load, newfig, finish, mono_cmap, auto_legend  # noqa: E402

d = load('p2')
Cs = d['Ccol'].ravel()
Ts = d['Tcol'].ravel()
valid = np.isfinite(Cs) & np.isfinite(Ts)
Cs = Cs[valid]
Ts = Ts[valid]
# 附录3：D=2.4e-3 exp(-0.45/C) exp[-3850/(T+273.15)]。
# 这里只对 result2.xlsx 的现成场作后处理映射，不重新求解模型。
Ds = 2.4e-3 * np.exp(-0.45 / Cs) * np.exp(-3850.0 / (Ts + 273.15))

fig = newfig(6.4, 3.8, width_fraction=0.92)
ax = fig.add_subplot(1, 1, 1)

# result2.xlsx 中的节点样本全量绘制（不抽样）
sc = ax.scatter(Cs, Ts, c=Ds * 1e9, s=2.0, cmap=mono_cmap('blue'), lw=0,
                alpha=0.55)
cb = fig.colorbar(sc, ax=ax, pad=0.02)
cb.set_label('扩散系数 $D$ ($10^{-9}$ m²/s)')

# KDE 等密度线（gaussian_kde 在全量样本上估计，网格 120×120）
from scipy.stats import gaussian_kde  # noqa: E402
kde = gaussian_kde(np.vstack([Cs, Ts]))
gx = np.linspace(Cs.min(), Cs.max(), 120)
gy = np.linspace(Ts.min(), Ts.max(), 120)
GX, GY = np.meshgrid(gx, gy)
Z = kde(np.vstack([GX.ravel(), GY.ravel()])).reshape(GX.shape)
lv = np.percentile(Z, [55, 75, 90, 97])
ax.contour(GX, GY, Z, levels=lv, colors=[C['red_strong']], linewidths=0.8)
from matplotlib.lines import Line2D  # noqa: E402
h_kde = Line2D([], [], color=C['red_strong'], lw=0.8, label='样本核密度等值线')
h_pt = Line2D([], [], ls='none', marker='o', ms=3.0, color=C['blue_main'],
              label='节点样本（%d 个）' % Cs.size)

ax.set_xlabel('干基含水率 $C$ (kg/kg)')
ax.set_ylabel('温度 $T$ (℃)')
ax.set_xlim(0.95, 2.62)
ax.set_ylim(27.0, 51.5)
ax.set_xticks(np.arange(1.0, 2.7, 0.25))
auto_legend(ax, handles=[h_pt, h_kde], loc='lower left')

finish(fig, 'fig_q2_coupling_scatter')
