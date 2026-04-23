# Software Requirements Specification

## 1. Introduction

### 1.1 Purpose
This system helps parents evaluate a child's play time on a personal computer using game process monitoring, household task control, and network traffic statistics.

### 1.2 Scope
The system runs on a PC, detects target games by process name, records play sessions, checks whether required tasks are completed, estimates network usage during the session, applies control rules, and exposes a REST API for configuration and reporting.

### 1.3 Stakeholders
- Parent or guardian
- Child
- Teacher or mentor reviewing the coursework

## 2. Overall Description

### 2.1 Product Perspective
The application is a standalone backend service. It interacts with the operating system process table, local files, and HTTP clients.

### 2.2 Product Functions
- Monitor running processes every few seconds
- Detect when a configured game starts or ends
- Record session start time, end time, duration, and network usage
- Store and manage a household task list
- Decide whether the child is allowed to play based on pending tasks and configured limits
- Provide aggregated statistics for the current day
- Provide REST API endpoints for management and monitoring

### 2.3 User Characteristics
- Parent:
  - configures games
  - manages tasks
  - checks statistics
  - sets limits
- Child:
  - is indirectly monitored by the system

### 2.4 Constraints
- Game recognition is based on process names
- Network traffic is measured at machine level, not per-process level
- The project is implemented in Python with FastAPI

## 3. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | The system shall scan running processes every `5` seconds by default. |
| FR2 | The system shall recognize a game if its process name exists in the configured game list. |
| FR3 | The system shall detect the start time of a game session. |
| FR4 | The system shall detect the end time of a game session. |
| FR5 | The system shall calculate the duration of each game session in minutes. |
| FR6 | The system shall store session history in a CSV file. |
| FR7 | The system shall store a list of household tasks in a local file. |
| FR8 | The system shall allow tasks to be marked as completed or pending. |
| FR9 | The system shall calculate whether the child can play based on pending tasks and the daily limit. |
| FR10 | The system shall estimate network usage during the current session. |
| FR11 | The system shall warn when the daily time limit is exceeded. |
| FR12 | The system shall warn when the network limit is exceeded. |
| FR13 | The system shall provide REST endpoints to manage games. |
| FR14 | The system shall provide REST endpoints to manage tasks. |
| FR15 | The system shall provide REST endpoints to configure limits. |
| FR16 | The system shall provide REST endpoints to return current status and daily statistics. |
| FR17 | The system shall expose API documentation through Swagger UI. |
| FR18 | The system shall support containerized execution with Docker. |

## 4. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | The system shall start on a standard Python environment using `pip install -r requirements.txt`. |
| NFR2 | The system shall store data in simple local files so the coursework can be demonstrated without a database. |
| NFR3 | The system shall be understandable for educational review and contain diagrams and tests. |
| NFR4 | The system shall use input validation for REST requests. |
| NFR5 | The automatic shutdown option shall be disabled by default for safety. |

## 5. External Interfaces

### 5.1 REST API
- `GET /status`
- `GET /games`
- `POST /games`
- `DELETE /games/{game_name}`
- `GET /tasks`
- `POST /tasks`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `GET /limits`
- `PUT /limits`
- `GET /stats/today`
- `GET /sessions`

### 5.2 File Interfaces
- `playtime.csv` for session history
- `settings.json` for configuration
- `tasks.json` for task list

## 6. Acceptance Criteria

- The application runs locally and via Docker
- A target game process can be configured and detected
- Session records are written to CSV
- Tasks can be created and completed
- REST API documentation is available at `/docs`
- Unit tests execute successfully
