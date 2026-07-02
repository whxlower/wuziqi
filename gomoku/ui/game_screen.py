"""
游戏对局界面 — 竖屏/横屏自适应布局
修复：AI 思考时彻底阻断用户操作 + 战绩追踪
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

import sys, os
import threading
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fonts import (FONT_NAME, s, d, is_landscape, get_bottom_bar_height,
                   get_sidebar_width, get_sidebar_font_scale)
from game_logic import Stone
from ai import GomokuAI
from ui.board_widget import BoardWidget
import user_manager


class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = 'pvp'
        self.ai = None
        self.ai_thinking = False
        self._ai_lock = threading.Lock()  # AI 状态锁
        self._current_layout = None
        self._player_color = 'black'  # 用户执子颜色
        self._difficulty = 'medium'
        Clock.schedule_once(self._init_ui, 0)

    def _init_ui(self, dt):
        self._build_ui()

    # ── 布局构建 ──────────────────────────────────────────────

    def _build_ui(self):
        with self.canvas.before:
            Color(0.15, 0.15, 0.18, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self._create_widgets()
        self._rebuild_layout()

    def _create_widgets(self):
        self.label_turn = Label(
            text='黑方落子', font_name=FONT_NAME, font_size=s(17),
            bold=True, color=(0.9, 0.8, 0.5, 1),
            halign='left', valign='middle',
        )
        self.label_turn.bind(size=self.label_turn.setter('text_size'))

        self.label_mode = Label(
            text='人人对战', font_name=FONT_NAME, font_size=s(13),
            color=(0.6, 0.6, 0.6, 1),
            halign='right', valign='middle',
        )
        self.label_mode.bind(size=self.label_mode.setter('text_size'))

        self.board_container = FloatLayout()
        self.board_widget = BoardWidget()
        self.board_widget.on_move = self._on_player_move
        self.board_container.add_widget(self.board_widget)

        self.btn_forbidden = Button(
            text='显示禁手', font_name=FONT_NAME, font_size=s(12),
            background_color=(0.5, 0.3, 0.2, 1), background_normal='',
        )
        self.btn_forbidden.bind(on_press=self._toggle_forbidden)

        self.btn_undo = Button(
            text='悔棋', font_name=FONT_NAME, font_size=s(12),
            background_color=(0.4, 0.4, 0.4, 1), background_normal='',
        )
        self.btn_undo.bind(on_press=self._on_undo)

        self.btn_restart = Button(
            text='重开', font_name=FONT_NAME, font_size=s(12),
            background_color=(0.3, 0.5, 0.3, 1), background_normal='',
        )
        self.btn_restart.bind(on_press=self._on_restart)

        self.btn_menu = Button(
            text='菜单', font_name=FONT_NAME, font_size=s(12),
            background_color=(0.5, 0.2, 0.2, 1), background_normal='',
        )
        self.btn_menu.bind(on_press=self._on_menu)

        self._buttons = [self.btn_forbidden, self.btn_undo,
                         self.btn_restart, self.btn_menu]

    def _rebuild_layout(self):
        orientation = 'landscape' if is_landscape() else 'portrait'
        if orientation == self._current_layout:
            return

        self.clear_widgets()
        self.root = BoxLayout()
        bar_h = get_bottom_bar_height()

        if orientation == 'landscape':
            self._build_landscape_layout(bar_h)
        else:
            self._build_portrait_layout(bar_h)

        self.add_widget(self.root)
        self._current_layout = orientation
        Clock.schedule_once(lambda dt: self._refresh_sizes(), 0)

    def _build_portrait_layout(self, bar_h):
        self.root.orientation = 'vertical'
        self.root.padding = d(6)
        self.root.spacing = d(4)

        self.top_bar = BoxLayout(
            orientation='horizontal', size_hint_y=None,
            height=bar_h - d(4), spacing=d(8)
        )
        self.label_turn.halign = 'left'
        self.label_mode.halign = 'right'
        self.top_bar.add_widget(self.label_turn)
        self.top_bar.add_widget(self.label_mode)
        self.root.add_widget(self.top_bar)

        self.root.add_widget(self.board_container)

        self.bottom_bar = BoxLayout(
            orientation='horizontal', size_hint_y=None,
            height=bar_h, spacing=d(5)
        )
        for btn, hint_x in zip(self._buttons, [0.3, 0.2, 0.2, 0.2]):
            btn.size_hint_x = hint_x
            btn.size_hint_y = 1
            btn.font_size = s(12)
            self.bottom_bar.add_widget(btn)
        self.root.add_widget(self.bottom_bar)

    def _build_landscape_layout(self, bar_h):
        self.root.orientation = 'horizontal'
        self.root.padding = d(6)
        self.root.spacing = d(6)

        self.root.add_widget(self.board_container)

        sidebar_w = get_sidebar_width()
        sf = get_sidebar_font_scale()

        right_panel = BoxLayout(
            orientation='vertical', size_hint_x=None, width=sidebar_w,
            spacing=d(8), padding=[d(4), d(8)]
        )

        info_box = BoxLayout(
            orientation='vertical', size_hint_y=None, height=d(80), spacing=d(4)
        )
        self.label_turn.halign = 'center'
        self.label_turn.font_size = s(15) * sf
        self.label_turn.size_hint_y = 0.6
        info_box.add_widget(self.label_turn)
        self.label_mode.halign = 'center'
        self.label_mode.font_size = s(11) * sf
        self.label_mode.size_hint_y = 0.4
        info_box.add_widget(self.label_mode)
        right_panel.add_widget(info_box)

        sep = Widget(size_hint_y=None, height=d(2))
        right_panel.add_widget(sep)
        right_panel.add_widget(Widget(size_hint_y=0.15))

        btn_h = d(42)
        btn_font = s(13) * sf
        for btn in self._buttons:
            btn.size_hint_x = 1
            btn.size_hint_y = None
            btn.height = btn_h
            btn.font_size = btn_font
            right_panel.add_widget(btn)

        right_panel.add_widget(Widget(size_hint_y=0.3))
        self.root.add_widget(right_panel)

    def _refresh_sizes(self):
        bar_h = get_bottom_bar_height()
        if self._current_layout == 'landscape':
            sf = get_sidebar_font_scale()
            self.label_turn.font_size = s(15) * sf
            self.label_mode.font_size = s(11) * sf
            btn_font = s(13) * sf
            btn_h = d(42)
            for btn in self._buttons:
                btn.font_size = btn_font
                btn.height = btn_h
        elif self._current_layout == 'portrait':
            if hasattr(self, 'top_bar'):
                self.top_bar.height = bar_h - d(4)
            if hasattr(self, 'bottom_bar'):
                self.bottom_bar.height = bar_h
            self.label_turn.font_size = s(17)
            self.label_mode.font_size = s(13)
            for btn in self._buttons:
                btn.font_size = s(12)
        self.board_widget.refresh()

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_window_resize(self, width, height):
        if not hasattr(self, 'board_widget'):
            return
        self._rebuild_layout()
        self._refresh_sizes()

    # ── 游戏控制 ──────────────────────────────────────────────

    def start_pvp(self):
        self.mode = 'pvp'
        self.ai = None
        self._player_color = 'black'
        self.board_widget.board.reset()
        self.board_widget.show_forbidden = False
        self.label_mode.text = '人人对战'
        self.btn_forbidden.text = '显示禁手'
        self.board_widget.refresh()
        self._update_turn_label()

    def start_pve(self, player_color: str, difficulty: str):
        self.mode = 'pve'
        self._player_color = player_color
        self._difficulty = difficulty
        ai_color = Stone.WHITE if player_color == 'black' else Stone.BLACK
        self.ai = GomokuAI(ai_color, difficulty)
        self.board_widget.board.reset()
        self.board_widget.show_forbidden = (player_color == 'black')
        diff_name = {'easy': '简单', 'medium': '中等', 'hard': '困难'}.get(difficulty, '中等')
        self.label_mode.text = f'人机 · {diff_name}'
        self.btn_forbidden.text = '隐藏禁手' if self.board_widget.show_forbidden else '显示禁手'

        with self._ai_lock:
            self.ai_thinking = False

        self.board_widget.refresh()
        self._update_turn_label()

        # AI 先手时启动后台线程
        if ai_color == Stone.BLACK:
            self._start_ai_turn()

    def _start_ai_turn(self):
        """启动 AI 回合（线程安全）"""
        with self._ai_lock:
            if self.ai_thinking:
                return
            self.ai_thinking = True

        self._ai_start_time = time.time()
        self.label_turn.text = 'AI 思考中...'
        self._set_buttons_enabled(False)
        # 启动计时器更新显示
        self._ai_timer_event = Clock.schedule_interval(self._update_ai_timer, 0.3)
        # 安全阀：超时强制结束
        self._ai_timeout_event = Clock.schedule_once(self._ai_force_done, 8)
        threading.Thread(target=self._ai_compute, daemon=True).start()

    def _ai_force_done(self, dt):
        """安全阀：AI 超时，用快速评分选一个较优位置落子"""
        with self._ai_lock:
            if not self.ai_thinking:
                return
            self.ai_thinking = False
        if hasattr(self, '_ai_timer_event'):
            self._ai_timer_event.cancel()
        self._set_buttons_enabled(True)

        board = self.board_widget.board
        if board.game_over:
            return

        # 用 AI 的快速评分选最佳候选点
        best_move = self._ai_pick_fallback_move(board)
        if best_move:
            row, col = best_move
            board.place_stone(row, col)
            self.board_widget.refresh()
            self._update_turn_label()
            if board.game_over:
                self._record_and_show_result(board)

    def _ai_pick_fallback_move(self, board):
        """快速评分选一个较优位置（不走搜索树）"""
        candidates = set()
        for r in range(board.SIZE):
            for c in range(board.SIZE):
                if board.board[r][c] != Stone.EMPTY:
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < board.SIZE and 0 <= nc < board.SIZE
                                    and board.board[nr][nc] == Stone.EMPTY):
                                candidates.add((nr, nc))
        if not candidates:
            return (8, 8)

        # 先检查必胜/必防
        for r, c in candidates:
            board.board[r][c] = self.ai.ai_color
            if board.check_win(r, c):
                board.board[r][c] = Stone.EMPTY
                return (r, c)
            board.board[r][c] = Stone.EMPTY
        for r, c in candidates:
            board.board[r][c] = self.ai.human_color
            if board.check_win(r, c):
                board.board[r][c] = Stone.EMPTY
                return (r, c)
            board.board[r][c] = Stone.EMPTY

        # 按快速评分排序取最优
        scored = []
        for (r, c) in candidates:
            score = self.ai._quick_score(board, r, c)
            scored.append((score, r, c))
        scored.sort(reverse=True)
        return (scored[0][1], scored[0][2]) if scored else (8, 8)

    def _update_ai_timer(self, dt):
        """定时更新 AI 思考时间显示"""
        if not self.ai_thinking:
            return False  # 停止计时器
        elapsed = time.time() - self._ai_start_time
        self.label_turn.text = f'AI 思考中... {elapsed:.1f}s'
        return True

    def _set_buttons_enabled(self, enabled):
        """启用/禁用按钮（悔棋、重开、菜单）"""
        alpha = 1.0 if enabled else 0.4
        for btn in (self.btn_undo, self.btn_restart, self.btn_menu):
            btn.disabled = not enabled
            btn.background_color = (*btn.background_color[:3], alpha)

    def _on_player_move(self, row: int, col: int):
        """玩家点击棋盘"""
        # 严格检查：AI 思考中一律拒绝
        with self._ai_lock:
            if self.ai_thinking:
                return

        board = self.board_widget.board

        # PvE 模式下，轮到 AI 时拒绝用户操作
        if self.mode == 'pve' and board.current_player == self.ai.ai_color:
            return

        success, msg = board.place_stone(row, col)
        if not success:
            self._show_message('提示', msg)
            return

        self.board_widget.refresh()
        self._update_turn_label()

        if board.game_over:
            self._record_and_show_result(board)
            return

        # PvE：轮到 AI
        if self.mode == 'pve' and board.current_player == self.ai.ai_color:
            self._start_ai_turn()

    def _ai_compute(self):
        """后台线程：AI 计算"""
        board = self.board_widget.board
        if board.game_over:
            with self._ai_lock:
                self.ai_thinking = False
            Clock.schedule_once(lambda dt: self._set_buttons_enabled(True), 0)
            return

        row, col = self.ai.get_best_move(board)
        Clock.schedule_once(lambda dt, r=row, c=col: self._ai_apply_move(r, c), 0)

    def _ai_apply_move(self, row, col):
        """主线程：应用 AI 落子"""
        # 停止计时器和安全阀
        if hasattr(self, '_ai_timer_event'):
            self._ai_timer_event.cancel()
        if hasattr(self, '_ai_timeout_event'):
            self._ai_timeout_event.cancel()

        board = self.board_widget.board
        if board.game_over:
            with self._ai_lock:
                self.ai_thinking = False
            self._set_buttons_enabled(True)
            return

        board.place_stone(row, col)

        with self._ai_lock:
            self.ai_thinking = False

        self._set_buttons_enabled(True)
        self.board_widget.refresh()
        self._update_turn_label()

        if board.game_over:
            self._record_and_show_result(board)

    def _record_and_show_result(self, board):
        """记录战绩并显示结果"""
        # 确定模式键
        if self.mode == 'pvp':
            mode_key = 'pvp'
        else:
            mode_key = f'pve_{self._difficulty}'

        user_is_black = (self._player_color == 'black')
        user_manager.record_game_result(mode_key, board.winner, user_is_black)
        self._show_result(board)

    def _update_turn_label(self):
        board = self.board_widget.board
        if board.game_over:
            return
        player_name = '黑方' if board.current_player == Stone.BLACK else '白方'
        if self.mode == 'pve':
            if board.current_player == self.ai.ai_color:
                self.label_turn.text = f'{player_name} | AI 思考中...'
            else:
                self.label_turn.text = f'{player_name} | 你的回合'
        else:
            self.label_turn.text = f'{player_name}落子'

    def _toggle_forbidden(self, instance):
        self.board_widget.show_forbidden = not self.board_widget.show_forbidden
        self.btn_forbidden.text = '隐藏禁手' if self.board_widget.show_forbidden else '显示禁手'
        self.board_widget.refresh()

    def _on_undo(self, instance):
        with self._ai_lock:
            if self.ai_thinking:
                return
        board = self.board_widget.board
        if board.game_over:
            return
        if self.mode == 'pve':
            board.undo()
            board.undo()
        else:
            board.undo()
        self.board_widget.refresh()
        self._update_turn_label()

    def _on_restart(self, instance):
        with self._ai_lock:
            if self.ai_thinking:
                return
        if self.mode == 'pvp':
            self.start_pvp()
        else:
            self.start_pve(self._player_color, self._difficulty)

    def _on_menu(self, instance):
        with self._ai_lock:
            if self.ai_thinking:
                return
        self.manager.current = 'menu'

    def _show_result(self, board):
        if board.winner:
            if self.mode == 'pve':
                if board.winner == self.ai.ai_color:
                    title, msg = 'AI 获胜', 'AI 赢了这局！再来一局？'
                else:
                    title, msg = '恭喜获胜', '你赢了！再来一局？'
            else:
                winner_name = '黑方' if board.winner == Stone.BLACK else '白方'
                title = f'{winner_name}获胜'
                msg = f'{winner_name}五子连珠！再来一局？'
        else:
            title, msg = '平局', '棋盘已满，平局！再来一局？'

        content = BoxLayout(orientation='vertical', padding=d(18), spacing=d(12))
        content.add_widget(Label(
            text=msg, font_name=FONT_NAME, font_size=s(15),
            color=(0.8, 0.8, 0.8, 1),
        ))
        btn_layout = BoxLayout(
            orientation='horizontal', spacing=d(12),
            size_hint_y=None, height=d(42)
        )
        btn_again = Button(
            text='再来一局', font_name=FONT_NAME, font_size=s(15),
            background_color=(0.3, 0.6, 0.3, 1), background_normal='',
        )
        btn_back = Button(
            text='返回菜单', font_name=FONT_NAME, font_size=s(15),
            background_color=(0.4, 0.4, 0.4, 1), background_normal='',
        )
        btn_layout.add_widget(btn_again)
        btn_layout.add_widget(btn_back)
        content.add_widget(btn_layout)

        popup = Popup(
            title=title, content=content,
            size_hint=(0.75, 0.35), auto_dismiss=False,
            title_font=FONT_NAME, title_size=s(18),
        )
        btn_again.bind(on_press=lambda x: (popup.dismiss(), self._on_restart(None)))
        btn_back.bind(on_press=lambda x: (popup.dismiss(), self._on_menu(None)))
        popup.open()

    def _show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=d(12), spacing=d(8))
        content.add_widget(Label(
            text=message, font_name=FONT_NAME, font_size=s(14),
            color=(0.8, 0.8, 0.8, 1),
        ))
        btn_ok = Button(
            text='确定', font_name=FONT_NAME, font_size=s(15),
            size_hint_y=None, height=d(38),
            background_color=(0.3, 0.5, 0.7, 1), background_normal='',
        )
        content.add_widget(btn_ok)

        popup = Popup(
            title=title, content=content,
            size_hint=(0.7, 0.22),
            title_font=FONT_NAME, title_size=s(16),
        )
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
