# Implementation Plan - Family Chore Gamification System (MVP)

This plan outlines the steps to build the Minimum Viable Product (MVP) of the ChoreSpec system, focusing on the core loop: Setup → Assignment → Calculation → Goal Tracking → Admin Validation.

## Phase 1: Project Initialization & Environment Setup
- [ ] **Initialize Project Structure**
    - Create project directories (`backend`, `frontend`, `scripts`).
    - Set up a Python virtual environment.
    - Initialize a Git repository.
- [ ] **Backend Setup (FastAPI)**
    - Install dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`).
    - Create basic FastAPI app structure (`main.py`, `database.py`, `models.py`, `schemas.py`, `crud.py`).
    - Verify server runs locally.
- [ ] **Frontend Setup (React + Vite)**
    - Initialize React app with Vite and TypeScript.
    - Install core dependencies (`axios`, `react-router-dom`, `tanstack-query` (optional but recommended)).
    - Set up basic folder structure (`components`, `pages`, `api`, `types`).
    - Install a CSS framework or set up vanilla CSS variables for the "Premium" design.

## Phase 2: Database & Core Backend Logic
- [ ] **Database Implementation**
    - Implement SQLAlchemy models based on `sqlalchemy-orm-model.py`.
    - Create a database initialization script (`init_db.py`) to create tables.
    - **Verification**: Run script and check `chorespec_mvp.db` is created with correct schema.
- [ ] **Seed Data Script**
    - Create a script to seed initial Roles (Admin, Teenager, Child) and a default Admin user.
    - **Verification**: Query database to confirm seed data exists.
- [ ] **API: User Management (Story 1)**
    - Implement `POST /users` (Create User).
    - Implement `POST /login` (Simple PIN auth, return user details/token).
    - Implement `GET /users` (List users for Admin).
    - **Verification**: Test creating a user and logging in via Swagger UI.
- [ ] **API: Role Management (Story 2)**
    - Implement `GET /roles` (List roles).
    - Implement `PUT /roles/{id}` (Update multiplier).
    - **Verification**: Update a multiplier and verify it persists.

## Phase 3: Task Management & Core Loop
- [ ] **API: Task Creation (Story 3)**
    - Implement `POST /tasks` (Create Task definition).
    - **Verification**: Create a task and verify it exists in DB.
- [ ] **Task Instantiation Logic (The "Daily" Engine)**
    - Create a utility function/script to generate `TaskInstance` records for the day based on `Tasks`.
    - Implement an endpoint `POST /daily-reset` (or similar) to trigger this manually for MVP.
    - **Verification**: Run reset, check `TaskInstance` table for new rows with correct `due_time`.
- [ ] **API: Task Execution (Story 3 & 4)**
    - Implement `GET /tasks/daily/{user_id}` (Get user's daily tasks).
    - Implement `POST /tasks/{instance_id}/complete` (Mark complete).
        - **Critical Logic**: Calculate points: `Base * RoleMultiplier`.
        - Create a `Transaction` record.
        - Update User's `current_points` and `lifetime_points`.
    - **Verification**: Complete a task, check User points increased correctly.

## Phase 4: Rewards & Goals
- [ ] **API: Rewards (Story 5)**
    - Implement `GET /rewards` (List catalog).
    - Implement `POST /rewards` (Admin create reward - optional for MVP but needed for data).
    - Implement `POST /users/{id}/goal` (Set current goal).
- [ ] **Frontend: Reward Hub**
    - Display Reward Catalog.
    - Implement "Set as Goal" functionality.
    - Show Progress Bar for current goal.

## Phase 5: Admin Reporting & Frontend Polish
- [ ] **API: Reporting (Story 4)**
    - Implement `GET /reports/weekly` (Aggregated data for charts).
- [ ] **Frontend: Admin Dashboard**
    - User Management View.
    - Task Creation Form.
    - Reporting Charts (Completion Rates, etc.).
- [ ] **Frontend: User Dashboard**
    - Daily Task List (Interactive).
    - Current Point Balance.
    - Goal Progress.
- [ ] **Design Polish**
    - Apply "Premium" aesthetics (Glassmorphism, animations).
    - Ensure responsive design for mobile (Tablets/Phones).

## Phase 6: Final Validation
- [ ] **End-to-End Testing**
    - Walk through the full flow: Create User -> Assign Role -> Create Task -> Generate Daily Instances -> User Completes Task -> Points Awarded -> Goal Progress Updated.
- [ ] **Deployment Prep**
    - Create `Dockerfile`.
    - Document running instructions.
