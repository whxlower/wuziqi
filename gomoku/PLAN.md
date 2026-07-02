# 五子棋 (Gomoku/Renju) — 项目开发计划

## 项目概述
基于 Python + Kivy 的五子棋游戏，支持人人对战和人机对战，含专业禁手规则。
可打包为 Android APK。

---

## 一、规则设计

### 基本规则
- 17×17 标准棋盘
- 黑先白后，交替落子
- 五子连珠（横/竖/斜）获胜

### 禁手规则（仅限黑方，Renju 标准）
| 禁手类型 | 说明 |
|---------|------|
| **三三禁手** | 一步棋同时形成两个或以上活三 |
| **四四禁手** | 一步棋同时形成两个或以上四（活四/冲四） |
| **长连禁手** | 一步棋形成六子或以上连珠 |

- 白方无禁手
- 黑方禁手位置不可落子，但若该位置恰好形成五连则判胜（五连优先）
- 需提供禁手说明页面供玩家查阅

---

## 二、项目结构

```
gomoku/
├── main.py              # 程序入口 + Kivy App
├── game_logic.py        # 核心逻辑：棋盘状态、胜负判定、禁手检测
├── ai.py                # AI 对手（极小极大 + Alpha-Beta 剪枝）
├── ui/
│   ├── __init__.py
│   ├── board_widget.py  # 棋盘绘制 + 触摸交互
│   ├── menu_screen.py   # 主菜单（模式选择）
│   ├── settings_screen.py # 设置页（选黑白、禁手说明）
│   └── result_popup.py  # 对局结果弹窗
├── assets/              # 图标等资源
├── buildozer.spec       # Android 打包配置
└── README.md            # 使用说明
```

---

## 三、模块设计

### 3.1 game_logic.py — 核心逻辑

```
class GomokuBoard:
    - board: 17x17 二维数组 (0=空, 1=黑, 2=白)
    - current_player: 当前玩家
    - move_history: 落子记录
    - game_over: 是否结束
    - winner: 胜者

    方法:
    - place_stone(row, col) → bool          # 落子，返回是否合法
    - check_win(row, col) → bool            # 判胜（五连）
    - check_forbidden(row, col) → str|None  # 禁手检测，返回禁手类型或None
    - is_valid_move(row, col) → bool        # 综合合法性判断
    - undo() → None                          # 悔棋
    - reset() → None                         # 重置
```

**禁手检测算法:**
1. `check_long_connection(row, col)` — 检测六连及以上
2. `check_double_three(row, col)` — 检测双活三
3. `check_double_four(row, col)` — 检测双四
4. 判断前先模拟落子，检测后撤回
5. 五连优先：若落子形成五连，不判禁手

### 3.2 ai.py — AI 对手

```
class GomokuAI:
    - ai_color: AI执子颜色
    - difficulty: 难度等级

    方法:
    - get_best_move(board) → (row, col)  # 返回最佳落子位置
    - evaluate(board) → int              # 局面评估
    - minimax(depth, alpha, beta) → int  # 极小极大搜索
```

**AI 策略:**
- 评估函数：连子数量 + 位置权重 + 攻防平衡
- 搜索深度：3-5 层（视设备性能）
- Alpha-Beta 剪枝优化
- 候选点生成：只搜索已有棋子周围的空位（距离≤2）
- AI 遵守禁手规则（执黑时）

### 3.3 UI 模块

**菜单页 (menu_screen.py):**
- 人人对战按钮
- 人机对战按钮
- 禁手说明按钮
- 设置按钮

**设置页 (settings_screen.py):**
- 人机对战时选择执黑/执白
- 难度选择（简单/中等/困难）

**棋盘 (board_widget.py):**
- Canvas 绘制 17×17 棋盘线
- 棋子用圆形绘制（黑/白）
- 触摸落子（坐标映射到格点）
- 最后一手标记（红色小点）
- 禁手位置提示（执黑时显示叉号）
- 悔棋按钮
- 当前玩家指示

**结果弹窗 (result_popup.py):**
- 显示胜者
- 再来一局 / 返回菜单

---

## 四、技术选型

| 组件 | 方案 |
|-----|-----|
| UI 框架 | Kivy 2.x |
| 语言 | Python 3.9+ |
| 打包工具 | Buildozer (Android) |
| AI 算法 | Minimax + Alpha-Beta |
| 棋盘渲染 | Kivy Canvas |
| 网络需求 | **无，纯单机离线运行** |

---

## 五、开发顺序

1. **game_logic.py** — 棋盘状态 + 胜负判定 + 禁手检测
2. **ai.py** — AI 对手实现
3. **ui/board_widget.py** — 棋盘绘制与交互
4. **ui/menu_screen.py** — 主菜单
5. **ui/settings_screen.py** — 设置与禁手说明
6. **ui/result_popup.py** — 结果弹窗
7. **main.py** — 整合所有模块
8. **buildozer.spec** — Android 打包配置
9. **README.md** — 文档

---

## 六、打包说明

```bash
# 安装 buildozer
pip install buildozer

# 初始化（已含在项目中）
buildozer init

# 构建 APK
buildozer android debug

# 安装到设备
buildozer android deploy run
```

---

## 预计产出文件
- 8 个 Python 源文件
- 1 个 buildozer.spec
- 1 个 README.md
