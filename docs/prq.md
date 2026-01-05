# Software Specification & Product Backlog: Family Chore Gamification System (ChoreSpec)

## 1. Executive Summary

The Family Chore Gamification System, or ChoreSpec, is a custom, locally-hosted web application designed to solve the core household pain point of lack of engagement in chores. It establishes a dynamic, role-based reward system (multipliers) and a tiered, goal-oriented Reward Hub. The application's unique value is transforming mandatory tasks into an engaging family game, resulting in consistently completed tasks and a reduced burden on primary caregivers.

## 2. Discovery & Problem Statement

### 2.1 The Problem

The single most painful problem is the Lack of Engagement and Motivation among family members (especially children) to consistently complete household chores, stemming from the absence of an immediate, satisfying feedback loop or a structured reward system.

### 2.2 User Personas

| Role | System Role | Core Goal/Need |
| :--- | :--- | :--- |
| Wife/Mother | Admin/Primary Planner | Define complex schedules, manage the reward economy, and track overall family fairness/performance. |
| Son (14 y.o.) | Engaged Teenager | Maximize point accumulation quickly via high role multipliers and save for high-value rewards. |
| Daughter (5 y.o.) | Motivated Child | Receive simple, immediate, and visible feedback for small, easy tasks to maintain interest. |

## 3. High-Level Requirements & Technical Blueprint

### 3.1 Core Feature List

*   **Dynamic Reward System**: Tasks have a Base Point Value multiplied by the User's Role Multiplier.
*   **Tiered/Goal-Oriented Reward Hub**: Users track points and set goals (Wishlist) for redemption.
*   **Configurable Daily View**: Users select their preferred motivational view (e.g., Max Value Task).
*   **Admin Reporting**: Oversight for task compliance and economic fairness.

### 3.2 Technical Blueprint (MVP Stack)

*   **Backend**: Python (preferred lightweight framework like Flask).
*   **Frontend**: TypeScript.
*   **Database**: SQLite (Chosen for lightweight, file-based, zero-admin use).
*   **Deployment**: Docker (Target environment: Synology NAS).
*   **Security**: Role-Based Access Control (RBAC) enforced by system roles.

## 4. Product Backlog: MVP & V1.1

### Section A: Minimum Viable Product (MVP) Backlog

The goal of the MVP is to establish the core loop: Setup → Assignment → Calculation → Goal Tracking → Admin Validation.

#### Story 1. System Initialization (User & Role Setup)

**As a** Admin/Primary Planner, **I want to** set up the initial user profiles and assign their system roles (Admin, Contributor, Teenager, Child), **so that** all family members can log in and the system can apply the correct permissions and reward logic immediately.

**Acceptance Criteria:**

| ID | Criterion | Logic (Simple Setup) |
| :--- | :--- | :--- |
| AC 1.1 | The Admin can access a "Manage Users" screen with a "Create New User" button. | Confirms the entry point. |
| AC 1.2 | Creating a new user requires inputting only two fields: User Nickname and a Unique Login PIN (4 digits). | Ensures a low-friction onboarding process. |
| AC 1.3 | The form requires selection of exactly one predefined System Role from a dropdown list. | Links the user to the core RBAC and Multiplier logic. |
| AC 1.4 | The newly created user can successfully log into the application using their Nickname and PIN. | Confirms basic authentication functionality. |
| AC 1.5 | Upon logging in, the new user's initial view correctly applies the permissions and visual priorities defined for their assigned Role. | Validates RBAC and custom UX configurations are loaded. |

#### Story 2. Role Multiplier Configuration

**As a** Admin/Primary Planner, **I want to** define the default point multiplier for each system role, **so that** the core dynamic rewarding logic is active, and effort is immediately equitably weighted by age/responsibility level.

**Acceptance Criteria:**

| ID | Criterion | Logic (Simple Grid) |
| :--- | :--- | :--- |
| AC 2.1 | The Admin can navigate to a dedicated "Role Multipliers" configuration screen. | Confirms entry point for configuring the core rewarding logic. |
| AC 2.2 | This screen displays the four System Roles in a table format, showing the Role Name and the editable Multiplier Value. | All roles visible for configuration in one place. |
| AC 2.3 | The Multiplier Value for any non-Admin role can be edited directly in the table using a numerical input field. | Allows rapid adjustment of the reward economy. |
| AC 2.4 | The system must prevent saving if any multiplier value is less than 0.1 or is not a valid number. | Enforces data integrity. |
| AC 2.5 | Once saved, the updated multiplier must immediately apply to all new task completions made by users assigned to that role. | Confirms direct link to the task completion flow. |

#### Story 3. Basic Task Creation (Minimum Viable Chore)

**As a** Admin/Primary Planner, **I want to** create a simple, fixed daily chore with a base point value, **so that** I can immediately populate the app with core content and allow the children to start earning points.

**Acceptance Criteria:**

| ID | Criterion | Logic (Minimum Viable Chore) |
| :--- | :--- | :--- |
| AC 3.1 | The Admin can navigate to a "Create New Task" form. | Confirms entry point for content creation. |
| AC 3.2 | The form must require input for Task Name, Base Point Value (integer $>0$), and Description. | Defines the minimum content for a task. |
| AC 3.3 | The form must allow selection of exactly one System Role for assignment. | Ensures a specific user sees the task in their "Assigned" list. |
| AC 3.4 | The schedule interface is simplified to only allow the Admin to set the task as "Daily" with a Fixed Completion Time (e.g., 5:00 PM). | Limits scheduling complexity to the simplest fixed requirement. |
| AC 3.5 | Once created, the task appears on the assigned user's Daily Task View and displays the correct Calculated Multiplier Reward next to the task name. | Validates visibility and core reward logic end-to-end. |

#### Story 4. Fairness & Compliance Report

**As a** Admin/Primary Planner, **I want to** view a weekly report combining task performance and reward distribution metrics for each role, **so that** I can validate the fairness of the rewards and identify which users are missing deadlines to ensure accountability.

**Acceptance Criteria:**

| ID | Criterion | Logic (Combined Report) |
| :--- | :--- | :--- |
| AC 4.1 | **Completion Rate**: The report must display the On-Time Completion Rate for each role (e.g., Teenager: 80%) as a primary metric. | Identifies specific roles/users failing to meet expectations. |
| AC 4.2 | **Overdue List**: The report must include a link or a section listing the top 3 most overdue tasks for the period, noting the assigned role. | Provides immediate, actionable information on system failures. |
| AC 4.3 | **Raw Effort**: The report must show the Total Base Points Earned by each role (the raw effort metric, independent of the multiplier). | Confirms the actual difficulty and effort level put in by the user. |
| AC 4.4 | **Reward Value**: The report must show the Total Multiplied Points Awarded to each role for the period. | Confirms the total incentive delivered. |
| AC 4.5 | **Comparison View**: The data should be presented in a side-by-side bar chart or grid to easily visually compare the four roles across all four metrics (AC 4.1, 4.3, 4.4). | Optimizes Admin analysis of fairness and balance. |

#### Story 5. Personal Goal Tracking (Wishlist)

**As a** Engaged Teenager, **I want to** select any reward from the catalog and add it to my personal Wishlist/Goal Tracker, **so that** I can always see the specific points remaining and stay motivated to keep earning towards that item.

**Acceptance Criteria:**

| ID | Criterion | Logic (Wishlist Tracking) |
| :--- | :--- | :--- |
| AC 5.1 | **Selection**: The user can click a visible icon (e.g., "Star") on any reward card to designate it as their primary Wishlist Goal. | Confirms the starting action for goal setting. |
| AC 5.2 | **Goal Display**: The selected reward appears in a dedicated "My Goal" section displaying Goal Cost, Points Earned, and Points Needed. | Ensures the three critical tracking metrics are clearly visible. |
| AC 5.3 | **Visualization**: A large, high-contrast visual progress bar must be displayed in the "My Goal" section, showing the user's progress percentage toward the goal. | Provides powerful, glanceable motivational feedback. |
| AC 5.4 | **Real-Time Update**: When a user completes a chore and receives points, the Points Needed metric and the progress bar must update instantly without a page refresh. | Validates real-time point-to-goal connectivity. |
| AC 5.5 | **Affordability Status**: Once the user's points meet or exceed the goal cost, the status text must visually change to "READY TO REDEEM!" | Confirms the final visual payoff moment. |

### Section B: V1.1 Enhancements Backlog

The goal of V1.1 is to add necessary complexity for operational realism and enhance the gamification experience.

#### Story 6. Flexible Scheduling

**As a** Admin/Planner, **I want to** create tasks with Flexible Time Windows (e.g., "Must be done within 3 days"), **so that** I can define tasks that don't need a hard daily deadline.

**Acceptance Criteria:**

| ID | Criterion | Logic |
| :--- | :--- | :--- |
| AC 6.1 | The Task Creation Form must include an option to select between "Fixed Schedule" (MVP) and "Flexible Window." | Expands the scope beyond MVP's fixed schedule. |
| AC 6.2 | When "Flexible Window" is selected, the Admin must input the Recurrence (e.g., weekly, monthly) and the Window Length (e.g., 3 days). | Defines the task's frequency and completion period. |
| AC 6.3 | The window begins immediately after the last completion (or on the assigned start date) and is displayed to the user as a clear countdown (e.g., "Due in 2 days, 15 hours"). | Ensures the user knows the time constraint without a hard clock time. |
| AC 6.4 | If the task is not completed before the Window Length expires, the task status is marked as "Overdue" and flagged in the Admin report. | Defines the failure state for flexible tasks. |

#### Story 7. Photo Verification (Accountability)

**As a** Admin/Planner, **I want to** toggle Photo Verification on for specific high-stakes tasks, **so that** I can confirm completion quality before points are officially awarded.

**Acceptance Criteria:**

| ID | Criterion | Logic |
| :--- | :--- | :--- |
| AC 7.1 | The Task Creation Form must include a toggle: "Requires Photo Verification." | Allows the Admin to specify which tasks need proof. |
| AC 7.2 | For a verified task, the user's Completion Flow is updated to include a mandatory step: "Upload Photo" before submission. | Modifies the basic MVP completion flow. |
| AC 7.3 | Tasks submitted with a photo are moved to an "Admin Review Queue." Points are reserved but not yet awarded to the user. | Introduces a pending state for points and creates the queue. |
| AC 7.4 | The Admin must be able to view the photo and select either "Approve & Award Points" or "Reject & Request Re-do." | Defines the Admin's final action and triggers point transaction. |
| AC 7.5 | The user receives a notification when their verified task is either approved or rejected (reason required). | Closes the loop on the accountability process. |

#### Story 8. Tiered Catalog Unlocks (Reward Enhancement)

**As a** Engaged Teenager, **I want to** higher reward Tiers (Silver, Gold) to visibly unlock only after I reach a certain Lifetime Point Milestone, **so that** I am motivated to continue saving for the long-term, exclusive rewards.

**Acceptance Criteria:**

| ID | Criterion | Logic |
| :--- | :--- | :--- |
| AC 8.1 | The Admin Configuration must include a screen to set the Lifetime Point Threshold required to unlock each Tier (e.g., Silver requires 500 Lifetime Points). | Creates the backend rule for tier progression. |
| AC 8.2 | Rewards assigned to Tiers above the user's current status are visible but prominently marked as "LOCKED" in the Reward Hub catalog. | Drives aspiration by showing unobtainable rewards. |
| AC 8.3 | The Reward Hub prominently features a Lifetime Points Progress Bar toward the next unlock threshold, along with the required Target Milestone. | Visualizes long-term effort and goal attainment. |
| AC 8.4 | When a user's Lifetime Point total surpasses a Tier Threshold, the system triggers a visual celebration/notification, and all rewards within that Tier become instantly unlocked and available for redemption. | Provides the major payoff moment for long-term engagement.