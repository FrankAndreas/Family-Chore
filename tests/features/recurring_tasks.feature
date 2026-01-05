# Recurring Tasks with Cooldown Period
# Feature for tasks that appear daily until completed, then enter a cooldown period

Feature: Recurring Tasks with Cooldown
    As an Admin
    I want to create recurring tasks with min/max day intervals
    So that household chores reappear automatically after a cooldown period

    Background:
        Given the system is initialized with default roles
        And a user "Alice" exists with role "Child"

    Scenario: Create recurring task with cooldown period
        When I create a recurring task with:
            | name          | description    | base_points | role_name | min_days | max_days |
            | Vacuum Floor  | Clean carpets  | 20          | Child     | 3        | 5        |
        Then the task should be created successfully
        And the task should have recurrence_min_days of 3
        And the task should have recurrence_max_days of 5

    Scenario: Recurring task appears daily until completed
        Given a recurring task exists:
            | name          | description    | base_points | role_name | min_days | max_days |
            | Vacuum Floor  | Clean carpets  | 20          | Child     | 3        | 5        |
        When I trigger the daily reset
        Then "Alice" should have 1 task in their daily view
        When I trigger the daily reset again the next day
        Then "Alice" should have 1 task in their daily view
        And the task "Vacuum Floor" should still be PENDING

    Scenario: Recurring task enters cooldown after completion
        Given a recurring task exists:
            | name          | description    | base_points | role_name | min_days | max_days |
            | Vacuum Floor  | Clean carpets  | 20          | Child     | 3        | 5        |
        And the daily reset has been triggered
        And "Alice" has the task "Vacuum Floor" in their daily view
        When "Alice" completes the task "Vacuum Floor"
        Then the task instance should be marked as COMPLETED
        When I trigger the daily reset the next day
        Then "Alice" should have 0 tasks in their daily view

    Scenario: Recurring task reappears after minimum cooldown period
        Given a recurring task exists:
            | name          | description    | base_points | role_name | min_days | max_days |
            | Vacuum Floor  | Clean carpets  | 20          | Child     | 3        | 5        |
        And the daily reset has been triggered
        And "Alice" completed the task "Vacuum Floor"
        When I advance time by 2 days and trigger daily reset
        Then "Alice" should have 0 tasks in their daily view
        When I advance time by 1 more day and trigger daily reset
        Then "Alice" should have 1 task in their daily view
        And the task "Vacuum Floor" should be PENDING

    Scenario: Validation - min_days must be less than or equal to max_days
        When I create a recurring task with:
            | name          | description    | base_points | role_name | min_days | max_days |
            | Invalid Task  | Bad config     | 10          | Child     | 5        | 3        |
        Then the task creation should fail with validation error

    Scenario: Validation - recurring tasks require both min and max days
        When I create a recurring task missing max_days:
            | name          | description    | base_points | role_name | min_days |
            | Invalid Task  | Bad config     | 10          | Child     | 3        |
        Then the task creation should fail with validation error

    Scenario: Recurring task cooldown applies to all users
        Given a user "Bob" exists with role "Child"
        And a recurring task exists for all family members:
            | name          | description    | base_points | min_days | max_days |
            | Trash Day     | Take out trash | 15          | 3        | 5        |
        And the daily reset has been triggered
        When "Alice" completes the task "Trash Day"
        And I trigger the daily reset the next day
        Then "Alice" should have 0 tasks in their daily view
        And "Bob" should have 0 tasks in their daily view
