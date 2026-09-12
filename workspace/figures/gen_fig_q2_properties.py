"""fig_q2_properties — 附录3 四条物性公式的平行坐标图（按含水率着色）。

C 取正式 result3.xlsx 的 21 列场；T 在前 3 h 取正式 result2.xlsx，
3 h 之后按题目平台温度 50 ℃。ρ/cp/k/D 用 code/props.py 附录3 公式重算，
不读 _figdata/p3.npz 的旧节点物性。
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _figcommon import C, load, newfig, finish, mono_cmap, ROOT  # noqa: E402

CODE = os.path.join(ROOT, 'code')
if CODE not in sys.path:
    sys.path.insert(0, CODE)
import props as PR  # noqa: E402

p2 = load('p2')
p3 = load('p3')

Ccol = np.asarray(p3['Ccol'], dtype=float)
t3 = np.asarray(p3['t'], dtype=float)
Tcol = np.full_like(Ccol, 50.0)
t2 = np.asarray(p2['t'], dtype=float)
T2 = np.asarray(p2['Tcol'], dtype=float)
early = t3 <= t2[-1] + 1e-9
for j in range(Ccol.shape[1]):
    Tcol[early, j] = np.interp(t3[early], t2, T2[:, j])

rho, cp, kk, Dd = PR.props(3, Ccol, Tcol)
Cs = Ccol.ravel()
Ts = Tcol.ravel()
rho = rho.ravel()
cp = cp.ravel()
kk = kk.ravel()
Dd = Dd.ravel()
print('[source] appendix=3  C=[%.4f, %.4f]  T=[%.4f, %.4f]  n=%d'
      % (float(Cs.min()), float(Cs.max()), float(Ts.min()), float(Ts.max()),
         Cs.size), flush=True)

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
print('[source] bins=%d  C_high=%.4f→C_low=%.4f  rho=%.1f→%.1f  '
      'cp=%.0f→%.0f  k=%.3f→%.3f  Dmin=%.3e'
      % (len(cvals), cvals[-1], cvals[0], rows[-1, 0], rows[0, 0],
         rows[-1, 1], rows[0, 1], rows[-1, 2], rows[0, 2], rows[:, 3].min()),
      flush=True)

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
# 轴名字符串与 main 一致，仍写 (℃)。main 用 Microsoft YaHei 画出 U+2103；
# 本环境优先中文字体把该字画成空白，刻度改用带实心 ℃ 字形的西文字体。
for lab in ax.get_xticklabels():
    lab.set_fontfamily('DejaVu Sans')
ax.set_xlim(-0.45, len(names) - 0.55)
# 上下各让出一行：端点量程读数贴在归一化轴的 0 / 1 之外
ax.set_ylim(-0.26, 1.24)
ax.set_ylabel('逐轴归一化取值 (—)')
ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])

finish(fig, 'fig_q2_properties')
