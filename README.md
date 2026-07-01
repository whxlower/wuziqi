# 五子棋游戏

一款基于Flutter开发的五子棋手机游戏，支持人机对战和人人对战，包含完整的禁手规则。

## 功能特性

- ✅ 人机对战模式（支持选择黑棋或白棋）
- ✅ 人人对战模式
- ✅ 完整禁手规则（三三禁手、四四禁手、长连禁手）
- ✅ 禁手规则说明页面
- ✅ 悔棋功能
- ✅ 显示禁手位置（人机对战模式）
- ✅ 胜负判定与结果展示

## 技术栈

- Flutter 3.x
- Dart
- CustomPaint + Canvas（棋盘绘制）
- Minimax + Alpha-Beta剪枝（AI引擎）
- SharedPreferences（数据存储）

## 项目结构

```
lib/
├── main.dart                    # 入口文件
├── ui/
│   ├── home_screen.dart         # 首页（模式选择）
│   ├── game_screen.dart         # 游戏界面
│   ├── board_widget.dart        # 棋盘组件
│   └── rule_screen.dart         # 禁手规则说明页
├── logic/
│   ├── board.dart               # 棋盘状态管理
│   ├── rules.dart               # 胜负判断
│   └── forbidden_moves.dart     # 禁手检测
├── ai/
│   ├── ai_engine.dart           # AI核心逻辑
│   └── evaluation.dart          # 评估函数
└── data/
    └── storage.dart             # 数据存储管理
```

## 构建APK步骤

### 方法一：使用GitHub Actions云端构建（推荐，无需安装任何工具）

**只需一个浏览器和GitHub账号，完全免费！**

#### 步骤1：创建GitHub账号（如已有可跳过）

访问 [GitHub官网](https://github.com/) 注册账号。

#### 步骤2：创建新仓库

1. 登录GitHub后，点击页面右上角的 "+" 号
2. 选择 "New repository"
3. 填写仓库名称（如 `gomoku-game`）
4. 选择 "Public"（公开仓库免费）
5. 点击 "Create repository"

#### 步骤3：上传项目文件

1. 在仓库页面点击 "Add file" → "Upload files"
2. 将本项目中的所有文件拖放到上传区域
3. 点击 "Commit changes"

#### 步骤4：触发构建

1. 进入仓库的 "Actions" 标签页
2. 点击左侧的 "Build Android APK"
3. 点击 "Run workflow" → "Run workflow"

#### 步骤5：下载APK

1. 等待构建完成（约15-20分钟）
2. 点击构建记录进入详情页
3. 向下滚动到 "Artifacts" 部分
4. 点击 "gomoku-apk" 下载压缩包
5. 解压后得到 `app-release.apk`

---

### 方法二：本地构建（需要安装开发工具）

如果您愿意安装开发工具，可以使用此方法：

#### 1. 安装开发环境

- [Flutter SDK](https://docs.flutter.dev/get-started/install)
- [Android Studio](https://developer.android.com/studio)（包含Android SDK）
- [Java JDK 8+](https://www.oracle.com/java/technologies/downloads/)

#### 2. 创建Flutter项目

```bash
flutter create gomoku
cd gomoku
```

#### 3. 替换源代码

将本项目中的 `lib/` 目录下的所有文件复制到刚创建的项目中，覆盖原有文件。

#### 4. 更新pubspec.yaml

将本项目的 `pubspec.yaml` 内容复制到刚创建的项目中。

#### 5. 构建APK

```bash
flutter build apk --release
```

#### 6. 获取APK文件

构建成功后，APK文件位于：
`build/app/outputs/flutter-apk/app-release.apk`

## 禁手规则说明

### 三三禁手
黑棋在落下一子后，同时形成两个或以上的"活三"（两端都有空位的三连）。

### 四四禁手
黑棋在落下一子后，同时形成两个或以上的"四"（冲四或活四）。

### 长连禁手
黑棋在落下一子后，形成六个或以上连续的棋子。

> 注意：禁手规则仅对黑棋生效，白棋无禁手限制。

## 开发说明

### AI难度设置

AI难度在 `lib/ai/ai_engine.dart` 中定义：
- 简单：搜索深度3
- 中等：搜索深度4
- 困难：搜索深度6

### 运行项目

```bash
flutter run
```

## License

MIT License
