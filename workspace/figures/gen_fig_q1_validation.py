"""fig_q1_validation — 残差诊断四合一：半解析对照 + 逐点偏差 + 网格/时间步收敛 + 守恒残差。"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matplotlib.ticker import NullFormatter  # noqa: E402

from _figcommon import (C, M, load, newfig, panel, finish,  # noqa: E402
                        shared_legend)

d = load('p1')

t = d['t']
# 半解析序列是既有验证数据；数值曲线改读正式 result1.xlsx。
with np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '_figdata', 'p1.npz')) as hist:
    ta = hist['t_ana'].copy()
    ana_center = hist['ana_center'].copy()
    ana_surf = hist['ana_surf'].copy()
num_center = np.interp(ta, t, d['Tcenter'])
num_surf = np.interp(ta, t, d['Tsurf'])
dev_c = num_center - ana_center
dev_s = num_surf - ana_surf

# 已锁定的现成 Q1 收敛数据；正式采用 N=160、Δt=0.125 s。
Ns = np.array([40.0, 80.0])
center_N = np.array([33.57545770, 33.57548548])
surface_N = np.array([36.78558090, 36.78563187])
ref_center_N = 33.57549243
ref_surface_N = 36.78564460
e_center_N = np.abs(center_N - ref_center_N) / abs(ref_center_N)
e_surface_N = np.abs(surface_N - ref_surface_N) / abs(ref_surface_N)

dts = np.array([1.000, 0.500, 0.250])
center_dt = np.array([33.57650786, 33.57590766, 33.57560766])
surface_dt = np.array([36.78620022, 36.78584633, 36.78566938])
ref_center_dt = 33.57545770
ref_surface_dt = 36.78558090
e_center_dt = np.abs(center_dt - ref_center_dt) / abs(ref_center_dt)
e_surface_dt = np.abs(surface_dt - ref_surface_dt) / abs(ref_surface_dt)
tol = 0.005

fig = newfig(6.4, 5.1, width_fraction=0.98)
gs = fig.add_gridspec(2, 2, hspace=0.38, wspace=0.30)
ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, 0])
ax_d = fig.add_subplot(gs[1, 1])

# (a) 数值 vs Bessel–Duhamel 半解析
ax_a.plot(t, d['Tcenter'], color=C['red_strong'], lw=1.5, label='数值 $T(0,t)$')
ax_a.plot(ta, ana_center, ls='none', marker=M[0], ms=3.0, mfc='none',
          mew=0.7, markevery=12, color=C['neutral_black'], label='半解析 $T(0,t)$')
ax_a.plot(t, d['Tsurf'], color=C['blue_main'], lw=1.5, ls='--',
          label='数值 $T(R,t)$')
ax_a.plot(ta, ana_surf, ls='none', marker=M[1], ms=3.0, mfc='none',
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

# (c) 网格收敛（对 N=160、Δt=0.125 s 参照解的相对偏差，式28）
ax_c.plot(Ns, e_center_N, color=C['red_strong'], lw=1.4, marker=M[0],
          ms=3.6, label='中心 $e_T$')
ax_c.plot(Ns, e_surface_N, color=C['blue_main'], lw=1.4, ls='--',
          marker=M[1], ms=3.6, label='表面 $e_T$')
ax_c.axhline(tol, color=C['neutral_mid'], lw=0.9, ls=':')
ax_c.annotate('0.5%', xy=(50, tol), xytext=(46, 8.5e-3),
              color=C['neutral_dark'])
ax_c.set_xscale('log')
ax_c.set_yscale('log')
ax_c.set_xlabel('控制体数 $N$｜实线 中心 / 虚线 表面')
ax_c.set_ylabel('相对偏差 $e$ (—)')
ax_c.set_xlim(35, 190)
ax_c.set_xticks([40, 80, 160])
ax_c.set_xticklabels(['40', '80', '160'])
# 不足一个十倍程的对数轴会自动补 minor 刻度标签（3×10¹ 之类），其上标只有
# 5.9 pt，会把整图 10% 分位字号压到印刷线以下；minor 标签一律关掉。
ax_c.xaxis.set_minor_formatter(NullFormatter())
ax_c.yaxis.set_minor_formatter(NullFormatter())
ax_c.set_ylim(1.0e-7, 3.5e-2)
ax_c.set_yticks([1e-6, 1e-4, 1e-2])
panel(ax_c, '(c)')

# (d) 时间步收敛（固定 N=40，参照 Δt=0.125 s）
ax_d.plot(dts, e_center_dt, color=C['red_strong'], lw=1.4, marker=M[0],
          ms=3.6, label='中心 $e_T$')
ax_d.plot(dts, e_surface_dt, color=C['blue_main'], lw=1.4, ls='--',
          marker=M[1], ms=3.6, label='表面 $e_T$')
ax_d.axhline(tol, color=C['neutral_mid'], lw=0.9, ls=':')
ax_d.annotate('0.5%', xy=(0.75, tol), xytext=(0.68, 8.5e-3),
              color=C['neutral_dark'])
ax_d.set_xscale('log')
ax_d.set_yscale('log')
ax_d.set_xlabel('时间步 $\\Delta t$ (s)｜固定 $N$=40')
ax_d.set_ylabel('相对偏差 $e$ (—)')
ax_d.set_xlim(0.10, 1.2)
ax_d.set_xticks([0.125, 0.25, 0.5, 1.0])
ax_d.set_xticklabels(['0.125', '0.25', '0.5', '1'])
ax_d.xaxis.set_minor_formatter(NullFormatter())
ax_d.yaxis.set_minor_formatter(NullFormatter())
ax_d.set_ylim(2.0e-6, 3.5e-2)
ax_d.set_yticks([1e-4, 1e-2])
panel(ax_d, '(d)')

shared_legend(fig, axes=[ax_a], where='top', ncol=4)

finish(fig, 'fig_q1_validation')
