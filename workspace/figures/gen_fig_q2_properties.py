"""fig_q2_properties — 附录3 四条物性公式的平行坐标图（按含水率着色）。

四轴 ρ / c_p / k / D 各自独立量纲，逐轴按自身量程归一到 [0,1] 后连线；
折线颜色编码该样本的干基含水率 C，温度取问题2 实际场中该 C 对应的平均温度。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load, newfig, finish, mono_cmap  # noqa: E402

d = load('p2')
p3 = load('p3')

# 取问题3 全程节点场（覆盖 C 从 2.55 到 0.15 的完整区间），按 C 分箱取代表样本
Cs = p3['nodesC'].ravel()
Ts = p3['nodesT'].ravel()
rho = p3['rho'].ravel()
cp = p3['cp'].ravel()
kk = p3['k'].ravel()
Dd = p3['D'].ravel()

nb = 24
edges = np.linspace(Cs.min(), Cs.max(), nb + 1)
which = np.clip(np.digitize(Cs, edges) - 1, 0, nb - 1)
rows, cvals = [], []
for b in range(nb):
    m = which == b
    if not np.any(m):
        continue
    rows.append([rho[m].mean(), cp[m].mean(), kk[m].mean(), Dd[m].mean(),
                 Ts[m].mean()])
    cvals.append(Cs[m].mean())
rows = np.asarray(rows)
cvals = np.asarray(cvals)

# 轴名拆两行（符号 / 单位）：量程写进同一个刻度标签时，"1.77e+03–3.41e+03"
# 这类长串宽 91 pt，而相邻轴心只隔 69 pt，实测 k 与 D 两条轴的标签直接重叠
# 2.3 pt（数字/CJK 在 PDF 里并成一个文本行，相撞体检查不到）。改走平行坐标的
# 常规做法：量程端点分别标在各轴两端，标签只留符号与单位。
names = ['$\\rho$\n(kg/m³)', '$c_p$\n(J/(kg·K))', '$k$\n(W/(m·K))',
         '$D$\n(m²/s)', '$T$\n(℃)']
lo = rows.min(axis=0)
hi = rows.max(axis=0)
norm = (rows - lo) / np.where(hi - lo > 0, hi - lo, 1.0)


def _num(v):
    """端点读数：常规量级写十进制，极小量级写 m×10^e，都控制在 3 位有效数字。"""
    import math
    if v == 0:
        return '0'
    if 1e-2 <= abs(v) < 1e4:
        s = '%.3g' % v
        return s if 'e' not in s else '%d' % round(v)
    e = int(math.floor(math.log10(abs(v))))
    return '$%.2f{\\times}10^{%d}$' % (v / 10.0 ** e, e)

cmap = mono_cmap('blue')
cnorm = (cvals - cvals.min()) / (cvals.max() - cvals.min())

fig = newfig(6.4, 3.6, width_fraction=0.94)
ax = fig.add_subplot(1, 1, 1)
xs = np.arange(len(names))
for j in range(norm.shape[0]):
    ax.plot(xs, norm[j], color=cmap(0.20 + 0.78 * cnorm[j]), lw=1.0, alpha=0.9)

# 轴线只画到归一化数据区 [0,1]：axvline 会贯穿整个 ylim，直接穿过两端的量程读数
ax.vlines(xs, 0.0, 1.0, color=C['neutral_mid'], lw=0.7)

sm = __import__('matplotlib').cm.ScalarMappable(cmap=cmap)
sm.set_clim(cvals.min(), cvals.max())
cb = fig.colorbar(sm, ax=ax, pad=0.02)
cb.set_label('干基含水率 $C$ (kg/kg)')

for x, l, h in zip(xs, lo, hi):
    ax.text(x, 1.055, _num(h), ha='center', va='bottom',
            color=C['neutral_black'])
    ax.text(x, -0.075, _num(l), ha='center', va='top',
            color=C['neutral_black'])

ax.set_xticks(xs)
ax.set_xticklabels(names)
ax.set_xlim(-0.45, len(names) - 0.55)
# 上下各让出一行：端点量程读数贴在归一化轴的 0 / 1 之外
ax.set_ylim(-0.26, 1.24)
ax.set_ylabel('逐轴归一化取值 (—)')
ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])

finish(fig, 'fig_q2_properties')
