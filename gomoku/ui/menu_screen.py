"""
主菜单界面
竖屏：纵向居中排列
横屏：左侧标题 + 右侧按钮
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fonts import FONT_NAME, s, d, is_landscape, get_sidebar_width
import user_manager


class MenuScreen(Screen):
    """主菜单页面"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_layout = None
        Clock.schedule_once(self._init_ui, 0)

    def _init_ui(self, dt):
        self._build_ui()

    def _build_ui(self):
        with self.canvas.before:
            Color(0.15, 0.15, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.label_title = Label(
            text='五 子 棋',
            font_name=FONT_NAME,
            font_size=s(42),
            bold=True,
            color=(0.9, 0.8, 0.5, 1),
            size_hint_y=None,
            height=d(70)
        )

        self.label_sub = Label(
            text='Renju · 17x17',
            font_name=FONT_NAME,
            font_size=s(15),
            color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None,
            height=d(25)
        )

        self.btn_pvp = self._create_button('人人对战', (0.3, 0.6, 0.3, 1))
        self.btn_pvp.bind(on_press=self._on_pvp)

        self.btn_pve = self._create_button('人机对战', (0.3, 0.4, 0.7, 1))
        self.btn_pve.bind(on_press=self._on_pve)

        self.btn_rules = self._create_button('禁手说明', (0.6, 0.4, 0.2, 1))
        self.btn_rules.bind(on_press=self._on_rules)

        self.btn_users = self._create_button('用户管理', (0.4, 0.3, 0.6, 1))
        self.btn_users.bind(on_press=self._on_users)

        # 当前用户标签
        self.label_user = Label(
            text='', font_name=FONT_NAME, font_size=s(12),
            color=(0.5, 0.5, 0.6, 1),
            size_hint_y=None, height=d(20),
        )

        self._buttons = [self.btn_pvp, self.btn_pve, self.btn_rules, self.btn_users]

        self._rebuild_layout()

    def _create_button(self, text, bg_color):
        return Button(
            text=text,
            font_name=FONT_NAME,
            font_size=s(19),
            size_hint_y=None,
            height=d(50),
            background_color=bg_color,
            background_normal='',
            color=(1, 1, 1, 1),
            bold=True,
        )

    def _rebuild_layout(self):
        """根据屏幕方向重建布局"""
        orientation = 'landscape' if is_landscape() else 'portrait'
        if orientation == self._current_layout:
            return

        self.clear_widgets()

        self.root = BoxLayout()

        if orientation == 'landscape':
            self._build_landscape()
        else:
            self._build_portrait()

        self.add_widget(self.root)
        self._current_layout = orientation
        Clock.schedule_once(lambda dt: self._refresh_sizes(), 0)

    def _build_portrait(self):
        """竖屏：纵向居中"""
        self.root.orientation = 'vertical'
        self.root.padding = [d(30), d(20)]
        self.root.spacing = d(12)

        self.root.add_widget(Widget(size_hint_y=0.3))

        self.label_title.halign = 'center'
        self.label_sub.halign = 'center'
        self.root.add_widget(self.label_title)
        self.root.add_widget(self.label_sub)

        # 显示当前用户
        self._update_user_label()
        self.root.add_widget(self.label_user)

        self.root.add_widget(Widget(size_hint_y=0.1))

        for btn in self._buttons:
            btn.size_hint_x = 1
            btn.size_hint_y = None
            btn.height = d(50)
            btn.font_size = s(19)
            self.root.add_widget(btn)

        self.root.add_widget(Widget(size_hint_y=0.3))

    def _build_landscape(self):
        """横屏：左侧标题 + 右侧按钮"""
        self.root.orientation = 'horizontal'
        self.root.padding = d(16)
        self.root.spacing = d(20)

        # 左侧：标题区域
        left = BoxLayout(
            orientation='vertical',
            size_hint_x=0.55,
        )
        left.add_widget(Widget(size_hint_y=0.3))
        self.label_title.halign = 'center'
        self.label_title.font_size = s(36)
        self.label_title.height = d(60)
        left.add_widget(self.label_title)
        self.label_sub.halign = 'center'
        self.label_sub.font_size = s(14)
        left.add_widget(self.label_sub)
        left.add_widget(Widget(size_hint_y=0.5))

        self.root.add_widget(left)

        # 右侧：按钮区域
        sidebar_w = get_sidebar_width()
        right = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=sidebar_w,
            spacing=d(14),
            padding=[d(8), d(40)]
        )

        right.add_widget(Widget(size_hint_y=0.2))

        btn_font = s(17)
        btn_h = d(48)
        for btn in self._buttons:
            btn.size_hint_x = 1
            btn.size_hint_y = None
            btn.height = btn_h
            btn.font_size = btn_font
            right.add_widget(btn)

        right.add_widget(Widget(size_hint_y=0.4))

        self.root.add_widget(right)

    def _refresh_sizes(self):
        if self._current_layout == 'portrait':
            self.label_title.font_size = s(42)
            self.label_title.height = d(70)
            self.label_sub.font_size = s(15)
            self.label_sub.height = d(25)
            for btn in self._buttons:
                btn.font_size = s(19)
                btn.height = d(50)
        elif self._current_layout == 'landscape':
            self.label_title.font_size = s(36)
            self.label_title.height = d(60)
            self.label_sub.font_size = s(14)
            for btn in self._buttons:
                btn.font_size = s(17)
                btn.height = d(48)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_window_resize(self, width, height):
        if not hasattr(self, 'label_title'):
            return
        self._rebuild_layout()
        self._refresh_sizes()

    def _on_pvp(self, instance):
        self.manager.current = 'game'
        self.manager.get_screen('game').start_pvp()

    def _on_pve(self, instance):
        self.manager.current = 'settings'

    def _on_rules(self, instance):
        self.manager.current = 'rules'

    def _on_users(self, instance):
        self.manager.current = 'users'

    def _update_user_label(self):
        """更新当前用户显示"""
        name = user_manager.get_current_user()
        if name:
            self.label_user.text = f'当前用户：{name}'
        else:
            self.label_user.text = '未登录（请先添加用户）'

    def on_enter(self):
        """每次进入菜单时刷新用户显示"""
        if hasattr(self, 'label_user'):
            self._update_user_label()
