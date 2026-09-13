"""fig_property_maps — 附录3/附录4 的水分扩散系数 D(C,T) 双面板热力图（共享对数色标）。"""
import os
import sys

import numpy as np
from matplotlib.colors import LogNorm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, ROOT, newfig, finish, mono_cmap  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, 'code'))
from props import props  # noqa: E402

Cg = np.linspace(0.15, 2.55, 145)
Tg = np.linspace(28.0, 50.0, 133)
CC, TT = np.meshgrid(Cg, Tg)
D3 = props(3, CC, TT)[3]
D4 = props(4, CC, TT)[3]
ratio = D4 / D3

fig = newfig(6.4, 3.2, width_fraction=0.98)
gs = fig.add_gridspec(1, 2, wspace=0.12)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

vmin = min(D3.min(), D4.min())
vmax = max(D3.max(), D4.max())
norm = LogNorm(vmin=vmin, vmax=vmax)
cmap = mono_cmap('blue')

for ax, Z in ((ax1, D3), (ax2, D4)):
    pm = ax.pcolormesh(Cg, Tg, Z, cmap=cmap, norm=norm, shading='auto',
                       rasterized=True)
    cs = ax.contour(Cg, Tg, Z, levels=[1e-9, 2e-9, 5e-9, 1e-8],
                    colors=[C['neutral_black']], linewidths=0.6)
    ax.set_xlabel('干基含水率 $C$ (kg/kg)')
    ax.set_xlim(0.15, 2.55)
    ax.set_ylim(28.0, 50.0)
    ax.set_xticks(np.arange(0.5, 2.51, 0.5))
    ax.set_yticks(np.arange(30, 50.1, 5))

ax1.set_ylabel('药材局部温度 $T$ (℃)')
ax2.set_yticklabels([])
# 低 C 一侧是色标暗端，文字放在那里对比度不足；改用面板标签承载口径名，
# 比值只写进 (b) 的轴标签（轴标签在白底上）。
ax1.set_title('(a) 附录3', loc='left', fontweight='bold')
ax2.set_title('(b) 附录4', loc='left', fontweight='bold')
ax2.set_xlabel('干基含水率 $C$ (kg/kg)｜$D_4/D_3$=%.3f–%.3f'
               % (ratio.min(), ratio.max()))

cb = fig.colorbar(pm, ax=[ax1, ax2], pad=0.02)
cb.set_label('水分扩散系数 $D$ (m$^2$/s)')

finish(fig, 'fig_property_maps')
