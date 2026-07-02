"""
设置页面 — 竖屏/横屏自适应
竖屏：纵向排列所有选项
横屏：左侧标题+颜色 / 右侧难度+按钮
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fonts import FONT_NAME, s, d, is_landscape, get_sidebar_width


class SettingsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_color = 'black'
        self.selected_difficulty = 'medium'
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
            text='人机对战设置',
            font_name=FONT_NAME,
            font_size=s(28),
            bold=True,
            color=(0.9, 0.8, 0.5, 1),
            size_hint_y=None,
            height=d(50)
        )

        self.label_color = Label(
            text='选择执子颜色',
            font_name=FONT_NAME,
            font_size=s(16),
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=d(28)
        )

        self.btn_black = ToggleButton(
            text='执黑（先手）',
            font_name=FONT_NAME, font_size=s(15),
            state='down', group='color',
            background_color=(0.3, 0.3, 0.3, 1), background_normal='',
            allow_no_selection=False,
        )
        self.btn_black.bind(on_press=self._on_color_select)

        self.btn_white = ToggleButton(
            text='执白（后手）',
            font_name=FONT_NAME, font_size=s(15),
            state='normal', group='color',
            background_color=(0.3, 0.3, 0.3, 1), background_normal='',
            allow_no_selection=False,
        )
        self.btn_white.bind(on_press=self._on_color_select)

        self.label_diff = Label(
            text='选择难度',
            font_name=FONT_NAME,
            font_size=s(16),
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=None,
            height=d(28)
        )

        self.diff_buttons = {}
        for diff_id, diff_text, diff_color in [
            ('easy', '简单', (0.3, 0.6, 0.3, 1)),
            ('medium', '中等', (0.6, 0.5, 0.2, 1)),
            ('hard', '困难', (0.7, 0.2, 0.2, 1)),
        ]:
            btn = ToggleButton(
                text=diff_text,
                font_name=FONT_NAME, font_size=s(15),
                state='down' if diff_id == 'medium' else 'normal',
                group='difficulty',
                background_color=diff_color, background_normal='',
                allow_no_selection=False,
            )
            btn.bind(on_press=lambda inst, d2=diff_id: self._on_difficulty_select(d2))
            self.diff_buttons[diff_id] = btn

        self.btn_start = Button(
            text='开始对局',
            font_name=FONT_NAME, font_size=s(20),
            size_hint_y=None, height=d(50),
            background_color=(0.3, 0.6, 0.3, 1), background_normal='',
            color=(1, 1, 1, 1), bold=True,
        )
        self.btn_start.bind(on_press=self._on_start)

        self.btn_back = Button(
            text='返回菜单',
            font_name=FONT_NAME, font_size=s(15),
            size_hint_y=None, height=d(42),
            background_color=(0.4, 0.4, 0.4, 1), background_normal='',
            color=(0.9, 0.9, 0.9, 1),
        )
        self.btn_back.bind(on_press=self._on_back)

        self._rebuild_layout()

    def _rebuild_layout(self):
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
        """竖屏：所有选项纵向排列"""
        self.root.orientation = 'vertical'
        self.root.padding = [d(30), d(20)]
        self.root.spacing = d(15)

        self.root.add_widget(Widget(size_hint_y=0.25))
        self.root.add_widget(self.label_title)
        self.root.add_widget(Widget(size_hint_y=0.08))

        # 颜色选择
        self.root.add_widget(self.label_color)
        color_layout = BoxLayout(
            orientation='horizontal', spacing=d(12),
            size_hint_y=None, height=d(46)
        )
        for btn in (self.btn_black, self.btn_white):
            btn.size_hint_x = 1
            btn.size_hint_y = 1
            btn.font_size = s(15)
        color_layout.add_widget(self.btn_black)
        color_layout.add_widget(self.btn_white)
        self.root.add_widget(color_layout)

        # 难度选择
        self.root.add_widget(self.label_diff)
        diff_layout = BoxLayout(
            orientation='horizontal', spacing=d(8),
            size_hint_y=None, height=d(46)
        )
        for btn in self.diff_buttons.values():
            btn.size_hint_x = 1
            btn.size_hint_y = 1
            btn.font_size = s(15)
            diff_layout.add_widget(btn)
        self.root.add_widget(diff_layout)

        self.root.add_widget(Widget(size_hint_y=0.1))

        self.btn_start.size_hint_x = 1
        self.btn_start.font_size = s(20)
        self.btn_start.height = d(50)
        self.root.add_widget(self.btn_start)

        self.btn_back.size_hint_x = 1
        self.btn_back.font_size = s(15)
        self.btn_back.height = d(42)
        self.root.add_widget(self.btn_back)

        self.root.add_widget(Widget(size_hint_y=0.35))

    def _build_landscape(self):
        """横屏：左侧标题+颜色 / 右侧难度+按钮"""
        self.root.orientation = 'horizontal'
        self.root.padding = d(16)
        self.root.spacing = d(16)

        sidebar_w = get_sidebar_width()

        # 左侧
        left = BoxLayout(
            orientation='vertical',
            size_hint_x=0.5,
            spacing=d(12),
            padding=[d(8), d(20)]
        )

        left.add_widget(Widget(size_hint_y=0.2))

        self.label_title.font_size = s(24)
        self.label_title.height = d(45)
        left.add_widget(self.label_title)

        left.add_widget(Widget(size_hint_y=0.1))

        self.label_color.font_size = s(14)
        self.label_color.halign = 'center'
        left.add_widget(self.label_color)

        color_layout = BoxLayout(
            orientation='horizontal', spacing=d(10),
            size_hint_y=None, height=d(42)
        )
        for btn in (self.btn_black, self.btn_white):
            btn.size_hint_x = 1
            btn.size_hint_y = 1
            btn.font_size = s(14)
        color_layout.add_widget(self.btn_black)
        color_layout.add_widget(self.btn_white)
        left.add_widget(color_layout)

        left.add_widget(Widget(size_hint_y=0.4))

        self.root.add_widget(left)

        # 右侧
        right = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=sidebar_w,
            spacing=d(12),
            padding=[d(8), d(20)]
        )

        right.add_widget(Widget(size_hint_y=0.15))

        self.label_diff.font_size = s(14)
        self.label_diff.halign = 'center'
        right.add_widget(self.label_diff)

        btn_h = d(40)
        for btn in self.diff_buttons.values():
            btn.size_hint_x = 1
            btn.size_hint_y = None
            btn.height = btn_h
            btn.font_size = s(14)
            right.add_widget(btn)

        right.add_widget(Widget(size_hint_y=0.1))

        self.btn_start.size_hint_x = 1
        self.btn_start.font_size = s(18)
        self.btn_start.height = d(46)
        right.add_widget(self.btn_start)

        self.btn_back.size_hint_x = 1
        self.btn_back.font_size = s(14)
        self.btn_back.height = d(40)
        right.add_widget(self.btn_back)

        right.add_widget(Widget(size_hint_y=0.25))

        self.root.add_widget(right)

    def _refresh_sizes(self):
        if self._current_layout == 'portrait':
            self.label_title.font_size = s(28)
            self.label_title.height = d(50)
            self.label_color.font_size = s(16)
            self.label_diff.font_size = s(16)
            for btn in (self.btn_black, self.btn_white):
                btn.font_size = s(15)
            for btn in self.diff_buttons.values():
                btn.font_size = s(15)
                btn.height = d(46)
            self.btn_start.font_size = s(20)
            self.btn_start.height = d(50)
            self.btn_back.font_size = s(15)
            self.btn_back.height = d(42)
        elif self._current_layout == 'landscape':
            self.label_title.font_size = s(24)
            self.label_title.height = d(45)
            self.label_color.font_size = s(14)
            self.label_diff.font_size = s(14)
            for btn in (self.btn_black, self.btn_white):
                btn.font_size = s(14)
            for btn in self.diff_buttons.values():
                btn.font_size = s(14)
                btn.height = d(40)
            self.btn_start.font_size = s(18)
            self.btn_start.height = d(46)
            self.btn_back.font_size = s(14)
            self.btn_back.height = d(40)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_window_resize(self, width, height):
        if not hasattr(self, 'label_title'):
            return
        self._rebuild_layout()
        self._refresh_sizes()

    def _on_color_select(self, instance):
        self.selected_color = 'black' if instance == self.btn_black else 'white'

    def _on_difficulty_select(self, diff_id):
        self.selected_difficulty = diff_id

    def _on_start(self, instance):
        self.manager.current = 'game'
        self.manager.get_screen('game').start_pve(
            self.selected_color, self.selected_difficulty
        )

    def _on_back(self, instance):
        self.manager.current = 'menu'
