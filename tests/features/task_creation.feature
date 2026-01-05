# Story 3: Basic Task Creation
# AC 3.1-3.5: Create tasks and verify they appear in user's daily view

Feature: Task Creation and Assignment
    As an Admin/Primary Planner
    I want to create simple, fixed daily chores with base point values
    So that I can populate the app and allow children to start earning points

    Background:
        Given the system is initialized with default roles
        And a user "TestChild" exists with role "Child"

    Scenario: AC 3.1 & 3.2 - Create task with required fields
        When I create a task with:
            | name        | description      | base_points | role_name | schedule_type | due_time |
            | Wash Dishes | Clean all dishes | 10          | Child     | daily         | 17:00    |
        Then the task should be created successfully
        And the task should have name "Wash Dishes"
        And the task should have base points 10

    Scenario: AC 3.3 - Task must be assigned to a role
        When I create a task with:
            | name       | description    | base_points | role_name | schedule_type | due_time |
            | Make Bed   | Tidy bedroom   | 5           | Teenager  | daily         | 09:00    |
        Then the task should be assigned to role "Teenager"

    Scenario: AC 3.4 - Task has daily schedule with fixed time
        When I create a task with:
            | name          | description | base_points | role_name | schedule_type | due_time |
            | Feed the Cat  | Give food   | 8           | Child     | daily         | 18:30    |
        Then the task should have schedule type "daily"
        And the task should have due time "18:30"

    Scenario: AC 3.5 - Task appears in assigned user's daily view with calculated reward
        Given a task exists:
            | name         | description  | base_points | role_name | schedule_type | due_time |
            | Water Plants | Water garden | 12          | Child     | daily         | 16:00    |
        And the "Child" role has multiplier value 1.5
        When I trigger the daily reset
        Then "TestChild" should have 1 task in their daily view
        And the task should show calculated points of 18

    Scenario: Validation - Task name cannot be empty
        When I create a task with:
            | name | description | base_points | role_name | schedule_type | due_time |
            |      | Test        | 10          | Child     | daily         | 17:00    |
        Then the task creation should fail with validation error

    Scenario: Validation - Base points must be positive
        When I create a task with:
            | name      | description | base_points | role_name | schedule_type | due_time |
            | Bad Task  | Test        | 0           | Child     | daily         | 17:00    |
        Then the task creation should fail with validation error

    Scenario: Validation - Time must be in HH:MM format
        When I create a task with:
            | name      | description | base_points | role_name | schedule_type | due_time |
            | Bad Time  | Test        | 10          | Child     | daily         | 25:00    |
        Then the task creation should fail with validation error

    Scenario: Unassigned task is available to all family members
        Given a user "Alice" exists with role "Teenager"
        And a user "Bob" exists with role "Admin"
        And a task exists without role assignment:
            | name           | description          | base_points | schedule_type | due_time |
            | Take Out Trash | Family shared chore  | 10          | daily         | 20:00    |
        When I trigger the daily reset
        Then "TestChild" should have 1 task in their daily view
        And "Alice" should have 1 task in their daily view
        And "Bob" should have 1 task in their daily view
        And all users should see task "Take Out Trash"
