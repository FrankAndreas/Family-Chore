# MVP Data Model Specification (SQLite Blueprint)

This document defines the core tables required to satisfy all MVP User Stories (1-5) and establish the relationships that power the dynamic reward and reporting systems.

**Technology Foundation (Recommended for implementation):**

*   **Backend**: FastAPI (Python)
*   **Frontend**: React (TypeScript)
*   **Database**: SQLite via SQLAlchemy ORM

## 1. Core Tables

### 1.1 Roles (Role Multiplier Configuration - AC 2.x)

Defines the base system roles and their multiplier values.

| Field Name | Data Type | Constraint/Reference | Rationale (AC Ref) |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY | Unique Role Identifier |
| name | TEXT | UNIQUE, NOT NULL | e.g., 'Admin', 'Teenager', 'Child' (AC 1.3) |
| multiplier_value | REAL | NOT NULL, >= 0.1 | Defines the economic weighting factor (AC 2.4) |

### 1.2 Users (System Initialization & Goal Tracking - AC 1.x, 5.x)

Defines individual user accounts and stores their cumulative point status.

| Field Name | Data Type | Constraint/Reference | Rationale (AC Ref) |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY | Unique User Identifier |
| role_id | INTEGER | FOREIGN KEY (Roles.id), NOT NULL | Links user to their permissions/multiplier (AC 1.3) |
| nickname | TEXT | UNIQUE, NOT NULL | User-friendly login name (AC 1.2) |
| login_pin | TEXT | NOT NULL | 4-digit PIN for authentication (AC 1.2) |
| current_points | INTEGER | NOT NULL, DEFAULT 0 | Points available for immediate redemption |
| lifetime_points | INTEGER | NOT NULL, DEFAULT 0 | Total points ever earned (For V1.1 Tier unlocks) |
| current_goal_reward_id | INTEGER | FOREIGN KEY (Rewards.id), NULLABLE | Stores the user's selected Wishlist Goal (AC 5.1) |

### 1.3 Tasks (Basic Task Creation - AC 3.x)

Defines the chore templates, independent of who is doing them or when.

| Field Name | Data Type | Constraint/Reference | Rationale (AC Ref) |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY | Unique Task Identifier |
| name | TEXT | NOT NULL | Name of the chore (AC 3.2) |
| description | TEXT | NOT NULL | Details of the chore (AC 3.2) |
| base_points | INTEGER | NOT NULL, > 0 | Raw points earned before multiplier (AC 3.2) |
| assigned_role_id | INTEGER | FOREIGN KEY (Roles.id), NULLABLE | Defines the target role (AC 3.3) |
| schedule_type | TEXT | NOT NULL, DEFAULT 'daily' | Defines recurrence (AC 3.4) |
| default_due_time | TEXT | NOT NULL | Default time of day for deadline (e.g., "17:00") (AC 3.4) |

### 1.4 Task_Instances (Task Execution & Reporting - AC 4.x)

Tracks every single time a chore is assigned and completed (or missed). This is critical for reporting.

| Field Name | Data Type | Constraint/Reference | Rationale (AC Ref) |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY | Unique instance ID |
| task_id | INTEGER | FOREIGN KEY (Tasks.id), NOT NULL | Links to the chore definition |
| user_id | INTEGER | FOREIGN KEY (Users.id), NOT NULL | The user assigned to this specific instance |
| due_time | TEXT (ISO 8601) | NOT NULL | Fixed Completion Time (AC 3.4) |
| completed_at | TEXT (ISO 8601) | NULLABLE | Timestamp of completion |
| status | TEXT | NOT NULL, e.g., 'PENDING', 'COMPLETED', 'OVERDUE' | Tracks compliance (AC 4.1, 4.2) |

### 1.5 Rewards (Reward Hub Catalog - AC 5.x)

Defines the items available for redemption.

| Field Name | Data Type | Constraint/Reference | Rationale (AC Ref) |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY | Unique Reward Identifier |
| name | TEXT | NOT NULL | Name of the reward |
| cost_points | INTEGER | NOT NULL, > 0 | Total points required for redemption (AC 5.2) |
| description | TEXT | | Details of the reward |
| tier_level | INTEGER | DEFAULT 0 | Tier level (0=Base, 1=Silver, etc. - V1.1 AC 8.1) |

## 2. Audit & Reporting Table

### 2.1 Transactions (Fairness Report - AC 4.x)

An immutable ledger for every point earned or spent. Essential for validating rewards and calculating reports.

| Field Name | Data Type | Constraint/Reference | Rationale (AC Ref) |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY | Transaction ID |
| user_id | INTEGER | FOREIGN KEY (Users.id), NOT NULL | The user involved |
| type | TEXT | NOT NULL, 'EARN' or 'REDEEM' | Transaction type |
| base_points_value | INTEGER | NOT NULL | Base points earned/spent (AC 4.3) |
| multiplier_used | REAL | NOT NULL | Multiplier at time of transaction (AC 4.4 calculation) |
| awarded_points | INTEGER | NOT NULL | Final points after multiplier (AC 4.4) |
| reference_instance_id | INTEGER | FOREIGN KEY (Task_Instances.id), NULLABLE | Links EARN to the completed task |
| timestamp | TEXT (ISO 8601) | NOT NULL | When the transaction occurred |

This data model covers all necessary fields to implement and test the entire MVP scope. You can now use this schema to start building your database migrations or ORM models in Python.