# 五子棋 (Gomoku/Renju)

17×17 标准五子棋，支持人人对战和人机对战，含 Renju 标准禁手规则。

纯单机离线运行，无需联网。

## 功能

- **人人对战**：两人轮流在同一设备上对弈
- **人机对战**：与 AI 对弈，可选执黑/执白，三档难度
- **禁手规则**：黑方受三三、四四、长连禁手限制，含详细说明页
- **五连优先**：黑方在禁手位置形成五连时判胜
- **悔棋**：支持撤回落子
- **禁手提示**：执黑时可显示所有禁手位置

## 运行（桌面调试）

```bash
# 安装依赖
pip install kivy pillow

# 运行
cd gomoku
python main.py
```

## 打包 Android APK（GitHub Actions 云端构建）

无需本地搭建环境，push 代码到 GitHub 后自动构建 APK。

### 使用步骤

```bash
# 1. 创建 GitHub 仓库并推送代码
git init
git add .
git commit -m "init: gomoku game"
git remote add origin https://github.com/<你的用户名>/gomoku.git
git push -u origin main

# 2. 等待 GitHub Actions 自动构建（约 30-60 分钟）
#    在仓库页面 Actions 标签页查看构建进度

# 3. 构建完成后，进入 Actions → 最新构建 → Artifacts 下载 APK
```

### 手动触发构建

在 GitHub 仓库页面 → Actions → Build Android APK → Run workflow

### 构建产物

APK 文件在 Actions 运行的 Artifacts 中下载（保留 30 天）。

### 原理

GitHub Actions 使用 Ubuntu 22.04 运行环境，自动安装 Java 17、
Buildozer、Android SDK/NDK，执行 `buildozer android debug` 构建。

首次构建会缓存 `~/.buildozer` 目录，后续构建会更快。

## 项目结构

```
gomoku/
├── main.py              # 程序入口
├── game_logic.py        # 核心逻辑：棋盘、胜负、禁手检测
├── ai.py                # AI 对手（Minimax + Alpha-Beta 剪枝）
├── ui/
│   ├── board_widget.py  # 棋盘绘制与触摸交互
│   ├── menu_screen.py   # 主菜单
│   ├── settings_screen.py # 人机对战设置
│   ├── rules_screen.py  # 禁手说明
│   └── game_screen.py   # 游戏对局界面
├── buildozer.spec       # Android 打包配置
└── README.md
```

## 禁手规则速查

仅对**黑方**生效，白方无禁手。

| 禁手 | 说明 |
|-----|------|
| 三三 | 一步同时形成两个活三 |
| 四四 | 一步同时形成两个四 |
| 长连 | 六子及以上连珠 |

**五连优先**：形成五连时不判禁手。
