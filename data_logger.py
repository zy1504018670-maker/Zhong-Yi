import csv
import os
from datetime import datetime, date

class DataLogger:
    CSV_FILE = "playtime.csv"

    @staticmethod
    def init_csv():
        if not os.path.exists(DataLogger.CSV_FILE):
            with open(DataLogger.CSV_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["start_time", "end_time", "game_name", "duration_min"])

    @staticmethod
    def log_session(start, end, game_name):
        duration = (end - start).total_seconds() / 60.0
        with open(DataLogger.CSV_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([start.isoformat(), end.isoformat(), game_name, round(duration, 2)])

    @staticmethod
    def load_today_sessions():
        today = date.today()
        sessions = []
        if not os.path.exists(DataLogger.CSV_FILE):
            return sessions
        with open(DataLogger.CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                start = datetime.fromisoformat(row['start_time'])
                if start.date() == today:
                    end = datetime.fromisoformat(row['end_time'])
                    sessions.append((start, end, row['game_name'], float(row['duration_min'])))
        return sessions

    @staticmethod
    def get_total_today():
        return sum(s[3] for s in DataLogger.load_today_sessions())
