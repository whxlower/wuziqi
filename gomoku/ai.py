"""
五子棋 AI — 威胁优先 + Minimax + Alpha-Beta
核心改进：
  1. 威胁优先级：五连 > 防五 > 活四 > 防活四 > 冲四活三 > 防冲四活三 > 活三
  2. 棋型识别：基于棋盘扫描的完整棋型评分
  3. 候选点只在根节点生成，子节点用周围 1 格
  4. 硬性时间截止
"""

import time
from typing import Tuple, List, Optional
from game_logic import GomokuBoard, Stone, Direction


class GomokuAI:
    """五子棋 AI"""

    DEPTH_MAP = {"easy": 1, "medium": 2, "hard": 4}
    TIME_LIMIT = {"easy": 0.3, "medium": 1.0, "hard": 2.0}
    MAX_CANDIDATES = {"easy": 8, "medium": 12, "hard": 15}

    # 棋型分值（威胁等级）
    SCORE_FIVE = 10000000       # 五连（赢了）
    SCORE_LIVE_FOUR = 1000000   # 活四（必胜）
    SCORE_RUSH_FOUR = 100000    # 冲四
    SCORE_LIVE_THREE = 50000    # 活三
    SCORE_SLEEP_THREE = 5000    # 眠三
    SCORE_LIVE_TWO = 500        # 活二
    SCORE_SLEEP_TWO = 50        # 眠二
    SCORE_LIVE_ONE = 10         # 活一

    POSITION_WEIGHT = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],
        [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 5, 6, 6, 6, 6, 6, 5, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 5, 6, 7, 7, 7, 6, 5, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 5, 6, 7, 7, 7, 6, 5, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 5, 6, 6, 6, 6, 6, 5, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 2, 1, 0],
        [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0],
        [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    def __init__(self, ai_color: Stone, difficulty: str = "medium"):
        self.ai_color = ai_color
        self.human_color = Stone.WHITE if ai_color == Stone.BLACK else Stone.BLACK
        self.max_depth = self.DEPTH_MAP.get(difficulty, 2)
        self.time_limit = self.TIME_LIMIT.get(difficulty, 1.0)
        self.max_candidates = self.MAX_CANDIDATES.get(difficulty, 12)
        self.nodes_searched = 0
        self._deadline = 0

    def get_best_move(self, board: GomokuBoard) -> Tuple[int, int]:
        self.nodes_searched = 0
        self._deadline = time.time() + self.time_limit

        candidates = self._get_candidates(board)
        if not candidates:
            return (8, 8)
        if len(candidates) == 1:
            return candidates[0]

        # 威胁优先：找必应手
        urgent = self._find_urgent_move(board, candidates)
        if urgent:
            return urgent

        best_move = candidates[0]

        # 迭代加深
        for depth in range(1, self.max_depth + 1):
            if time.time() >= self._deadline:
                break
            move = self._search_at_depth(board, candidates, depth)
            if move is not None:
                best_move = move
            if time.time() - (self._deadline - self.time_limit) > self.time_limit * 0.6:
                break

        return best_move

    # ── 威胁检测 ──────────────────────────────────────────────

    def _find_urgent_move(self, board: GomokuBoard,
                          candidates: list) -> Optional[Tuple[int, int]]:
        """威胁优先级检测：按威胁等级从高到低找应手"""

        # 1. 自己能赢（五连）
        for r, c in candidates:
            board.board[r][c] = self.ai_color
            if board.check_win(r, c):
                board.board[r][c] = Stone.EMPTY
                return (r, c)
            board.board[r][c] = Stone.EMPTY

        # 2. 对手能赢，必须堵
        for r, c in candidates:
            board.board[r][c] = self.human_color
            if board.check_win(r, c):
                board.board[r][c] = Stone.EMPTY
                return (r, c)
            board.board[r][c] = Stone.EMPTY

        # 3. 自己能做活四
        for r, c in candidates:
            board.board[r][c] = self.ai_color
            if self._has_live_four(board, r, c, self.ai_color):
                board.board[r][c] = Stone.EMPTY
                return (r, c)
            board.board[r][c] = Stone.EMPTY

        # 4. 对手能做活四，必须堵
        for r, c in candidates:
            board.board[r][c] = self.human_color
            if self._has_live_four(board, r, c, self.human_color):
                board.board[r][c] = Stone.EMPTY
                return (r, c)
            board.board[r][c] = Stone.EMPTY

        # 5. 自己能做冲四+活三（双威胁）
        ai_d4t3 = []
        for r, c in candidates:
            board.board[r][c] = self.ai_color
            if self._has_rush_four(board, r, c, self.ai_color) and \
               self._has_live_three(board, r, c, self.ai_color):
                ai_d4t3.append((r, c))
            board.board[r][c] = Stone.EMPTY
        if ai_d4t3:
            return ai_d4t3[0]

        # 6. 对手能做冲四+活三，必须堵
        human_d4t3 = []
        for r, c in candidates:
            board.board[r][c] = self.human_color
            if self._has_rush_four(board, r, c, self.human_color) and \
               self._has_live_three(board, r, c, self.human_color):
                human_d4t3.append((r, c))
            board.board[r][c] = Stone.EMPTY
        if human_d4t3:
            return human_d4t3[0]

        # 7. 对手有活三，必须堵（放最后，因为活三不是立即致命）
        for r, c in candidates:
            board.board[r][c] = self.human_color
            if self._has_live_three(board, r, c, self.human_color):
                board.board[r][c] = Stone.EMPTY
                return (r, c)
            board.board[r][c] = Stone.EMPTY

        return None

    def _has_live_four(self, board: GomokuBoard, row: int, col: int, stone: Stone) -> bool:
        """落子后是否形成活四（四连两端空）"""
        for dr, dc in Direction.ALL:
            if self._is_pattern(board, row, col, dr, dc, stone, 4, 2):
                return True
        return False

    def _has_rush_four(self, board: GomokuBoard, row: int, col: int, stone: Stone) -> bool:
        """落子后是否形成冲四（四连一端空）"""
        for dr, dc in Direction.ALL:
            if self._is_pattern(board, row, col, dr, dc, stone, 4, 1):
                return True
        return False

    def _has_live_three(self, board: GomokuBoard, row: int, col: int, stone: Stone) -> bool:
        """落子后是否形成活三（三连两端空，可延伸为活四）"""
        for dr, dc in Direction.ALL:
            if self._is_live_three(board, row, col, dr, dc, stone):
                return True
        return False

    def _is_pattern(self, board: GomokuBoard, row: int, col: int,
                    dr: int, dc: int, stone: Stone, length: int, open_ends: int) -> bool:
        """检测某方向是否有指定长度和开放端数的连续棋型"""
        # 正向计数
        pos_count = 0
        r, c = row + dr, col + dc
        while board._in_bounds(r, c) and board.board[r][c] == stone:
            pos_count += 1
            r += dr
            c += dc
        pos_open = board._in_bounds(r, c) and board.board[r][c] == Stone.EMPTY

        # 反向计数
        neg_count = 0
        r, c = row - dr, col - dc
        while board._in_bounds(r, c) and board.board[r][c] == stone:
            neg_count += 1
            r -= dr
            c -= dc
        neg_open = board._in_bounds(r, c) and board.board[r][c] == Stone.EMPTY

        total = pos_count + neg_count + 1
        opens = int(pos_open) + int(neg_open)

        return total == length and opens >= open_ends

    def _is_live_three(self, board: GomokuBoard, row: int, col: int,
                       dr: int, dc: int, stone: Stone) -> bool:
        """检测活三：三连两端空，且延伸后不会被堵死"""
        # 正向计数
        pos_count = 0
        r, c = row + dr, col + dc
        while board._in_bounds(r, c) and board.board[r][c] == stone:
            pos_count += 1
            r += dr
            c += dc
        pos_open = board._in_bounds(r, c) and board.board[r][c] == Stone.EMPTY

        # 反向计数
        neg_count = 0
        r, c = row - dr, col - dc
        while board._in_bounds(r, c) and board.board[r][c] == stone:
            neg_count += 1
            r -= dr
            c -= dc
        neg_open = board._in_bounds(r, c) and board.board[r][c] == Stone.EMPTY

        total = pos_count + neg_count + 1
        opens = int(pos_open) + int(neg_open)

        # 三连 + 两端空 = 活三
        if total == 3 and opens == 2:
            return True

        # 跳三：X_XXX 或 XXX_X（间隔一个空位的三子）
        if total == 3 and opens >= 1:
            # 检查是否有跳三模式
            # 正方向隔一格是否有空位再有棋子
            gap_r, gap_c = row + dr * (pos_count + 2), col + dc * (pos_count + 2)
            if pos_open and board._in_bounds(gap_r, gap_c):
                if board.board[row + dr * (pos_count + 1)][col + dc * (pos_count + 1)] == Stone.EMPTY \
                   and board.board[gap_r][gap_c] == stone:
                    return True
            gap_r, gap_c = row - dr * (neg_count + 2), col - dc * (neg_count + 2)
            if neg_open and board._in_bounds(gap_r, gap_c):
                if board.board[row - dr * (neg_count + 1)][col - dc * (neg_count + 1)] == Stone.EMPTY \
                   and board.board[gap_r][gap_c] == stone:
                    return True

        return False

    # ── 候选点生成 ──────────────────────────────────────────────

    def _get_candidates(self, board: GomokuBoard) -> List[Tuple[int, int]]:
        """生成候选点：已有棋子周围 2 格，按威胁度排序"""
        candidates = set()
        has_stone = False

        for r in range(board.SIZE):
            for c in range(board.SIZE):
                if board.board[r][c] != Stone.EMPTY:
                    has_stone = True
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < board.SIZE and 0 <= nc < board.SIZE
                                    and board.board[nr][nc] == Stone.EMPTY):
                                candidates.add((nr, nc))

        if not has_stone:
            return [(8, 8)]

        scored = []
        for (r, c) in candidates:
            score = self._quick_score(board, r, c)
            scored.append((score, r, c))

        scored.sort(reverse=True)
        return [(r, c) for _, r, c in scored[:self.max_candidates]]

    def _quick_score(self, board: GomokuBoard, row: int, col: int) -> float:
        """快速评估空位价值（攻防兼顾）"""
        score = self.POSITION_WEIGHT[row][col] * 3

        # 进攻价值
        board.board[row][col] = self.ai_color
        atk = 0
        for dr, dc in Direction.ALL:
            atk += self._quick_line_score(board, row, col, dr, dc, self.ai_color)
        board.board[row][col] = Stone.EMPTY

        # 防守价值（对手在此落子的威胁）
        board.board[row][col] = self.human_color
        dfs = 0
        for dr, dc in Direction.ALL:
            dfs += self._quick_line_score(board, row, col, dr, dc, self.human_color)
        board.board[row][col] = Stone.EMPTY

        # 防守权重 >= 进攻权重（先防守再进攻）
        score += atk * 1.0 + dfs * 1.2
        return score

    def _quick_line_score(self, board: GomokuBoard, row: int, col: int,
                          dr: int, dc: int, stone: Stone) -> float:
        """快速评估某方向棋型"""
        pos_count = 0
        r, c = row + dr, col + dc
        while board._in_bounds(r, c) and board.board[r][c] == stone:
            pos_count += 1
            r += dr
            c += dc
        pos_open = board._in_bounds(r, c) and board.board[r][c] == Stone.EMPTY

        neg_count = 0
        r, c = row - dr, col - dc
        while board._in_bounds(r, c) and board.board[r][c] == stone:
            neg_count += 1
            r -= dr
            c -= dc
        neg_open = board._in_bounds(r, c) and board.board[r][c] == Stone.EMPTY

        total = pos_count + neg_count + 1
        opens = int(pos_open) + int(neg_open)

        if total >= 5:
            return self.SCORE_FIVE
        elif total == 4:
            if opens == 2: return self.SCORE_LIVE_FOUR
            elif opens == 1: return self.SCORE_RUSH_FOUR
        elif total == 3:
            if opens == 2: return self.SCORE_LIVE_THREE
            elif opens == 1: return self.SCORE_SLEEP_THREE
        elif total == 2:
            if opens == 2: return self.SCORE_LIVE_TWO
            elif opens == 1: return self.SCORE_SLEEP_TWO
        elif total == 1:
            if opens == 2: return self.SCORE_LIVE_ONE
        return 0

    # ── Minimax 搜索 ──────────────────────────────────────────

    def _search_at_depth(self, board: GomokuBoard, candidates: list,
                         depth: int) -> Optional[Tuple[int, int]]:
        best_score = float('-inf')
        best_move = None
        for row, col in candidates:
            if time.time() >= self._deadline:
                return best_move
            board.board[row][col] = self.ai_color
            score = self._minimax(board, depth - 1, float('-inf'), float('inf'), False)
            board.board[row][col] = Stone.EMPTY
            if score > best_score:
                best_score = score
                best_move = (row, col)
        return best_move

    def _minimax(self, board: GomokuBoard, depth: int, alpha: float, beta: float,
                 is_maximizing: bool) -> float:
        self.nodes_searched += 1

        if time.time() >= self._deadline:
            return 0

        if depth == 0:
            return self._evaluate(board)

        candidates = self._get_nearby_moves(board)
        if not candidates:
            return 0

        if is_maximizing:
            max_eval = float('-inf')
            for row, col in candidates:
                if time.time() >= self._deadline:
                    return max_eval
                board.board[row][col] = self.ai_color
                if board.check_win(row, col):
                    board.board[row][col] = Stone.EMPTY
                    return self.SCORE_FIVE
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                board.board[row][col] = Stone.EMPTY
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for row, col in candidates:
                if time.time() >= self._deadline:
                    return min_eval
                board.board[row][col] = self.human_color
                if board.check_win(row, col):
                    board.board[row][col] = Stone.EMPTY
                    return -self.SCORE_FIVE
                eval_score = self._minimax(board, depth - 1, alpha, beta, True)
                board.board[row][col] = Stone.EMPTY
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _get_nearby_moves(self, board: GomokuBoard) -> List[Tuple[int, int]]:
        """子节点候选：已有棋子周围 1 格"""
        candidates = set()
        for r in range(board.SIZE):
            for c in range(board.SIZE):
                if board.board[r][c] != Stone.EMPTY:
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < board.SIZE and 0 <= nc < board.SIZE
                                    and board.board[nr][nc] == Stone.EMPTY):
                                candidates.add((nr, nc))
        return list(candidates)

    # ── 局面评估 ──────────────────────────────────────────────

    def _evaluate(self, board: GomokuBoard) -> float:
        """局面评估：扫描所有棋子的棋型"""
        ai_score = 0.0
        human_score = 0.0

        for r in range(board.SIZE):
            for c in range(board.SIZE):
                stone = board.board[r][c]
                if stone == Stone.EMPTY:
                    continue

                pos_weight = self.POSITION_WEIGHT[r][c]

                if stone == self.ai_color:
                    for dr, dc in Direction.ALL:
                        ai_score += self._evaluate_line(board, r, c, dr, dc, stone)
                    ai_score += pos_weight * 8
                else:
                    for dr, dc in Direction.ALL:
                        human_score += self._evaluate_line(board, r, c, dr, dc, stone)
                    human_score += pos_weight * 8

        # 防守系数：对手的威胁权重更高
        return ai_score - human_score * 1.1

    def _evaluate_line(self, board: GomokuBoard, row: int, col: int,
                       dr: int, dc: int, stone: Stone) -> float:
        """评估某方向棋型（避免重复计数）"""
        pr, pc = row - dr, col - dc
        if board._in_bounds(pr, pc) and board.board[pr][pc] == stone:
            return 0

        count = 1
        r, c = row + dr, col + dc
        while board._in_bounds(r, c) and board.board[r][c] == stone:
            count += 1
            r += dr
            c += dc

        open_ends = 0
        if board._in_bounds(r, c) and board.board[r][c] == Stone.EMPTY:
            open_ends += 1
        if board._in_bounds(pr, pc) and board.board[pr][pc] == Stone.EMPTY:
            open_ends += 1

        if count >= 5:
            return self.SCORE_FIVE
        elif count == 4:
            if open_ends == 2: return self.SCORE_LIVE_FOUR
            elif open_ends == 1: return self.SCORE_RUSH_FOUR
        elif count == 3:
            if open_ends == 2: return self.SCORE_LIVE_THREE
            elif open_ends == 1: return self.SCORE_SLEEP_THREE
        elif count == 2:
            if open_ends == 2: return self.SCORE_LIVE_TWO
            elif open_ends == 1: return self.SCORE_SLEEP_TWO
        elif count == 1:
            if open_ends == 2: return self.SCORE_LIVE_ONE
        return 0
