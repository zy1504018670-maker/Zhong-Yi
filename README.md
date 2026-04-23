# Child Play Time Monitor

课程第二课题实现：基于 `task list control`、游戏进程扫描和网络流量统计的儿童游戏时长监测系统。项目提供本地后台监控、REST API、运行数据持久化、基础规则引擎、Docker 运行方式，以及课程要求里的设计文档与 UML 图。

## 1. 当前完成情况

### 已完成
- 监控指定游戏进程是否启动
- 记录每次游戏开始时间、结束时间、持续时长
- 统计当天总游玩时长
- 统计每次会话的网络流量
- 通过任务清单判断当前是否允许游戏
- 根据规则给出告警
- 支持每日时长限制
- 提供 REST API 管理游戏、任务、限制和统计数据
- 提供 Swagger 文档：`/docs`
- 提供 Dockerfile
- 提供 SRS、backlog、用例图、架构图、类图、时序图
- 提供基础单元测试

### 还可以继续增强
- 当前网络流量统计是系统总网卡流量增量，不是“单个游戏进程独占流量”
- 当前任务控制是“规则判断 + 告警”，不是强制结束游戏进程
- 没有图形界面，目前以 REST API 和数据文件为主
- 还没有更细的历史报表导出和权限认证

## 2. 课件要求对照分析

### Lesson 1
- `Backlog`：已提供，见 `backlog.csv`
- `Architecture`：已补充，见 `architecture_diagram.puml`
- `Use case diagram`：已补充，见 `use_case_diagram.puml`
- `SRS`：已整理，见 `SRS.md`

### Lesson 2
- `3` 个关键用例时序图：已补充，见 `sequence_diagram.puml`
- 类图：已补充，见 `UML_class_diagram.puml`
- 单元测试：已补充，见 `tests/`

### Lesson 3
- Variant 2 关键点：
  - `Get task list`：已实现
  - `Get game list`：已实现
  - `Check game start time`：已实现
  - `Calc game duration`：已实现
  - `Apply rules`：已实现
- 原始代码缺失的 `task list control` 和 `network traffic amount`：本次已补齐

### Lesson 4
- FastAPI 服务：已实现
- `/docs` 文档：已实现
- Docker 运行：已实现
- API 资源设计已按本项目重构为更符合第二课题的接口

## 3. 如何运行

### 本地运行
1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 启动项目：

```bash
python main.py
```

3. 打开浏览器查看接口文档：

```text
http://localhost:8000/docs
```

### 直接用 Uvicorn 启动

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Docker 运行
1. 构建镜像：

```bash
docker build -t child-monitor .
```

2. 运行容器：

```bash
docker run -p 8000:8000 child-monitor
```

## 4. 主要接口

- `GET /status`：查看当前监控状态、今日总时长、今日网络流量、是否允许游戏
- `GET /games`：查看监控的游戏列表
- `POST /games`：新增游戏进程名
- `DELETE /games/{game_name}`：删除游戏进程名
- `GET /tasks`：查看任务列表和摘要
- `POST /tasks`：新增任务
- `PATCH /tasks/{task_id}`：更新任务状态
- `DELETE /tasks/{task_id}`：删除任务
- `GET /limits`：查看规则限制
- `PUT /limits`：设置每日时长限制、网络限制、是否允许自动关机
- `GET /stats/today`：查看今日按游戏汇总的时长和流量
- `GET /sessions`：查看最近会话记录

## 5. 项目结构说明

```text
ChildMonitor/
├─ api.py                    FastAPI 接口入口
├─ main.py                   本地启动入口
├─ monitor.py                核心监控逻辑与规则判断
├─ process_scanner.py        扫描系统进程并识别游戏
├─ network_monitor.py        统计网络流量增量
├─ data_logger.py            会话日志读写
├─ settings_store.py         游戏列表和限制配置持久化
├─ task_manager.py           任务清单持久化与状态管理
├─ config.py                 全局配置项和默认路径
├─ playtime.csv              监控会话数据
├─ settings.json             持久化配置
├─ tasks.json                任务清单数据
├─ SRS.md                    软件需求规格说明
├─ backlog.csv               任务分解与时间估算
├─ architecture_diagram.puml 架构图
├─ use_case_diagram.puml     用例图
├─ UML_class_diagram.puml    类图
├─ sequence_diagram.puml     三个关键时序图
├─ Dockerfile                Docker 构建文件
├─ requirements.txt          Python 依赖
└─ tests/                    单元测试
```

## 6. 每个文件代表什么

- `api.py`：定义 REST 接口，并把接口请求转发给核心监控对象
- `main.py`：命令行启动入口
- `monitor.py`：整个系统的大脑，负责会话开始/结束、规则判断、统计聚合
- `process_scanner.py`：从系统进程列表里识别是否有目标游戏在运行
- `network_monitor.py`：读取系统网卡收发字节数并换算为 MB
- `data_logger.py`：把每次游戏会话写到 `playtime.csv`
- `settings_store.py`：保存游戏列表、每日时长限制、网络限制、自动关机开关
- `task_manager.py`：保存任务清单，并判断是否还有未完成任务
- `config.py`：默认游戏名、扫描周期、文件路径、默认限制
- `SRS.md`：课程要求中的需求说明文档
- `backlog.csv`：课程要求中的开发任务清单和时间估算
- `architecture_diagram.puml`：系统模块关系图
- `use_case_diagram.puml`：用户与系统交互图
- `UML_class_diagram.puml`：类之间的结构关系图
- `sequence_diagram.puml`：三条关键业务流程图
- `tests/test_monitor_core.py`：核心逻辑测试
- `tests/test_api.py`：REST API 测试

## 7. 规则说明

系统现在实现了三类规则：

1. `pending_tasks`
   - 如果还有未完成任务，系统会把当前状态标记为“不建议游戏”

2. `daily_limit_exceeded`
   - 如果今日累计游戏时长超过阈值，系统会产生告警
   - 出于安全考虑，`auto_shutdown_enabled` 默认关闭

3. `network_limit_exceeded`
   - 如果当前会话网络流量超过阈值，系统会产生告警

## 8. 验证方式

### 运行单元测试

```bash
python -m unittest discover -s tests -v
```

### 已验证通过
- 核心逻辑测试通过
- API 接口测试通过
- 项目可编译导入通过

## 9. 可以怎么演示给老师看

1. 运行 `python main.py`
2. 打开 `http://localhost:8000/docs`
3. 先在 `/tasks` 增加一个“未完成任务”
4. 再在 `/games` 查看或新增要监控的游戏进程名
5. 启动对应游戏
6. 查看 `/status` 和 `/stats/today`
7. 结束游戏后查看 `playtime.csv` 中的会话记录

## 10. 安全说明

- 自动关机功能默认关闭，避免演示时误关机
- 如果确实要测试自动关机，请在 `/limits` 中显式设置 `auto_shutdown_enabled=true`
