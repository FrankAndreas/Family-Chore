# Implementation Plan - Family Chore Gamification System (MVP)

This plan outlines the steps to build the Minimum Viable Product (MVP) of the ChoreSpec system, focusing on the core loop: Setup → Assignment → Calculation → Goal Tracking → Admin Validation.

## Phase 1: Project Initialization & Environment Setup
- [x] **Initialize Project Structure**
    - Create project directories (`backend`, `frontend`, `scripts`).
    - Set up a Python virtual environment.
    - Initialize a Git repository.
- [x] **Backend Setup (FastAPI)**
    - Install dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`).
    - Create basic FastAPI app structure (`main.py`, `database.py`, `models.py`, `schemas.py`, `crud.py`).
    - Verify server runs locally.
- [x] **Frontend Setup (React + Vite)**
    - Initialize React app with Vite and TypeScript.
    - Install core dependencies (`axios`, `react-router-dom`).
    - Set up basic folder structure (`components`, `pages`, `api`, `types`).
    - Set up vanilla CSS variables for the "Premium" design.

## Phase 2: Database & Core Backend Logic
- [x] **Database Implementation**
    - Implement SQLAlchemy models.
    - Create a database initialization script (`init_db.py`) to create tables.
    - **Verification**: Run script and check `chorespec_mvp.db` is created with correct schema.
- [x] **Seed Data Script**
    - Create a script to seed initial Roles (Admin, Teenager, Child) and a default Admin user.
    - **Verification**: Query database to confirm seed data exists.
- [x] **API: User Management (Story 1)**
    - Implement `POST /users` (Create User).
    - Implement `POST /login` (Simple PIN auth).
    - Implement `GET /users` (List users for Admin).
    - **Verification**: Test creating a user and logging in via Swagger UI.
- [x] **API: Role Management (Story 2)**
    - Implement `GET /roles` (List roles).
    - Implement `PUT /roles/{id}` (Update multiplier).
    - **Verification**: Update a multiplier and verify it persists.

## Phase 3: Task Management & Core Loop
- [x] **API: Task Creation (Story 3)**
    - Implement `POST /tasks` (Create Task definition).
    - **Verification**: Create a task and verify it exists in DB.
- [x] **Task Instantiation Logic (The "Daily" Engine)**
    - Create a utility function to generate `TaskInstance` records.
    - Implement an endpoint `POST /daily-reset` to trigger this.
    - **Verification**: Run reset, check `TaskInstance` table for new rows.
- [x] **API: Task Execution (Story 3 & 4)**
    - Implement `GET /tasks/daily/{user_id}` (Get user's daily tasks).
    - Implement `POST /tasks/{instance_id}/complete` (Mark complete).
        - **Critical Logic**: Calculate points: `Base * RoleMultiplier`.
        - Create a `Transaction` record.
        - Update User's `current_points` and `lifetime_points`.
    - **Verification**: Complete a task, check User points increased correctly.

## Phase 4: Rewards & Goals
- [x] **API: Rewards (Story 5)**
    - Implement `GET /rewards` (List catalog).
    - Implement `POST /rewards` (Admin create reward).
    - Implement `POST /users/{id}/goal` (Set current goal).
- [🚧] **Frontend: Reward Hub**
    - [x] Backend integration
    - [ ] Catalog Grid (Polish)
    - [x] Progress Bar for current goal.

## Phase 5: Admin Reporting & Frontend Polish
- [x] **API: Reporting (Story 4)**
    - [x] Transaction-based data structures implemented.
- [x] **Frontend: Admin Dashboard**
    - [x] User Management View.
    - [x] Task Management View.
    - [x] Role Management View.
- [🚧] **Frontend: User Dashboard**
    - [x] Daily Task List (Interactive).
    - [x] Current Point Balance.
    - [x] Goal Progress.
- [x] **Design Polish**
    - [x] Premium aesthetics (Glassmorphism, animations).

## Phase 6: Final Validation
- [x] **End-to-End Testing**
    - [x] BDD tests passing for all major stories.
    - [x] Family claim logic verified.
- [ ] **Deployment Prep**
    - [ ] Create `Dockerfile`.
    - [ ] Document running instructions.
