import csv
from datetime import date, datetime
from pathlib import Path

from config import PLAYTIME_CSV


class DataLogger:
    FIELDNAMES = [
        "start_time",
        "end_time",
        "game_name",
        "duration_min",
        "network_mb",
        "end_reason",
        "rule_flags",
    ]

    def __init__(self, csv_file=PLAYTIME_CSV):
        self.csv_file = Path(csv_file)
        self.init_csv()

    def init_csv(self):
        self.csv_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.csv_file.exists():
            with self.csv_file.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
                writer.writeheader()
            return

        with self.csv_file.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            existing_fields = reader.fieldnames or []
            rows = list(reader)

        if existing_fields == self.FIELDNAMES:
            return

        upgraded_rows = []
        for row in rows:
            upgraded_row = {field: row.get(field, "") for field in self.FIELDNAMES}
            upgraded_rows.append(upgraded_row)

        with self.csv_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(upgraded_rows)

    def log_session(
        self,
        start,
        end,
        game_name,
        network_mb=0.0,
        end_reason="game_closed",
        rule_flags=None,
    ):
        duration = (end - start).total_seconds() / 60.0
        with self.csv_file.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
            writer.writerow(
                {
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                    "game_name": game_name,
                    "duration_min": round(duration, 2),
                    "network_mb": round(network_mb, 2),
                    "end_reason": end_reason,
                    "rule_flags": ",".join(sorted(rule_flags or [])),
                }
            )

    def load_today_sessions(self):
        today = date.today()
        sessions = []
        if not self.csv_file.exists():
            return sessions

        with self.csv_file.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                start = datetime.fromisoformat(row["start_time"])
                if start.date() != today:
                    continue

                end = datetime.fromisoformat(row["end_time"])
                sessions.append(
                    {
                        "start_time": start,
                        "end_time": end,
                        "game_name": row["game_name"],
                        "duration_min": float(row.get("duration_min") or 0.0),
                        "network_mb": float(row.get("network_mb") or 0.0),
                        "end_reason": row.get("end_reason") or "game_closed",
                        "rule_flags": [
                            value
                            for value in (row.get("rule_flags") or "").split(",")
                            if value
                        ],
                    }
                )
        return sessions

    def get_total_today(self):
        return sum(session["duration_min"] for session in self.load_today_sessions())

    def get_total_network_today(self):
        return sum(session["network_mb"] for session in self.load_today_sessions())

    def get_recent_sessions(self, limit=20):
        if not self.csv_file.exists():
            return []

        with self.csv_file.open("r", newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        recent_rows = rows[-limit:]
        recent_sessions = []
        for row in reversed(recent_rows):
            recent_sessions.append(
                {
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "game_name": row["game_name"],
                    "duration_min": float(row.get("duration_min") or 0.0),
                    "network_mb": float(row.get("network_mb") or 0.0),
                    "end_reason": row.get("end_reason") or "game_closed",
                    "rule_flags": [
                        value
                        for value in (row.get("rule_flags") or "").split(",")
                        if value
                    ],
                }
            )
        return recent_sessions
