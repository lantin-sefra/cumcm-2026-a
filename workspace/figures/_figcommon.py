"""22 张数据图的共享底座（风格/取色/取数/落盘）。

⛔ 本文件【不是】出图脚本（不以 gen_fig 开头），只被 gen_fig_*.py import。
风格契约：setup_style('nature') 全篇调一次；每张图建好 fig 后立即 set_paper_placement；
取色只走 nature_palette()，禁止 hex 字面量；落盘只走 save_fig（LaTeX 模式 → 仅 PDF）。
"""
from __future__ import annotations

import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from _utils.plot_utils import (  # noqa: E402
    setup_style, save_fig, set_paper_placement, nature_palette, nature_markers,
    smart_labels, auto_legend, shared_legend, uncertainty_band, dynamic_limits,
    declutter_axes, draw_vector_heatmap,
)

import matplotlib.pyplot as plt  # noqa: E402

setup_style(palette='nature')

# matplotlib 默认往 PDF 里嵌 Type3 字体，中文字形没有 ToUnicode 映射 —— 结果是
# PDF 里的中文完全不可提取：文字体检脚本只看得见数字和拉丁字符，中文标签的
# 重叠/字号一项都没被查过（实测 get_text() 提取到 0 个汉字）。改嵌 TrueType(42)
# 让中文可提取、可搜索、可复制，体检脚本才真正覆盖中文。
import matplotlib  # noqa: E402
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

C = nature_palette()
M = nature_markers()
FIGDATA = os.path.join(ROOT, 'figures', '_figdata')
OUTDIR = os.path.join(ROOT, 'figures')

# 交付口径常量（与 code/params.py 一致，仅用于画阈值线/标注，不参与求解）
C_TH = 0.15          # kg/kg 达标阈值
R0_CM = 2.0          # cm 初始半径
SEC_PER_HOUR = 3600.0


def load(tag):
    """读 figures/_figdata/<tag>.npz。缺文件直接 raise（禁止静默兜底出空图）。"""
    path = os.path.join(FIGDATA, '%s.npz' % tag)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            '缺少数值场缓存 %s —— 请先运行 python figures/prep_figdata.py' % path)
    return np.load(path)


def load_json(name):
    """读 output/<name>.json（上游 code/main.py 真算落盘的摘要）。"""
    import json
    path = os.path.join(ROOT, 'output', '%s.json' % name)
    if not os.path.isfile(path):
        raise FileNotFoundError('缺少上游结果 %s' % path)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_csv(name):
    """读 output/<name>（上游真算 CSV）。返回 pandas.DataFrame。"""
    import pandas as pd
    path = os.path.join(ROOT, 'output', name)
    if not os.path.isfile(path):
        raise FileNotFoundError('缺少上游结果 %s' % path)
    return pd.read_csv(path)


def newfig(w, h, width_fraction=0.92):
    """建图并立即登记版面占位（风格契约要求 set_paper_placement 紧随其后）。"""
    fig = plt.figure(figsize=(w, h), layout='constrained')
    # 两处余量都是实测需要的：
    # 1) constrained 按 matplotlib 字体度量排版，PDF 里的字形上升部比它算的再高
    #    1~2 pt，最左 y 标签会压到 mediabox 外；
    # 2) auto_legend 把图例抬进独立行时会重排，没让位的那一行子图会向上扩张，
    #    把 (a)/(b) 面板标签顶出画布 —— 顶部要留够一个面板标签的高度。
    # 左右各留 13 pt：旋转的中文 y 标签横向占位由字高决定，matplotlib 报出的
    # window extent 比 PDF 里的真实字形边缘偏右约 9.75 pt（实测扫墨迹标定：
    # 最左墨迹 ≈ mx − 9.75 pt），所以按它排版必然压边。shared_legend 提交车道后
    # 会 set_layout_engine('none') 冻结轴位、丢掉本 rect，事后无法补救，
    # 必须一开始就留够。
    mx = 13.0 / (w * 72.0)
    my = 2.0 / (h * 72.0)
    top = 6.0 / (h * 72.0)
    fig.get_layout_engine().set(rect=(mx, my, 1.0 - 2.0 * mx, 1.0 - my - top))
    set_paper_placement(fig, width_fraction=width_fraction)
    return fig


def panel(ax, tag):
    """子图面板标签 (a)/(b)/… —— 左上角，非整图标题。"""
    ax.set_title(tag, loc='left', fontweight='bold')


def finish(fig, name):
    """落盘 figures/<name>.pdf（LaTeX 模式仅矢量 PDF，不产 PNG）。"""
    out = os.path.join(OUTDIR, '%s.pdf' % name)
    save_fig(fig, out)
    plt.close(fig)
    print('[fig] %s.pdf' % name, flush=True)


def seq_colors(n, family='blue'):
    """同族 n 级渐变色（时间序/剖面族用）。取色仍源自 nature_palette。"""
    from matplotlib.colors import to_rgb, to_hex
    if family == 'blue':
        a, b = C['blue_secondary'], C['neutral_black']
    elif family == 'red':
        a, b = C['red_1'], C['red_strong']
    elif family == 'green':
        a, b = C['green_1'], C['green_3']
    else:
        a, b = C['neutral_light'], C['neutral_black']
    ra, rb = np.array(to_rgb(a)), np.array(to_rgb(b))
    if n == 1:
        return [to_hex(ra)]
    return [to_hex(ra + (rb - ra) * i / (n - 1.0)) for i in range(n)]


def mono_cmap(family='blue', dark_end=1.0):
    """由 nature_palette 语义色生成单调 colormap（热力图/时空图用）。

    dark_end < 1 时截掉最暗的一段：叠了黑色等值线的时空图里，落进接近纯黑那一端
    的等值线看不见（实测含水率图上端 vmax 处几乎全黑，2.5 那条线整段隐没）。
    """
    import numpy as _np
    from matplotlib.colors import LinearSegmentedColormap
    if family == 'blue':
        stops = ['#FFFFFF', C['blue_secondary'], C['blue_main'], C['neutral_black']]
    elif family == 'red':
        stops = ['#FFFFFF', C['red_1'], C['red_2'], C['red_strong']]
    elif family == 'green':
        stops = ['#FFFFFF', C['green_1'], C['green_2'], C['green_3']]
    else:
        stops = ['#FFFFFF', C['neutral_light'], C['neutral_mid'], C['neutral_black']]
    cm = LinearSegmentedColormap.from_list('mh_%s' % family, stops, N=256)
    if dark_end >= 1.0:
        return cm
    return LinearSegmentedColormap.from_list(
        'mh_%s_t' % family, cm(_np.linspace(0.0, dark_end, 256)), N=256)


def label_levels_on_cbar(cb, cs, fmt='%g'):
    """把等值线层级标到色标上，替代压在热力图上的 inline clabel。

    inline 标注只掏空等值线本身，字仍坐在热力图底色上；落到色标暗端时黑字
    对比度不足（实测 1.x:1），加白底又会撑出 3 倍字高的补丁。改为等值线只留线、
    层级读数移到色标（白底刻度区），既无对比度风险也不遮数据。
    """
    cb.add_lines(cs)
    levels = list(cs.levels)
    cb.set_ticks(levels)
    cb.set_ticklabels([fmt % v for v in levels])
    return cb


def nearest_idx(arr, val):
    """最近邻下标（按报表时刻从密集时间轴取快照，不插值造数）。"""
    return int(np.argmin(np.abs(np.asarray(arr, dtype=float) - float(val))))
