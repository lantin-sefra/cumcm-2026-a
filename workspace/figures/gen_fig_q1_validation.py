"""fig_q1_validation — 残差诊断四合一：半解析对照 + 逐点偏差 + 网格/时间步收敛 + 守恒残差。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matplotlib.ticker import NullFormatter  # noqa: E402

from _figcommon import (C, M, load, newfig, panel, finish,  # noqa: E402
                        shared_legend)

d = load('p1')
cv = load('conv')

t = d['t']
ta = d['t_ana']
dev_c = d['Tcenter'][1:] - d['ana_center']
dev_s = d['Tsurf'][1:] - d['ana_surf']

fig = newfig(6.4, 5.1, width_fraction=0.98)
gs = fig.add_gridspec(2, 2, hspace=0.38, wspace=0.30)
ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, 0])
ax_d = fig.add_subplot(gs[1, 1])

# (a) 数值 vs Bessel–Duhamel 半解析
ax_a.plot(t, d['Tcenter'], color=C['red_strong'], lw=1.5, label='数值 $T(0,t)$')
ax_a.plot(ta, d['ana_center'], ls='none', marker=M[0], ms=3.0, mfc='none',
          mew=0.7, markevery=12, color=C['neutral_black'], label='半解析 $T(0,t)$')
ax_a.plot(t, d['Tsurf'], color=C['blue_main'], lw=1.5, ls='--',
          label='数值 $T(R,t)$')
ax_a.plot(ta, d['ana_surf'], ls='none', marker=M[1], ms=3.0, mfc='none',
          mew=0.7, markevery=12, color=C['neutral_dark'], label='半解析 $T(R,t)$')
ax_a.set_xlabel('时间 $t$ (s)')
ax_a.set_ylabel('温度 $T$ (℃)')
ax_a.set_xlim(0, t[-1])
ax_a.set_xticks(np.arange(0, 1801, 600))
panel(ax_a, '(a)')

# (b) 逐点偏差时程
ax_b.axhline(0.0, color=C['neutral_mid'], lw=0.8, ls=':')
ax_b.plot(ta, dev_c * 1e3, color=C['red_strong'], lw=1.3, label='中心 $r=0$')
ax_b.plot(ta, dev_s * 1e3, color=C['blue_main'], lw=1.3, ls='--', label='表面 $r=R$')
mx = max(np.max(np.abs(dev_c)), np.max(np.abs(dev_s))) * 1e3
i_mx = int(np.argmax(np.abs(dev_c)))
ax_b.annotate('%.2f mK' % mx, xy=(ta[i_mx], mx), xytext=(190, 2.30),
              color=C['neutral_dark'])
ax_b.set_xlabel('时间 $t$ (s)｜实线 中心 / 虚线 表面')
ax_b.set_ylabel('数值−半解析偏差 (mK)')
ax_b.set_xlim(0, t[-1])
ax_b.set_ylim(-0.35, 3.45)
ax_b.set_xticks(np.arange(0, 1801, 600))
panel(ax_b, '(b)')

# (c) 网格收敛（对 N=160/Δt=0.125 s 参照解的相对偏差，式28）
ax_c.plot(cv['Ns'], cv['eT_N'], color=C['red_strong'], lw=1.4, marker=M[0],
          ms=3.6, label='温度 $e_T$')
ax_c.plot(cv['Ns'], cv['eC_N'], color=C['blue_main'], lw=1.4, ls='--',
          marker=M[1], ms=3.6, label='含水率 $e_C$')
ax_c.axhline(float(cv['tol']), color=C['neutral_mid'], lw=0.9, ls=':')
ax_c.annotate('0.5%', xy=(30, float(cv['tol'])), xytext=(26, 8.5e-3),
              color=C['neutral_dark'])
ax_c.set_xscale('log')
ax_c.set_yscale('log')
ax_c.set_xlabel('控制体数 $N$｜实线 $e_T$ / 虚线 $e_C$')
ax_c.set_ylabel('相对偏差 $e$ (—)')
ax_c.set_xticks([10, 20, 40, 80])
ax_c.set_xticklabels(['10', '20', '40', '80'])
# 不足一个十倍程的对数轴会自动补 minor 刻度标签（3×10¹ 之类），其上标只有
# 5.9 pt，会把整图 10% 分位字号压到印刷线以下；minor 标签一律关掉。
ax_c.xaxis.set_minor_formatter(NullFormatter())
ax_c.yaxis.set_minor_formatter(NullFormatter())
ax_c.set_ylim(1.2e-5, 3.5e-2)
ax_c.set_yticks([1e-4, 1e-2])
panel(ax_c, '(c)')

# (d) 时间步收敛（固定 N=40，参照 Δt=0.25 s）
ax_d.plot(cv['dts'], cv['eT_dt'], color=C['red_strong'], lw=1.4, marker=M[0],
          ms=3.6, label='温度 $e_T$')
ax_d.plot(cv['dts'], cv['eC_dt'], color=C['blue_main'], lw=1.4, ls='--',
          marker=M[1], ms=3.6, label='含水率 $e_C$')
ax_d.axhline(float(cv['tol']), color=C['neutral_mid'], lw=0.9, ls=':')
ax_d.annotate('0.5%', xy=(3.0, float(cv['tol'])), xytext=(2.6, 8.5e-3),
              color=C['neutral_dark'])
ax_d.set_xscale('log')
ax_d.set_yscale('log')
ax_d.set_xlabel('时间步 $\\Delta t$ (s)')
ax_d.set_ylabel('相对偏差 $e$ (—)')
ax_d.set_xticks([1, 2, 4, 8])
ax_d.set_xticklabels(['1', '2', '4', '8'])
ax_d.xaxis.set_minor_formatter(NullFormatter())
ax_d.yaxis.set_minor_formatter(NullFormatter())
ax_d.set_ylim(1.2e-5, 3.5e-2)
ax_d.set_yticks([1e-4, 1e-2])
panel(ax_d, '(d)')

shared_legend(fig, axes=[ax_a], where='top', ncol=4)

finish(fig, 'fig_q1_validation')
