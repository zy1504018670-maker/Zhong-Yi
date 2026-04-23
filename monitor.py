import time
import threading
from datetime import datetime
from process_scanner import ProcessScanner
from data_logger import DataLogger
from config import SCAN_INTERVAL, DEFAULT_LIMIT_MINUTES
import os
import sys

class GameMonitor:
    def __init__(self):
        self.current_game = None
        self.start_time = None
        self.scanner = ProcessScanner()
        self.running = False
        self.thread = None
        self.daily_limit = DEFAULT_LIMIT_MINUTES
        DataLogger.init_csv()

    def start_monitoring(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("Monitoring started...")

    def stop_monitoring(self):
        self.running = False

    def _monitor_loop(self):
        last_check = None
        while self.running:
            proc_names = self.scanner.get_running_processes()
            active_game = self.scanner.find_active_game(proc_names)

            if active_game and self.current_game is None:
                self.current_game = active_game
                self.start_time = datetime.now()
                print(f"[{self.start_time.strftime('%H:%M:%S')}] Game '{active_game}' started")

            elif not active_game and self.current_game is not None:
                end_time = datetime.now()
                duration = (end_time - self.start_time).total_seconds() / 60.0
                print(f"[{end_time.strftime('%H:%M:%S')}] Game '{self.current_game}' ended, duration: {duration:.1f} min")
                DataLogger.log_session(self.start_time, end_time, self.current_game)
                self.current_game = None
                self.start_time = None

            now = datetime.now()
            if last_check is None or (now - last_check).seconds >= 60:
                self._check_time_limit()
                last_check = now

            time.sleep(SCAN_INTERVAL)

    def _check_time_limit(self):
        total = DataLogger.get_total_today()
        if self.current_game and self.start_time:
            current_duration = (datetime.now() - self.start_time).total_seconds() / 60.0
            total += current_duration
        if total >= self.daily_limit and self.daily_limit > 0:
            print(f"WARNING: Daily limit of {self.daily_limit} minutes reached! Shutting down in 60 seconds...")
            if not hasattr(self, '_shutdown_triggered'):
                self._shutdown_triggered = True
                threading.Timer(60.0, self._shutdown_pc).start()

    def _shutdown_pc(self):
        print("Shutting down now...")
        if sys.platform == "win32":
            os.system("shutdown /s /t 0")
        else:
            os.system("shutdown -h now")

    def set_daily_limit(self, minutes):
        self.daily_limit = minutes
        print(f"Daily time limit set to {minutes} minutes")

    def show_daily_chart(self):
        import matplotlib.pyplot as plt
        sessions = DataLogger.load_today_sessions()
        if not sessions:
            print("No play data today.")
            return
        game_times = {}
        for _, _, game, dur in sessions:
            game_times[game] = game_times.get(game, 0) + dur
        if self.current_game and self.start_time:
            cur_dur = (datetime.now() - self.start_time).total_seconds() / 60.0
            game_times[self.current_game] = game_times.get(self.current_game, 0) + cur_dur

        games = list(game_times.keys())
        times = list(game_times.values())
        plt.bar(games, times)
        plt.xlabel("Game")
        plt.ylabel("Minutes")
        plt.title(f"Play Time Today (Total: {sum(times):.1f} min)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def shutdown_now(self):
        self._shutdown_pc()

    # 创建一个全局监控器实例，供 api.py 使用
game_monitor = GameMonitor()
