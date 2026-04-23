import psutil


class ProcessScanner:
    @staticmethod
    def get_running_processes():
        proc_names = []
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"]
                if name:
                    proc_names.append(name.lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return proc_names

    @staticmethod
    def is_game(proc_name, game_process_names):
        normalized = {game_name.lower() for game_name in game_process_names}
        return proc_name.lower() in normalized

    @staticmethod
    def find_active_game(proc_names, game_process_names):
        for name in proc_names:
            if ProcessScanner.is_game(name, game_process_names):
                return name
        return None
