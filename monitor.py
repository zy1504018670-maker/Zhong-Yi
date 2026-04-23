import os
import sys
import threading
import time
from datetime import datetime

from config import SCAN_INTERVAL, SHUTDOWN_GRACE_SECONDS
from data_logger import DataLogger
from network_monitor import NetworkMonitor
from process_scanner import ProcessScanner
from settings_store import SettingsStore
from task_manager import TaskManager


class GameMonitor:
    def __init__(
        self,
        scanner=None,
        data_logger=None,
        task_manager=None,
        settings_store=None,
        network_monitor=None,
    ):
        self.current_game = None
        self.start_time = None
        self.session_start_network_bytes = None
        self.session_rule_flags = set()
        self.scanner = scanner or ProcessScanner()
        self.data_logger = data_logger or DataLogger()
        self.task_manager = task_manager or TaskManager()
        self.settings_store = settings_store or SettingsStore()
        self.network_monitor = network_monitor or NetworkMonitor()
        self.running = False
        self.thread = None
        self.shutdown_triggered = False
        self.reload_settings()

    def reload_settings(self):
        settings = self.settings_store.load()
        self.game_process_names = set(settings["game_process_names"])
        self.daily_limit = int(settings["daily_limit_minutes"])
        self.network_limit_mb = float(settings["network_limit_mb"])
        self.auto_shutdown_enabled = bool(settings["auto_shutdown_enabled"])

    def start_monitoring(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("Monitoring started...")

    def stop_monitoring(self):
        self.running = False
        if self.current_game:
            self._end_current_session("monitor_stopped")
        if self.thread and self.thread.is_alive() and threading.current_thread() != self.thread:
            self.thread.join(timeout=2)
        self.thread = None

    def _monitor_loop(self):
        last_rule_check = None
        while self.running:
            proc_names = self.scanner.get_running_processes()
            active_game = self.scanner.find_active_game(proc_names, self.game_process_names)

            if active_game and self.current_game is None:
                self._start_session(active_game)
            elif not active_game and self.current_game is not None:
                self._end_current_session("game_closed")
            elif active_game and self.current_game and active_game != self.current_game:
                self._end_current_session("switched_game")
                self._start_session(active_game)

            now = datetime.now()
            if last_rule_check is None or (now - last_rule_check).total_seconds() >= 5:
                self._check_rules()
                last_rule_check = now

            time.sleep(SCAN_INTERVAL)

    def _start_session(self, active_game):
        self.current_game = active_game
        self.start_time = datetime.now()
        self.session_start_network_bytes = self.network_monitor.get_total_bytes()
        self.session_rule_flags = set()
        print(f"[{self.start_time.strftime('%H:%M:%S')}] Game '{active_game}' started")
        self._check_rules()

    def _end_current_session(self, end_reason):
        if not self.current_game or not self.start_time:
            return

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() / 60.0
        network_mb = self.get_current_session_network_mb()
        print(
            f"[{end_time.strftime('%H:%M:%S')}] Game '{self.current_game}' ended, "
            f"duration: {duration:.1f} min, network: {network_mb:.1f} MB"
        )
        self.data_logger.log_session(
            self.start_time,
            end_time,
            self.current_game,
            network_mb=network_mb,
            end_reason=end_reason,
            rule_flags=self.session_rule_flags,
        )
        self.current_game = None
        self.start_time = None
        self.session_start_network_bytes = None
        self.session_rule_flags = set()
        self.shutdown_triggered = False

    def _check_rules(self):
        pending_tasks = self.task_manager.get_pending_tasks()
        total_minutes = self.get_total_today_minutes(include_current=True)
        current_network_mb = self.get_current_session_network_mb()

        if self.current_game and pending_tasks:
            if "pending_tasks" not in self.session_rule_flags:
                print("WARNING: There are unfinished tasks. The child should finish tasks before gaming.")
            self.session_rule_flags.add("pending_tasks")

        if self.current_game and self.daily_limit > 0 and total_minutes >= self.daily_limit:
            if "daily_limit_exceeded" not in self.session_rule_flags:
                print(
                    f"WARNING: Daily limit of {self.daily_limit} minutes exceeded "
                    f"(current total: {total_minutes:.1f} minutes)."
                )
            self.session_rule_flags.add("daily_limit_exceeded")
            if self.auto_shutdown_enabled and not self.shutdown_triggered:
                self.shutdown_triggered = True
                print(f"Shutdown scheduled in {SHUTDOWN_GRACE_SECONDS} seconds.")
                threading.Timer(SHUTDOWN_GRACE_SECONDS, self._shutdown_pc).start()

        if self.current_game and self.network_limit_mb > 0 and current_network_mb >= self.network_limit_mb:
            if "network_limit_exceeded" not in self.session_rule_flags:
                print(
                    f"WARNING: Network traffic limit of {self.network_limit_mb:.1f} MB exceeded "
                    f"(current session: {current_network_mb:.1f} MB)."
                )
            self.session_rule_flags.add("network_limit_exceeded")

    def _shutdown_pc(self):
        if not self.auto_shutdown_enabled:
            return

        print("Shutting down now...")
        if sys.platform == "win32":
            os.system("shutdown /s /t 0")
        else:
            os.system("shutdown -h now")

    def get_total_today_minutes(self, include_current=False):
        total = self.data_logger.get_total_today()
        if include_current and self.current_game and self.start_time:
            total += self.get_current_session_minutes()
        return total

    def get_total_today_network_mb(self, include_current=False):
        total = self.data_logger.get_total_network_today()
        if include_current and self.current_game:
            total += self.get_current_session_network_mb()
        return total

    def get_current_session_minutes(self):
        if not self.current_game or not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds() / 60.0

    def get_current_session_network_mb(self):
        if self.session_start_network_bytes is None:
            return 0.0
        current_total_bytes = self.network_monitor.get_total_bytes()
        used_bytes = max(0, current_total_bytes - self.session_start_network_bytes)
        return self.network_monitor.bytes_to_megabytes(used_bytes)

    def set_limits(
        self,
        daily_limit_minutes=None,
        network_limit_mb=None,
        auto_shutdown_enabled=None,
    ):
        settings = self.settings_store.update_limits(
            daily_limit_minutes=daily_limit_minutes,
            network_limit_mb=network_limit_mb,
            auto_shutdown_enabled=auto_shutdown_enabled,
        )
        self.reload_settings()
        return settings

    def add_game(self, game_name):
        settings = self.settings_store.add_game(game_name)
        self.reload_settings()
        return settings["game_process_names"]

    def remove_game(self, game_name):
        settings = self.settings_store.remove_game(game_name)
        self.reload_settings()
        return settings["game_process_names"]

    def get_games(self):
        return sorted(self.game_process_names)

    def add_task(self, title, description=""):
        return self.task_manager.add_task(title, description)

    def update_task(self, task_id, title=None, description=None, completed=None):
        return self.task_manager.update_task(task_id, title, description, completed)

    def remove_task(self, task_id):
        self.task_manager.remove_task(task_id)

    def get_tasks(self):
        return self.task_manager.list_tasks()

    def get_status(self):
        pending_tasks = self.task_manager.get_pending_tasks()
        current_rule_flags = sorted(self.session_rule_flags)
        total_minutes = self.get_total_today_minutes(include_current=True)
        total_network_mb = self.get_total_today_network_mb(include_current=True)
        can_play = len(pending_tasks) == 0 and (
            self.daily_limit <= 0 or total_minutes < self.daily_limit
        )
        return {
            "is_monitoring": self.running,
            "current_game": self.current_game,
            "current_session_minutes": round(self.get_current_session_minutes(), 2),
            "current_session_network_mb": round(self.get_current_session_network_mb(), 2),
            "daily_limit_minutes": self.daily_limit,
            "network_limit_mb": self.network_limit_mb,
            "auto_shutdown_enabled": self.auto_shutdown_enabled,
            "today_total_minutes": round(total_minutes, 2),
            "today_total_network_mb": round(total_network_mb, 2),
            "pending_tasks_count": len(pending_tasks),
            "current_rule_flags": current_rule_flags,
            "can_play": can_play,
        }

    def get_today_stats(self):
        sessions = self.data_logger.load_today_sessions()
        game_times = {}
        game_network = {}
        for session in sessions:
            game_name = session["game_name"]
            game_times[game_name] = game_times.get(game_name, 0.0) + session["duration_min"]
            game_network[game_name] = game_network.get(game_name, 0.0) + session["network_mb"]

        if self.current_game:
            game_times[self.current_game] = game_times.get(self.current_game, 0.0) + self.get_current_session_minutes()
            game_network[self.current_game] = game_network.get(self.current_game, 0.0) + self.get_current_session_network_mb()

        return {
            "date": str(datetime.now().date()),
            "game_stats_minutes": {key: round(value, 2) for key, value in game_times.items()},
            "game_stats_network_mb": {key: round(value, 2) for key, value in game_network.items()},
            "total_minutes": round(sum(game_times.values()), 2),
            "total_network_mb": round(sum(game_network.values()), 2),
        }

    def get_recent_sessions(self, limit=20):
        return self.data_logger.get_recent_sessions(limit=limit)

    def show_daily_chart(self):
        import matplotlib.pyplot as plt

        stats = self.get_today_stats()["game_stats_minutes"]
        if not stats:
            print("No play data today.")
            return

        games = list(stats.keys())
        times = list(stats.values())
        plt.bar(games, times)
        plt.xlabel("Game")
        plt.ylabel("Minutes")
        plt.title(f"Play Time Today (Total: {sum(times):.1f} min)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def shutdown_now(self):
        self._shutdown_pc()


game_monitor = GameMonitor()
