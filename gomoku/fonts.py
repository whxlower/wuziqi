"""
字体管理模块
加载项目内置中文字体 + 自适应字号工具
优化：方向检测、宽高比适配、设备类型识别
"""

import os
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import sp, dp

# 字体文件路径
_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
_FONT_PATH = os.path.join(_FONT_DIR, 'font.ttc')

# 注册中文字体
if os.path.exists(_FONT_PATH):
    LabelBase.register('zh_font', _FONT_PATH)
    FONT_NAME = 'zh_font'
else:
    FONT_NAME = 'Noto Sans CJK SC'


# ── 方向与设备检测 ──────────────────────────────────────────────

def is_landscape():
    """当前是否为横屏（宽 > 高）"""
    return Window.width > Window.height


def get_orientation():
    """返回 'landscape' 或 'portrait'"""
    return 'landscape' if is_landscape() else 'portrait'


def get_device_type():
    """
    返回设备类型：'phone' 或 'tablet'
    判断依据：短边是否 >= 500dp
    """
    short_side = min(Window.width, Window.height)
    short_dp = short_side / dp(1)
    return 'tablet' if short_dp >= 500 else 'phone'


def get_aspect_ratio():
    """返回宽高比（宽/高），始终 >= 1"""
    w, h = Window.width, Window.height
    return max(w, h) / min(w, h) if min(w, h) > 0 else 1.0


# ── 缩放系统 ──────────────────────────────────────────────

def _get_scale():
    """
    返回缩放因子。
    基准：750px 短边 → 1.0
    横屏时以短边为基准（字不能太小），额外乘 0.85
    范围：0.55 ~ 1.8
    """
    w, h = Window.width, Window.height
    short = min(w, h)
    long_side = max(w, h)

    # 以短边为基准
    scale = short / 750

    # 横屏：短边较短，缩放因子适当缩小
    if w > h:
        scale *= 0.85

    # 超宽屏（宽高比 > 2.0）再缩小
    aspect = long_side / short if short > 0 else 1.0
    if aspect > 2.0:
        scale *= 0.9

    # 超窄屏（折叠屏外屏）
    if aspect < 1.3 and w < h:
        scale *= 0.9

    return max(0.55, min(scale, 1.8))


def s(base_sp: float) -> float:
    """返回自适应 sp 值，用于 font_size"""
    return sp(base_sp * _get_scale())


def d(base_dp: float) -> float:
    """返回自适应 dp 值，用于尺寸/间距"""
    from kivy.metrics import dp as _dp
    return _dp(base_dp * _get_scale())


# ── 布局参数 ──────────────────────────────────────────────

def get_grid_margins():
    """
    棋盘边距比例。
    横屏时边距略大（有更多空间）
    """
    device = get_device_type()
    landscape = is_landscape()
    if device == 'tablet':
        return 0.05 if landscape else 0.06
    else:
        return 0.03


def get_bottom_bar_height():
    """底部/侧边按钮栏高度/宽度（自适应）"""
    device = get_device_type()
    if device == 'tablet':
        return d(52)
    else:
        return d(44)


def get_sidebar_width():
    """
    横屏模式下右侧控制面板宽度。
    竖屏时返回 0。
    """
    if not is_landscape():
        return 0
    device = get_device_type()
    w = Window.width
    # 侧边栏占屏幕宽度的 22%~28%，有上下限
    ratio = 0.25 if device == 'tablet' else 0.28
    sidebar = w * ratio
    # 限制范围
    min_w = d(140)
    max_w = d(280)
    return max(min_w, min(sidebar, max_w))


def get_sidebar_font_scale():
    """
    横屏侧边栏的字号缩放因子。
    侧边栏较窄，字号需要比主区域略小。
    """
    if not is_landscape():
        return 1.0
    device = get_device_type()
    return 0.85 if device == 'tablet' else 0.9


# 常用字号快捷方式
FONT_SIZE_TITLE = 36
FONT_SIZE_SUBTITLE = 16
FONT_SIZE_BUTTON = 18
FONT_SIZE_LABEL = 15
FONT_SIZE_SMALL = 13
