"""
用户管理页面 — 增删用户、查看/删除战绩
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fonts import FONT_NAME, s, d, is_landscape
import user_manager


class UserScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_layout = None
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
        self._current_layout = orientation
        self._build_content()

    def _build_content(self):
        """构建页面内容"""
        root = BoxLayout(orientation='vertical', padding=d(12), spacing=d(8))

        # 标题栏
        title_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=d(45), spacing=d(8)
        )
        title_bar.add_widget(Label(
            text='用户管理', font_name=FONT_NAME, font_size=s(24),
            bold=True, color=(0.9, 0.8, 0.5, 1),
            halign='left',
        ))
        btn_add = Button(
            text='+ 添加用户', font_name=FONT_NAME, font_size=s(14),
            size_hint_x=None, width=d(100),
            background_color=(0.3, 0.6, 0.3, 1), background_normal='',
        )
        btn_add.bind(on_press=self._show_add_user)
        title_bar.add_widget(btn_add)
        root.add_widget(title_bar)

        # 用户列表（滚动）
        scroll = ScrollView()
        self.user_list = BoxLayout(
            orientation='vertical', size_hint_y=None,
            spacing=d(6), padding=[d(4), 0]
        )
        self.user_list.bind(minimum_height=self.user_list.setter('height'))
        scroll.add_widget(self.user_list)
        root.add_widget(scroll)

        # 底部按钮
        btn_back = Button(
            text='返回菜单', font_name=FONT_NAME, font_size=s(15),
            size_hint_y=None, height=d(42),
            background_color=(0.4, 0.4, 0.4, 1), background_normal='',
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        root.add_widget(btn_back)

        self.add_widget(root)
        self._refresh_user_list()

    def _refresh_user_list(self):
        """刷新用户列表显示"""
        self.user_list.clear_widgets()
        users = user_manager.get_users()
        current = user_manager.get_current_user()

        if not users:
            self.user_list.add_widget(Label(
                text='暂无用户，点击上方添加',
                font_name=FONT_NAME, font_size=s(14),
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None, height=d(40),
            ))
            return

        for user in users:
            name = user["name"]
            is_current = (name == current)
            self._add_user_row(name, is_current)

    def _add_user_row(self, name, is_current):
        """添加一行用户卡片"""
        bg_color = (0.25, 0.25, 0.3, 1) if is_current else (0.18, 0.18, 0.22, 1)

        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=d(50),
            spacing=d(6), padding=d(6)
        )

        # 用户名 + 当前标记
        display_name = f'● {name}' if is_current else f'   {name}'
        lbl_name = Label(
            text=display_name, font_name=FONT_NAME, font_size=s(15),
            color=(0.9, 0.85, 0.5, 1) if is_current else (0.8, 0.8, 0.8, 1),
            halign='left', size_hint_x=0.4,
        )
        lbl_name.bind(size=lbl_name.setter('text_size'))
        row.add_widget(lbl_name)

        # 战绩统计
        stats = user_manager.get_user_stats(name)
        total_w = sum(s.get("wins", 0) for s in stats.values())
        total_l = sum(s.get("losses", 0) for s in stats.values())
        total_d = sum(s.get("draws", 0) for s in stats.values())

        lbl_stats = Label(
            text=f'胜{total_w} 负{total_l} 平{total_d}',
            font_name=FONT_NAME, font_size=s(12),
            color=(0.6, 0.7, 0.6, 1),
            size_hint_x=0.3,
        )
        row.add_widget(lbl_stats)

        # 操作按钮
        if not is_current:
            btn_sel = Button(
                text='切换', font_name=FONT_NAME, font_size=s(11),
                size_hint_x=None, width=d(55),
                background_color=(0.3, 0.4, 0.6, 1), background_normal='',
            )
            btn_sel.bind(on_press=lambda x, n=name: self._switch_user(n))
            row.add_widget(btn_sel)

        btn_detail = Button(
            text='战绩', font_name=FONT_NAME, font_size=s(11),
            size_hint_x=None, width=d(55),
            background_color=(0.4, 0.5, 0.3, 1), background_normal='',
        )
        btn_detail.bind(on_press=lambda x, n=name: self._show_stats(n))
        row.add_widget(btn_detail)

        btn_del = Button(
            text='删除', font_name=FONT_NAME, font_size=s(11),
            size_hint_x=None, width=d(55),
            background_color=(0.6, 0.2, 0.2, 1), background_normal='',
        )
        btn_del.bind(on_press=lambda x, n=name: self._confirm_delete(n))
        row.add_widget(btn_del)

        # 背景色（用 canvas 画）
        with row.canvas.before:
            Color(*bg_color)
            self._row_rect = Rectangle(pos=row.pos, size=row.size)
        # 绑定 pos/size 更新（闭包问题：用默认参数捕获当前 rect）
        rect = self._row_rect
        row.bind(pos=lambda inst, val, r=rect: setattr(r, 'pos', val),
                 size=lambda inst, val, r=rect: setattr(r, 'size', val))

        self.user_list.add_widget(row)

    def _switch_user(self, name):
        user_manager.set_current_user(name)
        self._refresh_user_list()

    def _show_add_user(self, instance):
        """弹出添加用户对话框"""
        content = BoxLayout(orientation='vertical', padding=d(16), spacing=d(10))

        input_field = TextInput(
            hint_text='输入用户名',
            font_name=FONT_NAME, font_size=s(15),
            multiline=False,
            size_hint_y=None, height=d(42),
        )
        content.add_widget(input_field)

        lbl_msg = Label(
            text='', font_name=FONT_NAME, font_size=s(12),
            color=(1, 0.4, 0.4, 1),
            size_hint_y=None, height=d(20),
        )
        content.add_widget(lbl_msg)

        btn_layout = BoxLayout(
            orientation='horizontal', spacing=d(10),
            size_hint_y=None, height=d(38)
        )
        btn_ok = Button(
            text='确定', font_name=FONT_NAME, font_size=s(14),
            background_color=(0.3, 0.6, 0.3, 1), background_normal='',
        )
        btn_cancel = Button(
            text='取消', font_name=FONT_NAME, font_size=s(14),
            background_color=(0.4, 0.4, 0.4, 1), background_normal='',
        )
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)

        popup = Popup(
            title='添加用户', content=content,
            size_hint=(0.8, 0.3), auto_dismiss=False,
            title_font=FONT_NAME, title_size=s(16),
        )

        def do_add(instance):
            ok, msg = user_manager.add_user(input_field.text)
            if ok:
                popup.dismiss()
                self._refresh_user_list()
            else:
                lbl_msg.text = msg

        btn_ok.bind(on_press=do_add)
        btn_cancel.bind(on_press=popup.dismiss)
        input_field.bind(on_text_validate=do_add)
        popup.open()

    def _show_stats(self, name):
        """弹出用户战绩详情"""
        stats = user_manager.get_user_stats(name)

        content = BoxLayout(orientation='vertical', padding=d(16), spacing=d(8))

        mode_names = {
            'pvp': '人人对战',
            'pve_easy': '人机·简单',
            'pve_medium': '人机·中等',
            'pve_hard': '人机·困难',
        }

        for mode_key, mode_label in mode_names.items():
            ms = stats.get(mode_key, {})
            w = ms.get("wins", 0)
            l = ms.get("losses", 0)
            dr = ms.get("draws", 0)
            total = w + l + dr
            if total == 0:
                continue

            row = BoxLayout(
                orientation='horizontal', size_hint_y=None, height=d(30)
            )
            row.add_widget(Label(
                text=mode_label, font_name=FONT_NAME, font_size=s(13),
                color=(0.8, 0.8, 0.8, 1), halign='left',
            ))
            row.add_widget(Label(
                text=f'胜{w}  负{l}  平{dr}  共{total}局',
                font_name=FONT_NAME, font_size=s(13),
                color=(0.6, 0.8, 0.6, 1), halign='right',
            ))
            content.add_widget(row)

        # 检查是否有战绩
        has_stats = any(stats.get(k, {}).get("wins", 0) +
                        stats.get(k, {}).get("losses", 0) +
                        stats.get(k, {}).get("draws", 0) > 0
                        for k in mode_names)
        if not has_stats:
            content.add_widget(Label(
                text='暂无对局记录', font_name=FONT_NAME, font_size=s(14),
                color=(0.5, 0.5, 0.5, 1),
            ))

        btn_layout = BoxLayout(
            orientation='horizontal', spacing=d(10),
            size_hint_y=None, height=d(38)
        )
        btn_reset = Button(
            text='重置战绩', font_name=FONT_NAME, font_size=s(13),
            background_color=(0.6, 0.3, 0.2, 1), background_normal='',
        )
        btn_close = Button(
            text='关闭', font_name=FONT_NAME, font_size=s(13),
            background_color=(0.4, 0.4, 0.4, 1), background_normal='',
        )
        btn_layout.add_widget(btn_reset)
        btn_layout.add_widget(btn_close)
        content.add_widget(btn_layout)

        popup = Popup(
            title=f'{name} 的战绩', content=content,
            size_hint=(0.8, 0.55), auto_dismiss=False,
            title_font=FONT_NAME, title_size=s(16),
        )

        def do_reset(instance):
            user_manager.reset_user_stats(name)
            popup.dismiss()
            self._refresh_user_list()

        btn_reset.bind(on_press=do_reset)
        btn_close.bind(on_press=popup.dismiss)
        popup.open()

    def _confirm_delete(self, name):
        """确认删除用户"""
        content = BoxLayout(orientation='vertical', padding=d(16), spacing=d(12))
        content.add_widget(Label(
            text=f'确定删除用户 "{name}" ？\n删除后战绩将无法恢复。',
            font_name=FONT_NAME, font_size=s(14),
            color=(0.9, 0.7, 0.7, 1),
        ))

        btn_layout = BoxLayout(
            orientation='horizontal', spacing=d(10),
            size_hint_y=None, height=d(38)
        )
        btn_yes = Button(
            text='确定删除', font_name=FONT_NAME, font_size=s(14),
            background_color=(0.7, 0.2, 0.2, 1), background_normal='',
        )
        btn_no = Button(
            text='取消', font_name=FONT_NAME, font_size=s(14),
            background_color=(0.4, 0.4, 0.4, 1), background_normal='',
        )
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)
        content.add_widget(btn_layout)

        popup = Popup(
            title='确认删除', content=content,
            size_hint=(0.75, 0.28), auto_dismiss=False,
            title_font=FONT_NAME, title_size=s(16),
        )

        def do_delete(instance):
            user_manager.delete_user(name)
            popup.dismiss()
            self._refresh_user_list()

        btn_yes.bind(on_press=do_delete)
        btn_no.bind(on_press=popup.dismiss)
        popup.open()

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_window_resize(self, width, height):
        if not hasattr(self, 'user_list'):
            return
        self._rebuild_layout()

    def on_enter(self):
        """每次进入页面时刷新用户列表"""
        if hasattr(self, 'user_list'):
            self._refresh_user_list()
