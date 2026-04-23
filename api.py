from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import threading
import time

# 导入监控模块的全局状态（需要与 monitor 共享）
# 这里使用一个简单的全局变量字典，实际可以用数据库
import config
from data_logger import DataLogger

app = FastAPI(title="Child Play Time Monitor API", version="1.0")

# 定义请求/响应模型
class GameName(BaseModel):
    name: str

class LimitMinutes(BaseModel):
    limit: int

class Student(BaseModel):
    id: int
    name: str

# 模拟学生列表（用于满足“get list of students”要求）
students_db = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

# ---------- 健康检查 ----------
@app.get("/")
def root():
    return {"message": "Child Play Time Monitor API is running"}

# ---------- 游戏列表管理 ----------
@app.get("/games")
def get_games():
    """获取当前监控的游戏进程名列表"""
    return {"games": list(config.GAME_PROCESS_NAMES)}

@app.post("/games")
def add_game(game: GameName):
    """添加一个要监控的游戏进程名"""
    if game.name in config.GAME_PROCESS_NAMES:
        raise HTTPException(status_code=400, detail="Game already exists")
    config.GAME_PROCESS_NAMES.add(game.name)
    # 持久化到配置文件（简单起见，这里不写回文件，重启后丢失）
    return {"message": f"Game '{game.name}' added", "games": list(config.GAME_PROCESS_NAMES)}

@app.delete("/games/{game_name}")
def delete_game(game_name: str):
    """删除一个游戏进程名"""
    if game_name not in config.GAME_PROCESS_NAMES:
        raise HTTPException(status_code=404, detail="Game not found")
    config.GAME_PROCESS_NAMES.remove(game_name)
    return {"message": f"Game '{game_name}' removed", "games": list(config.GAME_PROCESS_NAMES)}

# ---------- 时间限制管理 ----------
@app.get("/limit")
def get_limit():
    """获取当前每日时间限制（分钟）"""
    from monitor import game_monitor  # 延迟导入避免循环
    return {"daily_limit_minutes": game_monitor.daily_limit}

@app.put("/limit")
def set_limit(limit: LimitMinutes):
    from monitor import game_monitor
    game_monitor.set_daily_limit(limit.limit)
    return {"message": f"Daily limit set to {limit.limit} minutes"}

# ---------- 统计数据 ----------
@app.get("/stats/today")
def get_today_stats():
    """获取今日各游戏时长统计"""
    sessions = DataLogger.load_today_sessions()
    game_times = {}
    for _, _, game, dur in sessions:
        game_times[game] = game_times.get(game, 0) + dur
    # 加上当前正在进行的游戏
    from monitor import game_monitor
    if game_monitor.current_game and game_monitor.start_time:
        cur_dur = (datetime.now() - game_monitor.start_time).total_seconds() / 60.0
        game_times[game_monitor.current_game] = game_times.get(game_monitor.current_game, 0) + cur_dur
    total = sum(game_times.values())
    return {"date": str(date.today()), "game_stats": game_times, "total_minutes": total}

# ---------- 学生列表（满足题目要求） ----------
@app.get("/students")
def get_students():
    return {"students": students_db}

@app.post("/students")
def add_student(student: Student):
    students_db.append(student.dict())
    return {"message": "Student added", "students": students_db}

# ---------- 正确答案管理（满足题目要求，但本应用用不到，简单占位） ----------
right_answers = {"1": "A", "2": "B"}

@app.get("/answers")
def get_answers():
    return right_answers

@app.post("/answers")
def add_answer(key: str, value: str):
    right_answers[key] = value
    return {"message": "Answer added"}
