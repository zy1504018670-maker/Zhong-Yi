# Child Play Time Monitor

## 功能
- 监控指定游戏进程，记录游戏时长
- 每日时间限制，超时自动关机
- 提供 REST API 管理游戏列表和获取统计
- 支持 Docker 运行

## 本地运行
1. 安装依赖：`pip install -r requirements.txt`
2. 运行：`python main.py`
3. 打开浏览器访问 http://localhost:8000/docs

## Docker 运行
1. 构建镜像：`docker build -t child-monitor .`
2. 运行容器：`docker run -p 8000:8000 child-monitor`

## API 端点示例
- `GET /games` 查看监控的游戏
- `POST /games` 添加游戏（JSON: {"name": "game.exe"}）
- `GET /stats/today` 查看今日统计
- `PUT /limit` 设置时间限制（JSON: {"limit": 90}）