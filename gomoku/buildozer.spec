[app]

# App 基本信息
title = 五子棋
package.name = gomoku
package.domain = org.renju
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttc,ttf
version = 1.0.0

# 依赖
requirements = python3,kivy,pillow

# Android 配置
android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# 全屏模式
fullscreen = 1

# 横竖屏 (portrait=竖屏, landscape=横屏)
orientation = portrait

# 应用图标
# icon.filename = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/presplash.png

# 日志级别
log_level = 2

# iOS 配置（如需）
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# ios.kivy_ios_branch = master

# Build 配置
android.release_artifact = aab
