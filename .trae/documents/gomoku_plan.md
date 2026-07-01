# 五子棋游戏开发计划

## 一、项目概述

开发一款适配Android的五子棋手机App，支持人机对战和人人对战模式，包含完整的禁手规则及说明。

## 二、技术选型

| 分类 | 技术 | 理由 |
|------|------|------|
| 框架 | Flutter (Dart) | 单代码库跨平台，Canvas绘制棋盘性能优秀，快速构建高质量UI |
| 棋盘渲染 | CustomPaint + Canvas | 15×15棋盘自绘制，适配不同屏幕尺寸 |
| AI引擎 | Minimax + Alpha-Beta剪枝 | 搜索深度4-6层，提供良好对战体验 |
| 数据存储 | SharedPreferences | 存储对局记录和用户设置 |

## 三、项目架构

```
gomoku/
├── lib/
│   ├── main.dart                    # 入口文件
│   ├── ui/                         # UI展示层
│   │   ├── home_screen.dart        # 首页（模式选择）
│   │   ├── game_screen.dart        # 游戏界面
│   │   ├── board_widget.dart       # 棋盘组件
│   │   ├── rule_screen.dart        # 禁手规则说明页
│   │   └── settings_screen.dart    # 设置页
│   ├── logic/                      # 棋盘逻辑层
│   │   ├── board.dart              # 棋盘状态管理
│   │   ├── rules.dart              # 胜负判断
│   │   └── forbidden_moves.dart    # 禁手检测
│   ├── ai/                         # AI引擎层
│   │   ├── ai_engine.dart          # AI核心逻辑
│   │   └── evaluation.dart         # 评估函数
│   └── data/                       # 数据持久层
│       └── storage.dart            # 数据存储管理
├── android/                        # Android配置
├── assets/                         # 资源文件
└── pubspec.yaml                    # 依赖配置
```

## 四、开发步骤

### 阶段一：项目初始化与基础架构

1. 使用Flutter命令创建项目
2. 配置pubspec.yaml依赖
3. 创建项目目录结构

### 阶段二：棋盘逻辑层开发（核心）

1. **board.dart** - 棋盘状态管理
   - 15×15二维数组表示棋盘
   - 落子、悔棋、重置功能
   - 当前玩家追踪

2. **rules.dart** - 胜负判断
   - 检测横、竖、斜四个方向
   - 判断五子连珠
   - 判断平局

3. **forbidden_moves.dart** - 禁手检测（仅黑棋）
   - **三三禁手**：同时形成两个或以上活三
   - **四四禁手**：同时形成两个或以上冲四或活四
   - **长连禁手**：形成六个或以上连续棋子

### 阶段三：AI引擎开发

1. **evaluation.dart** - 评估函数
   - 对每个空位计算评分
   - 考虑连子数量、活棋数量、威胁程度

2. **ai_engine.dart** - AI核心逻辑
   - Minimax算法 + Alpha-Beta剪枝
   - 难度分级：简单（深度3）、中等（深度4）、困难（深度6）
   - 支持选择黑棋或白棋

### 阶段四：UI界面开发

1. **board_widget.dart** - 棋盘组件
   - Canvas绘制15×15棋盘
   - 绘制棋子、最后落子标记
   - 触摸交互处理

2. **home_screen.dart** - 首页
   - 模式选择：人机对战 / 人人对战
   - 进入规则说明
   - 进入设置

3. **game_screen.dart** - 游戏界面
   - 棋盘展示
   - 当前玩家指示
   - 悔棋、重新开始按钮
   - 胜负结果弹窗

4. **rule_screen.dart** - 禁手规则说明
   - 图文并茂解释三种禁手
   - 示例棋局展示

### 阶段五：数据持久化与优化

1. **storage.dart** - 数据存储
   - 保存对局记录
   - 保存用户设置（难度、默认颜色）

2. Android平台适配
   - 屏幕适配
   - 权限配置

### 阶段六：APK打包配置

1. 生成签名密钥（key.jks）
   ```bash
   keytool -genkey -v -keystore key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias gomoku
   ```

2. 配置android/key.properties
   - 签名密钥路径
   - 密钥别名和密码

3. 配置android/app/build.gradle
   - 应用签名配置
   - 应用版本号和包名

4. 构建Release APK
   ```bash
   flutter build apk --release
   ```

5. APK输出路径
   - `build/app/outputs/flutter-apk/app-release.apk`

## 五、禁手规则详解

### 1. 三三禁手
黑棋在落下一子后，同时形成两个或以上的"活三"（两端都有空位的三连）。

### 2. 四四禁手
黑棋在落下一子后，同时形成两个或以上的"四"（冲四或活四）。

### 3. 长连禁手
黑棋在落下一子后，形成六个或以上连续的棋子。

> 注意：禁手规则**仅对黑棋生效**，白棋无禁手限制。

## 六、风险处理

| 风险 | 处理方案 |
|------|----------|
| AI搜索时间过长 | 设置搜索深度限制，使用Alpha-Beta剪枝优化 |
| 禁手检测误判 | 编写单元测试覆盖各种禁手场景 |
| 屏幕适配问题 | 使用MediaQuery获取屏幕尺寸，动态计算棋盘大小 |
| 触摸定位不准 | 增加触摸区域判定容差 |

## 七、开发里程碑

1. **第1天**：项目初始化，完成棋盘逻辑层（board.dart, rules.dart）
2. **第2天**：完成禁手检测（forbidden_moves.dart）及单元测试
3. **第3天**：完成AI引擎（evaluation.dart, ai_engine.dart）
4. **第4天**：完成UI界面（board_widget.dart, home_screen.dart, game_screen.dart）
5. **第5天**：完成规则说明页、数据存储及Android适配
6. **第6天**：APK签名配置与Release构建，生成可安装的APK文件
