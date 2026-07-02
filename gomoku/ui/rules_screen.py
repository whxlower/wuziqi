"""
禁手说明页面 — 竖屏/横屏自适应
竖屏：单列滚动
横屏：增加左右内边距，避免内容拉伸过宽
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fonts import FONT_NAME, s, d, is_landscape


class RulesScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_layout = None
        self.rule_labels = []
        Clock.schedule_once(self._init_ui, 0)

    def _init_ui(self, dt):
        self._build_ui()

    def _build_ui(self):
        with self.canvas.before:
            Color(0.12, 0.12, 0.15, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self._rebuild_layout()

    def _rebuild_layout(self):
        orientation = 'landscape' if is_landscape() else 'portrait'
        if orientation == self._current_layout:
            return

        self.clear_widgets()

        root = BoxLayout(orientation='vertical', padding=d(12))

        self.label_title = Label(
            text='禁手规则说明',
            font_name=FONT_NAME,
            font_size=s(26),
            bold=True,
            color=(0.9, 0.8, 0.5, 1),
            size_hint_y=None,
            height=d(45)
        )
        root.add_widget(self.label_title)

        # 横屏时左右留白，避免内容过宽
        if orientation == 'landscape':
            h_layout = BoxLayout(orientation='horizontal', spacing=d(12))
            h_layout.add_widget(Widget(size_hint_x=0.15))
            scroll = self._create_scroll_content()
            h_layout.add_widget(scroll)
            h_layout.add_widget(Widget(size_hint_x=0.15))
            root.add_widget(h_layout)
        else:
            scroll = self._create_scroll_content()
            root.add_widget(scroll)

        self.btn_back = Button(
            text='返回菜单',
            font_name=FONT_NAME,
            font_size=s(16),
            size_hint_y=None,
            height=d(45),
            background_color=(0.4, 0.4, 0.4, 1),
            background_normal='',
            color=(0.9, 0.9, 0.9, 1),
        )
        self.btn_back.bind(on_press=self._on_back)
        root.add_widget(self.btn_back)

        self.add_widget(root)
        self._current_layout = orientation
        Clock.schedule_once(lambda dt: self._refresh_sizes(), 0)

    def _create_scroll_content(self):
        """创建滚动内容区域"""
        scroll = ScrollView()

        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=d(12),
            padding=[d(8), 0]
        )
        content.bind(minimum_height=content.setter('height'))

        rules = [
            ('禁手概述',
             '在五子棋（Renju）正式规则中，为了平衡先后手优势，'
             '对先手方（黑方）设置了禁手限制。\n\n'
             '禁手仅针对黑方，白方不受任何禁手限制。\n'
             '黑方落子时，必须避开禁手位置，否则判为违规，落子无效。\n\n'
             '重要规则：五连优先 —— 如果黑方在禁手位置恰好形成五连，'
             '则以五连获胜论，不判禁手。'),
            ('三三禁手',
             '定义：黑方一步棋同时形成两个或两个以上的"活三"。\n\n'
             '什么是活三？\n'
             '  连续三颗同色棋子排成一线，且两端均为空位，'
             '下一步可以形成"活四"（四连两端空）的形态。\n\n'
             '  ···_bbb_···\n\n'
             '  b为黑子，_为空位。当黑方落子后同时在两个方向形成活三，'
             '即为三三禁手。\n\n'
             '注意：如果其中一个"三"是眠三（一端被堵），则不构成三三禁手。'),
            ('四四禁手',
             '定义：黑方一步棋同时形成两个或两个以上的"四"。\n\n'
             '四的类型：\n'
             '  活四：四连两端均空，必胜形态\n'
             '  冲四：四连一端被堵，只能从另一端阻挡\n\n'
             '当黑方落子后同时在两个方向形成四（活四或冲四），'
             '即为四四禁手。\n\n'
             '注意：双活四、活四+冲四、双冲四，都算四四禁手。'),
            ('长连禁手',
             '定义：黑方一步棋形成六颗或六颗以上连续同色棋子。\n\n'
             '五子棋要求恰好五连获胜。黑方形成六连或更长的连珠，'
             '属于长连禁手，判为违规。\n\n'
             '白方无此限制，白方六连仍然判胜。\n\n'
             '这与"五连优先"规则配合：如果黑方落子位置恰好形成五连，'
             '即使同时构成长连，也以五连获胜论。'),
            ('五连优先规则',
             '当黑方在某个位置同时满足"禁手"和"五连"条件时，'
             '以五连获胜为优先，不判禁手。\n\n'
             '这是为了保证黑方的获胜权利不被禁手规则剥夺。\n\n'
             '例如：如果黑方某步棋既形成了三三又恰好五连，'
             '则判黑方获胜，而非三三禁手。'),
            ('为什么要有禁手？',
             '五子棋先手优势极大。如果没有禁手规则，黑方（先手）'
             '可以通过特定开局必胜。\n\n'
             '禁手规则的存在是为了：\n'
             '  1. 平衡先后手优势，增加公平性\n'
             '  2. 提高比赛的策略深度和观赏性\n'
             '  3. 让白方有更多反击机会\n\n'
             '在本游戏中，禁手仅对玩家执黑时生效。'
             'AI 执黑时也会遵守禁手规则。'),
        ]

        self.rule_labels = []
        for title, text in rules:
            rule_title = Label(
                text='[b]' + title + '[/b]',
                font_name=FONT_NAME,
                font_size=s(18),
                markup=True,
                color=(0.9, 0.7, 0.3, 1),
                size_hint_y=None,
                height=d(30),
                halign='left',
                valign='middle',
                text_size=(None, None),
            )
            content.add_widget(rule_title)

            rule_text = Label(
                text=text,
                font_name=FONT_NAME,
                font_size=s(14),
                color=(0.85, 0.85, 0.85, 1),
                size_hint_y=None,
                halign='left',
                valign='top',
                text_size=(None, None),
                line_height=1.3,
            )
            rule_text.bind(
                width=lambda inst, val: inst.setter('text_size')(inst, (val, None)),
                texture_size=lambda inst, val: inst.setter('height')(inst, val[1] + d(8))
            )
            content.add_widget(rule_text)
            self.rule_labels.extend([rule_title, rule_text])

        scroll.add_widget(content)
        return scroll

    def _refresh_sizes(self):
        self.label_title.font_size = s(26)
        self.btn_back.font_size = s(16)
        self.btn_back.height = d(45)
        for lbl in self.rule_labels:
            if lbl.markup:
                lbl.font_size = s(18)
            else:
                lbl.font_size = s(14)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_window_resize(self, width, height):
        if not hasattr(self, 'label_title'):
            return
        self._rebuild_layout()
        self._refresh_sizes()

    def _on_back(self, instance):
        self.manager.current = 'menu'
