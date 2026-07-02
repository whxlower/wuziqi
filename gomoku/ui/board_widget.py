"""
棋盘绘制与交互组件 — 自适应分辨率
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty
from game_logic import GomokuBoard, Stone
from fonts import get_grid_margins


class BoardWidget(Widget):
    """五子棋棋盘组件，自动适配父容器尺寸"""

    grid_size = NumericProperty(17)
    cell_size = NumericProperty(0)
    board_offset_x = NumericProperty(0)
    board_offset_y = NumericProperty(0)
    show_forbidden = BooleanProperty(False)
    show_last_move = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = GomokuBoard()
        self.bind(size=self._redraw, pos=self._redraw)

    def _redraw(self, *args):
        self.canvas.before.clear()
        self.canvas.clear()

        if self.width < 50 or self.height < 50:
            return

        # 自适应：根据设备类型和可用空间计算格子大小
        margin_ratio = get_grid_margins()
        margin = min(self.width, self.height) * margin_ratio
        available = min(self.width, self.height) - 2 * margin
        self.cell_size = available / (self.grid_size - 1)

        board_pixel_size = self.cell_size * (self.grid_size - 1)
        self.board_offset_x = self.x + (self.width - board_pixel_size) / 2
        self.board_offset_y = self.y + (self.height - board_pixel_size) / 2

        # 动态线宽和标记大小
        line_w = max(dp(0.8), self.cell_size * 0.025)
        star_r = max(dp(2), self.cell_size * 0.08)
        stone_radius = self.cell_size * 0.42
        highlight_r = stone_radius * 0.45
        last_mark_r = max(dp(3), self.cell_size * 0.1)
        forbidden_offset = max(dp(3.5), self.cell_size * 0.12)

        with self.canvas.before:
            # 木色背景
            Color(0.85, 0.72, 0.50, 1)
            Rectangle(
                pos=(self.board_offset_x - self.cell_size / 2,
                     self.board_offset_y - self.cell_size / 2),
                size=(board_pixel_size + self.cell_size,
                      board_pixel_size + self.cell_size)
            )

        with self.canvas:
            # 网格线
            Color(0.3, 0.2, 0.1, 1)
            for i in range(self.grid_size):
                y = self.board_offset_y + i * self.cell_size
                Line(points=[self.board_offset_x, y,
                             self.board_offset_x + board_pixel_size, y],
                     width=line_w)
                x = self.board_offset_x + i * self.cell_size
                Line(points=[x, self.board_offset_y,
                             x, self.board_offset_y + board_pixel_size],
                     width=line_w)

            # 星位
            star_points = [(3,3),(3,8),(3,13),(8,3),(8,8),(8,13),(13,3),(13,8),(13,13)]
            Color(0.3, 0.2, 0.1, 1)
            for r, c in star_points:
                sx = self.board_offset_x + c * self.cell_size
                sy = self.board_offset_y + r * self.cell_size
                Ellipse(pos=(sx - star_r, sy - star_r), size=(star_r * 2, star_r * 2))

            # 棋子
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    stone = self.board.get_stone(r, c)
                    if stone != Stone.EMPTY:
                        self._draw_stone(r, c, stone, stone_radius, highlight_r)

            # 最后一手标记
            if self.show_last_move and self.board.move_history:
                lr, lc = self.board.move_history[-1]
                lx = self.board_offset_x + lc * self.cell_size
                ly = self.board_offset_y + lr * self.cell_size
                Color(1, 0, 0, 0.8)
                Ellipse(pos=(lx - last_mark_r, ly - last_mark_r),
                        size=(last_mark_r * 2, last_mark_r * 2))

            # 禁手标记
            if self.show_forbidden and self.board.current_player == Stone.BLACK:
                for fr, fc, _ in self.board.get_forbidden_moves():
                    fx = self.board_offset_x + fc * self.cell_size
                    fy = self.board_offset_y + fr * self.cell_size
                    Color(1, 0, 0, 0.4)
                    Line(points=[fx - forbidden_offset, fy - forbidden_offset,
                                 fx + forbidden_offset, fy + forbidden_offset],
                         width=line_w * 1.2)
                    Line(points=[fx - forbidden_offset, fy + forbidden_offset,
                                 fx + forbidden_offset, fy - forbidden_offset],
                         width=line_w * 1.2)

    def _draw_stone(self, row, col, stone, radius, highlight_r):
        sx = self.board_offset_x + col * self.cell_size
        sy = self.board_offset_y + row * self.cell_size

        if stone == Stone.BLACK:
            Color(0.15, 0.15, 0.15, 1)
            Ellipse(pos=(sx - radius, sy - radius), size=(radius * 2, radius * 2))
            Color(0.35, 0.35, 0.35, 0.6)
            Ellipse(pos=(sx - highlight_r * 0.6, sy - highlight_r * 0.2),
                    size=(highlight_r, highlight_r))
        else:
            Color(0.95, 0.95, 0.95, 1)
            Ellipse(pos=(sx - radius, sy - radius), size=(radius * 2, radius * 2))
            border_w = max(dp(0.8), self.cell_size * 0.02)
            Color(0.4, 0.4, 0.4, 1)
            Line(circle=(sx, sy, radius), width=border_w)

    def _pos_to_grid(self, touch_x, touch_y):
        if self.cell_size == 0:
            return None, None
        col = round((touch_x - self.board_offset_x) / self.cell_size)
        row = round((touch_y - self.board_offset_y) / self.cell_size)
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            cx = self.board_offset_x + col * self.cell_size
            cy = self.board_offset_y + row * self.cell_size
            dist = ((touch_x - cx) ** 2 + (touch_y - cy) ** 2) ** 0.5
            if dist <= self.cell_size * 0.45:
                return row, col
        return None, None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            row, col = self._pos_to_grid(touch.x, touch.y)
            if row is not None and hasattr(self, 'on_move'):
                self.on_move(row, col)
                return True
        return super().on_touch_down(touch)

    def reset(self):
        self.board.reset()
        self._redraw()

    def refresh(self):
        self._redraw()
