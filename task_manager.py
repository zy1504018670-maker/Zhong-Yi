import json
from datetime import datetime
from pathlib import Path

from config import TASKS_FILE


class TaskManager:
    def __init__(self, path=TASKS_FILE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_exists()

    def ensure_exists(self):
        if not self.path.exists():
            self.save([])

    def load(self):
        self.ensure_exists()
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, tasks):
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(tasks, file, ensure_ascii=False, indent=2)

    def list_tasks(self):
        return self.load()

    def get_pending_tasks(self):
        return [task for task in self.load() if not task["completed"]]

    def add_task(self, title, description=""):
        tasks = self.load()
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Task title cannot be empty")
        next_id = max((task["id"] for task in tasks), default=0) + 1
        task = {
            "id": next_id,
            "title": normalized_title,
            "description": description.strip(),
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
        }
        tasks.append(task)
        self.save(tasks)
        return task

    def update_task(self, task_id, title=None, description=None, completed=None):
        tasks = self.load()
        for task in tasks:
            if task["id"] != task_id:
                continue

            if title is not None:
                normalized_title = title.strip()
                if not normalized_title:
                    raise ValueError("Task title cannot be empty")
                task["title"] = normalized_title
            if description is not None:
                task["description"] = description.strip()
            if completed is not None:
                task["completed"] = completed
                task["completed_at"] = datetime.now().isoformat() if completed else None
            self.save(tasks)
            return task
        raise ValueError("Task not found")

    def remove_task(self, task_id):
        tasks = self.load()
        updated_tasks = [task for task in tasks if task["id"] != task_id]
        if len(updated_tasks) == len(tasks):
            raise ValueError("Task not found")
        self.save(updated_tasks)

    def summary(self):
        tasks = self.load()
        completed_count = sum(1 for task in tasks if task["completed"])
        return {
            "total": len(tasks),
            "completed": completed_count,
            "pending": len(tasks) - completed_count,
        }
