"""
五子棋 (Gomoku/Renju) — 主程序入口
支持人人对战和人机对战，含专业禁手规则（Renju标准）
纯单机离线运行，基于 Kivy 框架，可打包 Android APK
"""

import platform
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.metrics import dp, sp

# 先注册中文字体，再加载任何 UI
import fonts  # noqa: F401

from ui.menu_screen import MenuScreen
from ui.settings_screen import SettingsScreen
from ui.rules_screen import RulesScreen
from ui.game_screen import GameScreen
from ui.user_screen import UserScreen

# 桌面调试：固定窗口大小；移动端不设置（自动全屏）
if platform.system() in ('Windows', 'Darwin', 'Linux'):
    Window.size = (420, 750)


def get_scale_factor():
    """
    基于屏幕高度返回缩放因子。
    基准：750px 高度 → 1.0
    """
    h = Window.height
    return max(0.6, min(h / 750, 1.8))


class GomokuApp(App):
    """五子棋应用主类"""

    def build(self):
        self.title = '五子棋 · Renju'

        sm = ScreenManager(transition=FadeTransition(duration=0.2))

        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(RulesScreen(name='rules'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(UserScreen(name='users'))

        # 监听窗口尺寸变化
        Window.bind(on_resize=self._on_resize)

        return sm

    def _on_resize(self, window, width, height):
        """窗口大小改变时刷新所有页面"""
        for screen in self.root.screens:
            if hasattr(screen, 'on_window_resize') and hasattr(screen, '_current_layout'):
                screen.on_window_resize(width, height)


if __name__ == '__main__':
    GomokuApp().run()
