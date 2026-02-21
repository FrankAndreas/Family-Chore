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
- **Transactions**: Every point change is recorded as an immutable transaction (`EARN`, `REDEEM`, or `PENALTY`).
- **Penalties / Negative Points**:
  - Admins can manually deduct points from users for missed chores or misbehavior.
  - Penalties deduct from `current_points` (spendable balance) but do NOT reduce `lifetime_points` (to prevent demotion from unlocked tiers).
  - A required "Reason" (text) is attached to the penalty transaction for transparency.
- **Gamification Polish (V1.2)**:
  - **Daily First Task Bonus**: The first task completed by a user each day awards a flat `+5` bonus points (`bonus_points`).
  - **Streak Multiplier (Future/Optional)**: Consecutive days of completing at least one task add a `+0.1` additive bonus to the user's role multiplier (capped at `+0.5`). 

### 2.3 Task Management (The Engine)
#### Task Templates (`Task`)
- **Base Points**: The raw value of the chore.
- **Targeting**: 
  - **Specific Role**: Only users in that role see the task.
  - **All Family Members** (`assigned_role_id = null`): All users see and can claim the task.
- **Photo Requirement**: Tasks can be flagged as `requires_photo_verification`, routing completions to an admin `IN_REVIEW` queue before points are awarded.

#### Scheduling Types
1. **Daily**: Appears every day at a specific `HH:MM`.
2. **Weekly**: Appears once a week on a specific day (e.g., "Saturday").
3. **Recurring**: Flexible tasks with a cooldown period.
   - `recurrence_min_days`: Minimum days that must pass before the task reappears (globally).

#### Task Instances (`TaskInstance`)
- Realized chores generated from templates.
- **States**: `PENDING`, `IN_REVIEW`, `COMPLETED`.
- **Claiming Logic**: A user can complete an instance assigned to a different user; the system automatically reassigns that instance to the "claimer" for reward allocation.

### 2.4 Reward Hub
- **Catalog**: Global list of available rewards with point costs and tier levels.
- **Goal Setting**: Users can select one active "Goal".
- **Progress Tracking**: UI visualizes progress toward the goal (Points Earned vs. Cost) with pulse animations for affordable items.
- **Tiered Unlocks (V1.1)**:
  - Rewards are grouped into **Bronze** (Default), **Silver** (300 LP), and **Gold** (1000 LP) tiers (adjusted from 500/1500 for faster early progression).
  - Tiers unlock based on `lifetime_points`. Spending points does not demote a user.
  - Locked rewards are visible but desaturated and unclickable to drive aspiration.
- **Reward Hub UI Polish (V1.3)**:
  - **Tiered Layout**: Visually separate rewards into distinct sections based on their tier (Bronze, Silver, Gold) rather than a single flat list.
  - **Aesthetics**: Apply premium "Glassmorphism" styling to reward cards, including subtle hover effects and improved typography.
  - **Animations**: Implement smooth entry animations for reward cards and a celebratory "pulse" or highlight effect when a reward becomes affordable.
  - **Redemption Modal**: Enhance the redemption confirmation modal with better visual hierarchy, clearly showing the point cost and remaining balance.
- **Celebration**: Visual confetti effect upon unlocking a new tier or redeeming a high-value reward.
- **Admin Override**: Admins see all rewards as unlocked for management purposes.

### 2.5 Analytics & Compliance
- **Goal**: Provide transparency into household chore contributions and reward distribution.
- **Weekly Activity Chart**:
  - Visualizes "Tasks Completed" per user over the last 7 days.
  - grouped by Date and User.
- **Fairness Distribution**:
  - Pie chart showing the percentage share of Total Points Earned by each user.
  - Helps identify if one user is carrying the load.
- **Access**: Available to all users to promote healthy competition and accountability.

### 2.6 System Polish & Hardening (V1.4)
- **Deployment Hardening**: Provide a production-ready Docker setup, including environment variable management, non-root user execution, and network isolation.
- **CI/CD Pipeline**: Add GitHub Actions pipelines for automated testing, linting (`flake8`, `mypy`, `eslint`), and build verification on every pull request.
- **UI/UX Consistency**: Ensure consistent styling across all views, specifically focusing on mobile responsiveness, accessible form controls, robust generic empty states, and standardizing error handling.

### 2.7 Notifications & Reminders (V1.5)
- **Channels**: Web Push notifications (using service workers + VAPID) or lightweight Email integration (e.g., SMTP or Resend).
- **Triggers**:
  - **Daily Reminders**: Sent to users with pending daily tasks at a configurable time.
  - **Approval Requests**: Sent to admins when a photo-verification task enters the `IN_REVIEW` queue.
- **Opt-in/Opt-out**: Users can configure their notification preferences in their profile settings.

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
- **Charting**: Using `recharts` for responsive, animated graphs.
- **Features**:
  - **Admin Context**: Full management of Users, Roles, and Task Templates.
  - **User Context**: Personalized dashboard, active goal tracking, and task completion flow.
  - **Family Dashboard**: Dedicated "God Mode" view for shared task oversight.
  - **Analytics Dashboard**: Visual reports for compliance and stats.

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
- `GET /tasks/review-queue`: Admin view of tasks pending photo verification.
- `POST /tasks/{id}/upload-photo`: Provide evidence for verification.
- `POST /tasks/{id}/complete`: The core "payday" endpoint. (Transitions to IN_REVIEW if photo required).
- `POST /tasks/{id}/review`: Admin approval/rejection of verified tasks.

### Analytics
- `GET /analytics/weekly`: Last 7 days task completion stats.
- `GET /analytics/distribution`: Lifetime points share per user.

### System
- `POST /daily-reset/`: Manual trigger for task generation.
- `GET /events`: SSE stream for UI updates.
- `GET/PUT /settings/language/default`: Global localization toggle.

### 4.1 BDD Scenarios (Negative Points / Penalties)
**Scenario: Admin applies a penalty**
- **Given** an Admin is logged in and viewing a user with 100 `current_points` and 500 `lifetime_points`
- **When** the Admin submits a penalty of 20 points with reason "Missed trash" for that user
- **Then** the user's `current_points` becomes 80
- **And** the user's `lifetime_points` remains 500
- **And** a `PENALTY` transaction is recorded in the activity log with "Missed trash"
- **And** a real-time event is broadcasted to update the user's UI.

**Scenario: Penalty prevents negative balance**
- **Given** a user has 10 `current_points`
- **When** the Admin applies a penalty of 20 points
- **Then** the user's `current_points` becomes 0 (assuming floor is 0) *or* -10 (depending on Architect's plan, let's leave it up to Architect or state it explicitly: balance can go negative). Let's specify: The user's `current_points` can become negative (e.g., -10) to reflect a point debt.

### 4.2 BDD Scenarios (Push Notifications / Reminders)
**Scenario: Daily Chore Reminder**
- **Given** a user has incomplete "Daily" tasks assigned for today
- **When** the configured daily reminder time is reached
- **Then** a push notification or email is dispatched to the user's configured contact method
- **And** the notification lists the number of pending tasks.

**Scenario: Task Approval Notification**
- **Given** a user completes a task that `requires_photo_verification`
- **When** the task transitions to `IN_REVIEW`
- **Then** a notification is immediately dispatched to users with the "Admin" role
- **And** the notification contains the task name and the user who completed it.

---

## 5. Current Implementation Delta (vs. MVP Spec)
The system has exceeded the original MVP spec in several ways:
1. **Recurring Task Logic**: Full cooldown implementation is active in `crud.py`.
2. **SSE Integration**: The backend broadcasts real-time updates for UI reactivity.
3. **Flexible Assignment**: The "Claim" logic for tasks assigned to others is fully functional.
4. **I18N Support**: The database and models are already prepared for multi-language support.
5. **Photo Support**: The schema already supports photo verification (V1.1 feature).
