# Software Requirements Specification – Child Play Time Monitor

## 1. Introduction
### 1.1 Purpose
Control children's gaming time on PC.

### 1.2 Scope
Windows/Linux, monitors game processes, logs playtime, provides statistics, auto-shutdown.

## 2. Overall Description
### 2.1 Product Functions
- Process scanning every 5 seconds
- Game session detection
- CSV logging
- Daily chart
- Time limit with shutdown
- REST API for remote management

### 2.2 User Characteristics
Parents: configure games/limits; Children: no interaction.

## 3. Specific Requirements
| ID | Requirement |
|----|-------------|
| FR1 | Scan processes every 5s |
| FR2 | Detect game by name |
| FR3 | Log start/end times |
| FR4 | Compute daily total |
| FR5 | Show bar chart |
| FR6 | Set daily limit |
| FR7 | Shutdown when limit exceeded |
| FR8 | REST API CRUD for games |
| FR9 | REST API statistics |