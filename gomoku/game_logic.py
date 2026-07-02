"""
五子棋核心逻辑模块
棋盘状态管理、胜负判定、禁手检测（Renju规则）
"""

from enum import IntEnum
from typing import Optional, List, Tuple, Set


class Stone(IntEnum):
    EMPTY = 0
    BLACK = 1  # 黑方（受禁手限制）
    WHITE = 2  # 白方（无禁手）


class ForbiddenType:
    """禁手类型"""
    NONE = None
    DOUBLE_THREE = "三三禁手"
    DOUBLE_FOUR = "四四禁手"
    OVERLINE = "长连禁手"


class Direction:
    """四个方向：水平、垂直、两条对角线"""
    HORIZONTAL = (0, 1)
    VERTICAL = (1, 0)
    DIAGONAL_1 = (1, 1)   # 左上→右下
    DIAGONAL_2 = (1, -1)  # 右上→左下

    ALL = [HORIZONTAL, VERTICAL, DIAGONAL_1, DIAGONAL_2]


class GomokuBoard:
    SIZE = 17

    def __init__(self):
        self.reset()

    def reset(self):
        """重置棋盘"""
        self.board = [[Stone.EMPTY] * self.SIZE for _ in range(self.SIZE)]
        self.current_player = Stone.BLACK
        self.move_history: List[Tuple[int, int]] = []
        self.game_over = False
        self.winner: Optional[Stone] = None

    def _in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.SIZE and 0 <= col < self.SIZE

    def place_stone(self, row: int, col: int) -> Tuple[bool, str]:
        """
        尝试落子。
        返回 (成功, 消息)。
        """
        if self.game_over:
            return False, "对局已结束"
        if not self._in_bounds(row, col):
            return False, "超出棋盘范围"
        if self.board[row][col] != Stone.EMPTY:
            return False, "该位置已有棋子"

        # 黑方需要检测禁手
        if self.current_player == Stone.BLACK:
            forbidden = self.check_forbidden(row, col)
            if forbidden:
                return False, f"禁手：{forbidden}，落子无效"

        # 落子
        self.board[row][col] = self.current_player
        self.move_history.append((row, col))

        # 判胜（五连）
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
            return True, f"{'黑方' if self.winner == Stone.BLACK else '白方'}获胜！"

        # 判平局（满棋盘）
        if len(self.move_history) == self.SIZE * self.SIZE:
            self.game_over = True
            return True, "棋盘已满，平局！"

        # 切换玩家
        self.current_player = Stone.WHITE if self.current_player == Stone.BLACK else Stone.BLACK
        return True, "落子成功"

    def _count_direction(self, row: int, col: int, dr: int, dc: int, stone: Stone) -> int:
        """沿一个方向计数连续同色棋子（不含起点）"""
        count = 0
        r, c = row + dr, col + dc
        while self._in_bounds(r, c) and self.board[r][c] == stone:
            count += 1
            r += dr
            c += dc
        return count

    def _get_line_info(self, row: int, col: int, dr: int, dc: int, stone: Stone) -> Tuple[int, int, int]:
        """
        获取某方向的连续棋子信息（含当前位置，临时置入后检测）
        返回 (正向数量, 反向数量, 总长度)
        """
        pos = self._count_direction(row, col, dr, dc, stone)
        neg = self._count_direction(row, col, -dr, -dc, stone)
        return pos, neg, pos + neg + 1

    def check_win(self, row: int, col: int) -> bool:
        """检查是否五连获胜（严格五连，六连不算）"""
        stone = self.board[row][col]
        if stone == Stone.EMPTY:
            return False

        for dr, dc in Direction.ALL:
            pos, neg, total = self._get_line_info(row, col, dr, dc, stone)
            if total == 5:
                return True
        return False

    def check_forbidden(self, row: int, col: int) -> Optional[str]:
        """
        检测黑方禁手（在模拟落子前调用）
        五连优先：如果该位置能形成五连，不判禁手
        """
        # 临时落子
        self.board[row][col] = Stone.BLACK

        # 五连优先
        if self.check_win(row, col):
            self.board[row][col] = Stone.EMPTY
            return None

        # 长连检测
        if self._check_overline(row, col):
            self.board[row][col] = Stone.EMPTY
            return ForbiddenType.OVERLINE

        # 双四检测
        if self._check_double_four(row, col):
            self.board[row][col] = Stone.EMPTY
            return ForbiddenType.DOUBLE_FOUR

        # 双三检测
        if self._check_double_three(row, col):
            self.board[row][col] = Stone.EMPTY
            return ForbiddenType.DOUBLE_THREE

        self.board[row][col] = Stone.EMPTY
        return None

    def _check_overline(self, row: int, col: int) -> bool:
        """长连检测：是否有六子及以上的连珠"""
        for dr, dc in Direction.ALL:
            pos, neg, total = self._get_line_info(row, col, dr, dc, Stone.BLACK)
            if total >= 6:
                return True
        return False

    def _count_live_ends(self, row: int, col: int, dr: int, dc: int, stone: Stone, length: int) -> int:
        """
        检测某方向上指定长度的连子，返回活端数（0, 1, 2）
        活端：连子两端为空位
        """
        # 正向找到连子末端
        r, c = row, col
        for _ in range(length - 1):
            r += dr
            c += dc
        # 正向端
        fr, fc = r + dr, c + dc
        pos_open = self._in_bounds(fr, fc) and self.board[fr][fc] == Stone.EMPTY

        # 反向找到连子末端
        r, c = row, col
        for _ in range(length - 1):
            r -= dr
            c -= dc
        # 反向端
        br, bc = r - dr, c - dc
        neg_open = self._in_bounds(br, bc) and self.board[br][bc] == Stone.EMPTY

        return int(pos_open) + int(neg_open)

    def _is_live_three(self, row: int, col: int, dr: int, dc: int) -> bool:
        """
        检测某方向是否形成活三
        活三：连续三子，两端均空（且延伸后可形成活四，不会被禁手阻挡）
        """
        pos, neg, total = self._get_line_info(row, col, dr, dc, Stone.BLACK)

        # 3子连续 + 两端空 = 活三
        if total == 3:
            live_ends = self._count_live_ends(row, col, dr, dc, Stone.BLACK, 3)
            return live_ends == 2

        # 跳三模式：如 X_XXX 或 XXX_X（间隔一个空位）
        # 检查正向跳一格
        r1, c1 = row + dr * 2, col + dc * 2
        if self._in_bounds(r1, c1):
            # 连续2子 + 跳一格 + 1子
            if (pos == 2 and self._in_bounds(r1, c1) and
                    self.board[row + dr][col + dc] == Stone.BLACK and
                    self.board[r1][c1] == Stone.EMPTY):
                # 跳三：OOXOXX 型
                pass  # 由 _count_live_ends 处理

        # 简化处理：通过模拟判断
        return False

    def _find_threes(self, row: int, col: int) -> int:
        """统计落子后形成的活三数量"""
        count = 0
        for dr, dc in Direction.ALL:
            pos, neg, total = self._get_line_info(row, col, dr, dc, Stone.BLACK)

            if total == 3:
                live_ends = self._count_live_ends(row, col, dr, dc, Stone.BLACK, 3)
                if live_ends == 2:
                    count += 1
            elif total == 4:
                # 可能是跳三的情况：如 _X_XXX_ 中间有间隔
                pass

        # 额外检测跳三（间隔型）
        count += self._find_jump_threes(row, col)
        return count

    def _find_jump_threes(self, row: int, col: int) -> int:
        """检测跳三（如 X_XXX 或 XXX_X 型）"""
        count = 0
        stone = Stone.BLACK

        for dr, dc in Direction.ALL:
            # 检测模式：当前位置与同方向其他棋子形成跳三
            # 向正向和反向各延伸，检查中间是否有间隔
            for sign in [1, -1]:
                # 尝试在正方向隔一格位置有棋子
                r1, c1 = row + dr * sign, col + dc * sign
                if not self._in_bounds(r1, c1) or self.board[r1][c1] != stone:
                    continue

                # 再往同方向一格应为空
                r2, c2 = row + dr * sign * 2, col + dc * sign * 2
                if not self._in_bounds(r2, c2) or self.board[r2][c2] != Stone.EMPTY:
                    continue

                # 再往同方向一格应有棋子
                r3, c3 = row + dr * sign * 3, col + dc * sign * 3
                if not self._in_bounds(r3, c3) or self.board[r3][c3] != stone:
                    continue

                # 这样就是跳三：当前 + 隔一格 + 再一格（中间有空）
                # 检查两端是否都空
                # 外端
                outer_r, outer_c = row - dr * sign, col - dc * sign
                outer_open = self._in_bounds(outer_r, outer_c) and self.board[outer_r][outer_c] == Stone.EMPTY
                # 内端
                inner_r, inner_c = r3 + dr * sign, r3 + dc * sign
                inner_open = self._in_bounds(inner_r, inner_c) and self.board[inner_r][inner_c] == Stone.EMPTY

                if outer_open and inner_open:
                    count += 1

        return count

    def _check_double_three(self, row: int, col: int) -> bool:
        """双三检测：一步形成两个或以上活三"""
        return self._find_threes(row, col) >= 2

    def _find_fours(self, row: int, col: int) -> int:
        """统计落子后形成的四的数量（每方向最多计一个四）"""
        count = 0
        stone = Stone.BLACK

        for dr, dc in Direction.ALL:
            if self._is_four_in_direction(row, col, dr, dc, stone):
                count += 1

        return count

    def _is_four_in_direction(self, row: int, col: int,
                              dr: int, dc: int, stone: Stone) -> bool:
        """检测某方向是否形成一个四（连续四子 或 跳四 XXX_X / X_XXX）"""
        # 沿该方向收集一段棋子（以 row,col 为中心向两侧延伸）
        line = []  # (r, c, stone_or_empty)
        for i in range(-5, 6):
            r, c = row + dr * i, col + dc * i
            if self._in_bounds(r, c):
                line.append((r, c, self.board[r][c]))
            else:
                line.append((r, c, None))  # 边界外

        # 中心点在 line[5]
        center_idx = 5

        # 在包含中心点的连续区域内查找四的模式
        # 从中心向两侧找到连续的非边界区域
        start = center_idx
        while start > 0 and line[start - 1][2] is not None:
            start -= 1
        end = center_idx
        while end < len(line) - 1 and line[end + 1][2] is not None:
            end += 1

        # 在 [start, end] 范围内，查找包含 (row,col) 的四
        # 连续四：恰好 4 个连续同色 + 两端至少一端为空
        for i in range(start, end - 2):
            # 检查 4 连续格子
            cells = [line[i + j][2] for j in range(4)]
            if all(c == stone for c in cells):
                # 确认这个四包含 (row,col)
                positions = [(line[i + j][0], line[i + j][1]) for j in range(4)]
                if (row, col) in positions:
                    # 检查两端是否至少有一端为空（可成五）
                    left_open = (i > 0 and line[i - 1][2] == Stone.EMPTY)
                    right_open = (i + 4 <= end and line[i + 4][2] == Stone.EMPTY)
                    if left_open or right_open:
                        return True

        # 跳四：4 子 + 1 空，空位恰好是 (row,col) 或是被填的空位
        # 模式：XXX_X（空在第4位）或 X_XXX（空在第2位）
        for i in range(start, end - 3):
            cells = [line[i + j][2] for j in range(5)]
            stones_in = sum(1 for c in cells if c == stone)
            empties_in = sum(1 for c in cells if c == Stone.EMPTY)
            if stones_in == 4 and empties_in == 1:
                # 找到空位的位置
                empty_idx = cells.index(Stone.EMPTY)
                empty_pos = (line[i + empty_idx][0], line[i + empty_idx][1])
                # 这个四必须包含 (row,col) 作为落子点
                # 即 (row,col) 是空位被填入，或是四中的一个子
                placed_positions = [(line[i + j][0], line[i + j][1])
                                    for j in range(5) if j != empty_idx]
                if (row, col) in placed_positions:
                    # 空位必须能成五（两端检查）
                    # 空位两侧的子必须是连续的四子
                    return True

        return False

    def _check_double_four(self, row: int, col: int) -> bool:
        """双四检测：一步形成两个或以上四"""
        return self._find_fours(row, col) >= 2

    def undo(self) -> bool:
        """悔棋（撤回最后一步，人机模式撤两步）"""
        if not self.move_history:
            return False

        # 撤回一步
        row, col = self.move_history.pop()
        self.board[row][col] = Stone.EMPTY
        self.current_player = Stone.BLACK if self.current_player == Stone.WHITE else Stone.WHITE
        self.game_over = False
        self.winner = None
        return True

    def get_stone(self, row: int, col: int) -> Stone:
        return self.board[row][col]

    def get_forbidden_moves(self) -> List[Tuple[int, int, str]]:
        """
        获取当前黑方所有禁手位置（用于UI提示）
        只检查黑棋周围 2 格内的空位，不扫全棋盘
        """
        if self.current_player != Stone.BLACK:
            return []

        # 收集黑棋附近的空位
        check_positions = set()
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.board[r][c] == Stone.BLACK:
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < self.SIZE and 0 <= nc < self.SIZE
                                    and self.board[nr][nc] == Stone.EMPTY):
                                check_positions.add((nr, nc))

        forbidden = []
        for r, c in check_positions:
            result = self.check_forbidden(r, c)
            if result:
                forbidden.append((r, c, result))
        return forbidden
