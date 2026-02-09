# Reverse-Engineered System Specification: ChoreSpec

**Author**: Antigravity (Product Owner Agent)  
**Date**: 2026-02-07  
**Status**: Finalized from Implementation (v1.1+)

---

## 1. System Overview
ChoreSpec is a family-oriented chore gamification system. It transforms household tasks into a reward-based economy using role-based multipliers and goal-oriented progress tracking.

### Core Value Proposition
- **Gamification**: Real-time point earning and reward redemption.
- **Fairness**: Role-based multipliers adjust effort-to-reward ratios (e.g., a child earns 1.5x points for the same task an adult earns 1.0x for).
- **Automation**: Automatic daily/weekly/recurring task generation with a midnight reset.
- **Accountability**: Audit trail of all point transactions and task completions.

---

## 2. Functional Architecture

### 2.1 User & Identity Management
- **Authentication**: Lightweight PIN-based login (Nickname + 4-digit PIN).
- **Roles**: Users are assigned exactly one role.
- **Stats**: Individual tracking of `current_points` (spendable) and `lifetime_points` (cumulative effort).
- **Localization**: User-level `preferred_language` support (overrides system default).

### 2.2 Role & Economy Logic
- **Multipliers**: Each role has an editable `multiplier_value` (minimum 0.1).
- **Point Calculation**: 
  `Awarded Points = floor(Base Task Points * User Role Multiplier)`
- **Transactions**: Every point change is recorded as an immutable transaction (`EARN` or `REDEEM`).

### 2.3 Task Management (The Engine)
#### Task Templates (`Task`)
- **Base Points**: The raw value of the chore.
- **Targeting**: 
  - **Specific Role**: Only users in that role see the task.
  - **All Family Members** (`assigned_role_id = null`): All users see and can claim the task.
- **Photo Requirement**: Tasks can be flagged as `requires_photo_verification`.

#### Scheduling Types
1. **Daily**: Appears every day at a specific `HH:MM`.
2. **Weekly**: Appears once a week on a specific day (e.g., "Saturday").
3. **Recurring**: Flexible tasks with a cooldown period.
   - `recurrence_min_days`: Minimum days that must pass before the task reappears (globally).

#### Task Instances (`TaskInstance`)
- Realized chores generated from templates.
- **States**: `PENDING`, `COMPLETED`.
- **Claiming Logic**: A user can complete an instance assigned to a different user; the system automatically reassigns that instance to the "claimer" for reward allocation.

### 2.4 Reward Hub
- **Catalog**: Global list of available rewards with point costs and tier levels.
- **Goal Setting**: Users can select one active "Goal".
- **Progress Tracking**: UI visualizes progress toward the goal (Points Earned vs. Cost) with pulse animations for affordable items.
- **Tiered Unlocks (V1.1)**:
  - Rewards are grouped into **Bronze** (Default), **Silver** (500 LP), and **Gold** (1500 LP) tiers.
  - Tiers unlock based on `lifetime_points`. Spending points does not demote a user.
  - Locked rewards are visible but desaturated and unclickable to drive aspiration.
- **Celebration**: Visual confetti effect upon unlocking a new tier.
- **Admin Override**: Admins see all rewards as unlocked for management purposes.

---

## 3. Technical Implementation

### 3.1 Backend (FastAPI + SQLAlchemy)
- **Database**: SQLite (`chorespec_mvp.db`).
- **Real-time Engine**: 
  - **SSE (Server-Sent Events)**: Broadcasters for `task_created`, `task_deleted`, and `task_completed` events.
  - **Background Scheduler**: `APScheduler` performs a "Daily Reset" at 00:00 every night.
- **Stateful Resets**: Uses `SystemSettings` to track `last_daily_reset` ensuring no missed or duplicate generations on server restarts.

### 3.2 Frontend (React + Vite + TypeScript)
- **Design System**: Premium "Glassmorphism" design with vanilla CSS.
- **State Management**: React Context/Hooks with Axios/Fetch for REST API.
- **Features**:
  - **Admin Context**: Full management of Users, Roles, and Task Templates.
  - **User Context**: Personalized dashboard, active goal tracking, and task completion flow.
  - **Family Dashboard**: Dedicated "God Mode" view for shared task oversight.

---

## 4. API Specification (Summary)

### Management
- `POST /users/`, `GET /users/`
- `POST /login/` (Nickname + PIN matching)
- `GET /roles/`, `PUT /roles/{id}` (Multiplier update)

### Task Flow
- `POST /tasks/`: Create template (auto-generates instances for today).
- `GET /tasks/daily/{user_id}`: Personalized task list.
- `GET /tasks/pending`: Global view of all uncompleted chores.
- `POST /tasks/{id}/complete`: The core "payday" endpoint.

### System
- `POST /daily-reset/`: Manual trigger for task generation.
- `GET /events`: SSE stream for UI updates.
- `GET/PUT /settings/language/default`: Global localization toggle.

---

## 5. Current Implementation Delta (vs. MVP Spec)
The system has exceeded the original MVP spec in several ways:
1. **Recurring Task Logic**: Full cooldown implementation is active in `crud.py`.
2. **SSE Integration**: The backend broadcasts real-time updates for UI reactivity.
3. **Flexible Assignment**: The "Claim" logic for tasks assigned to others is fully functional.
4. **I18N Support**: The database and models are already prepared for multi-language support.
5. **Photo Support**: The schema already supports photo verification (V1.1 feature).
