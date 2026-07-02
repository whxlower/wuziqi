"""
用户管理模块
数据存储在 data/users.json
"""

import json
import os
from game_logic import Stone

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_data():
    if not os.path.exists(USERS_FILE):
        return {"users": [], "current_user": None}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"users": [], "current_user": None}


def _save_data(data):
    _ensure_data_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_users():
    """返回所有用户列表"""
    return _load_data().get("users", [])


def get_current_user():
    """返回当前活跃用户名，无则返回 None"""
    data = _load_data()
    return data.get("current_user")


def set_current_user(name):
    """设置当前活跃用户"""
    data = _load_data()
    data["current_user"] = name
    _save_data(data)


def add_user(name):
    """添加用户，返回 (成功, 消息)"""
    name = name.strip()
    if not name:
        return False, "用户名不能为空"
    if len(name) > 20:
        return False, "用户名最长 20 字符"

    data = _load_data()
    for u in data["users"]:
        if u["name"] == name:
            return False, "用户名已存在"

    data["users"].append({
        "name": name,
        "stats": {
            "pvp": {"wins": 0, "losses": 0, "draws": 0},
            "pve_easy": {"wins": 0, "losses": 0, "draws": 0},
            "pve_medium": {"wins": 0, "losses": 0, "draws": 0},
            "pve_hard": {"wins": 0, "losses": 0, "draws": 0},
        }
    })

    # 如果是第一个用户，自动设为当前用户
    if len(data["users"]) == 1:
        data["current_user"] = name

    _save_data(data)
    return True, "添加成功"


def delete_user(name):
    """删除用户"""
    data = _load_data()
    data["users"] = [u for u in data["users"] if u["name"] != name]
    if data["current_user"] == name:
        data["current_user"] = data["users"][0]["name"] if data["users"] else None
    _save_data(data)


def get_user_stats(name):
    """获取用户的战绩数据"""
    data = _load_data()
    for u in data["users"]:
        if u["name"] == name:
            return u.get("stats", {})
    return {}


def record_game_result(mode, winner, user_is_black=True):
    """
    记录对局结果
    mode: 'pvp', 'pve_easy', 'pve_medium', 'pve_hard'
    winner: Stone.BLACK, Stone.WHITE, or None (draw)
    user_is_black: 用户是否执黑
    """
    data = _load_data()
    current = data.get("current_user")
    if not current:
        return

    # 人人对战不计入战绩
    if mode == "pvp":
        return

    for u in data["users"]:
        if u["name"] == current:
            stats = u.setdefault("stats", {})
            mode_stats = stats.setdefault(mode, {"wins": 0, "losses": 0, "draws": 0})

            if winner is None:
                mode_stats["draws"] += 1
            elif mode == "pvp":
                # PvP: 根据执子颜色判断输赢
                user_won = (winner == Stone.BLACK and user_is_black) or \
                           (winner == Stone.WHITE and not user_is_black)
                if user_won:
                    mode_stats["wins"] += 1
                else:
                    mode_stats["losses"] += 1
            else:
                # PvE: 用户赢 vs AI 赢
                if winner == Stone.BLACK and user_is_black:
                    mode_stats["wins"] += 1
                elif winner == Stone.WHITE and not user_is_black:
                    mode_stats["wins"] += 1
                else:
                    mode_stats["losses"] += 1
            break

    _save_data(data)


def reset_user_stats(name):
    """重置用户战绩"""
    data = _load_data()
    for u in data["users"]:
        if u["name"] == name:
            u["stats"] = {
                "pvp": {"wins": 0, "losses": 0, "draws": 0},
                "pve_easy": {"wins": 0, "losses": 0, "draws": 0},
                "pve_medium": {"wins": 0, "losses": 0, "draws": 0},
                "pve_hard": {"wins": 0, "losses": 0, "draws": 0},
            }
            break
    _save_data(data)
