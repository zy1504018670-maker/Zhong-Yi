import psutil
from config import GAME_PROCESS_NAMES

class ProcessScanner:
    @staticmethod
    def get_running_processes():
        proc_names = []
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name:
                    proc_names.append(name.lower())
            except:
                continue
        return proc_names

    @staticmethod
    def is_game(proc_name):
        return proc_name.lower() in {g.lower() for g in GAME_PROCESS_NAMES}

    @staticmethod
    def find_active_game(proc_names):
        for name in proc_names:
            if ProcessScanner.is_game(name):
                return name
        return None
