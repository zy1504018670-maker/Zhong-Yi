import threading
import uvicorn
from monitor import game_monitor
from api import app

def start_api():
    """启动 FastAPI 服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    # 启动监控后台线程
    game_monitor.start_monitoring()
    
    # 启动 API 服务器（阻塞当前线程，但不会阻塞监控线程）
    # 因为监控线程是 daemon=True，所以主线程退出时它会自动结束
    print("Starting REST API server at http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    start_api()

if __name__ == "__main__":
    main()
