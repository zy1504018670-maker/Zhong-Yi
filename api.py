from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from monitor import GameMonitor, game_monitor


class GameName(BaseModel):
    name: str = Field(..., min_length=1)


class LimitSettings(BaseModel):
    daily_limit_minutes: int | None = Field(default=None, ge=0)
    network_limit_mb: float | None = Field(default=None, ge=0)
    auto_shutdown_enabled: bool | None = None


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


def create_app(monitor_instance: GameMonitor | None = None, manage_lifecycle=True):
    monitor_instance = monitor_instance or game_monitor

    if manage_lifecycle:
        @asynccontextmanager
        async def lifespan(app):
            app.state.game_monitor.start_monitoring()
            yield
            app.state.game_monitor.stop_monitoring()
    else:
        @asynccontextmanager
        async def lifespan(app):
            yield

    app = FastAPI(
        title="Child Play Time Monitor API",
        version="2.0.0",
        description="REST API for monitoring game playtime, household tasks, and network usage.",
        lifespan=lifespan,
    )
    app.state.game_monitor = monitor_instance

    def current_monitor():
        return app.state.game_monitor

    @app.get("/")
    def root():
        return {
            "message": "Child Play Time Monitor API is running",
            "docs": "/docs",
        }

    @app.get("/status")
    def get_status():
        return current_monitor().get_status()

    @app.get("/games")
    def get_games():
        return {"games": current_monitor().get_games()}

    @app.post("/games", status_code=201)
    def add_game(game: GameName):
        try:
            games = current_monitor().add_game(game.name)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return {"message": f"Game '{game.name}' added", "games": games}

    @app.delete("/games/{game_name}")
    def delete_game(game_name: str):
        try:
            games = current_monitor().remove_game(game_name)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return {"message": f"Game '{game_name}' removed", "games": games}

    @app.get("/tasks")
    def get_tasks():
        tasks = current_monitor().get_tasks()
        return {
            "tasks": tasks,
            "summary": current_monitor().task_manager.summary(),
        }

    @app.post("/tasks", status_code=201)
    def add_task(task: TaskCreate):
        try:
            created_task = current_monitor().add_task(task.title, task.description)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return {"message": "Task added", "task": created_task}

    @app.patch("/tasks/{task_id}")
    def update_task(task_id: int, task: TaskUpdate):
        try:
            updated_task = current_monitor().update_task(
                task_id,
                title=task.title,
                description=task.description,
                completed=task.completed,
            )
        except ValueError as error:
            status_code = 400 if "empty" in str(error).lower() else 404
            raise HTTPException(status_code=status_code, detail=str(error)) from error
        return {"message": "Task updated", "task": updated_task}

    @app.delete("/tasks/{task_id}")
    def delete_task(task_id: int):
        try:
            current_monitor().remove_task(task_id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return {"message": "Task removed"}

    @app.get("/limits")
    def get_limits():
        status = current_monitor().get_status()
        return {
            "daily_limit_minutes": status["daily_limit_minutes"],
            "network_limit_mb": status["network_limit_mb"],
            "auto_shutdown_enabled": status["auto_shutdown_enabled"],
        }

    @app.put("/limits")
    def update_limits(settings: LimitSettings):
        if (
            settings.daily_limit_minutes is None
            and settings.network_limit_mb is None
            and settings.auto_shutdown_enabled is None
        ):
            raise HTTPException(status_code=400, detail="At least one limit field must be provided")

        updated = current_monitor().set_limits(
            daily_limit_minutes=settings.daily_limit_minutes,
            network_limit_mb=settings.network_limit_mb,
            auto_shutdown_enabled=settings.auto_shutdown_enabled,
        )
        return {"message": "Limits updated", "settings": updated}

    @app.get("/stats/today")
    def get_today_stats():
        return current_monitor().get_today_stats()

    @app.get("/sessions")
    def get_recent_sessions(limit: int = 20):
        return {"sessions": current_monitor().get_recent_sessions(limit=limit)}

    return app


app = create_app()
