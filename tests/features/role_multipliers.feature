# Story 2: Role Multiplier Configuration
# AC 2.1-2.5: Configure and update role multipliers

Feature: Role Multiplier Configuration
    As an Admin/Primary Planner
    I want to define the default point multiplier for each system role
    So that effort is equitably weighted by age/responsibility level

    Background:
        Given the system is initialized with default roles

    Scenario: AC 2.1 & 2.2 - View all role multipliers
        When I request the list of roles
        Then I should see 4 roles
        And each role should have a name and multiplier value

    Scenario: AC 2.3 - Update role multiplier
        When I update the "Teenager" role multiplier to 1.5
        Then the role should be updated successfully
        And the "Teenager" role should have multiplier value 1.5

    Scenario: AC 2.4 - Prevent invalid multiplier (too low)
        When I update the "Child" role multiplier to 0.05
        Then the update should fail with error "Multiplier must be >= 0.1"

    Scenario: AC 2.4 - Prevent invalid multiplier (negative)
        When I update the "Contributor" role multiplier to -1.0
        Then the update should fail with error "Multiplier must be >= 0.1"

    Scenario: AC 2.5 - Multiplier applies to new task completions
        Given a user "Emma" with role "Teenager" and multiplier 1.2
        And a task "Clean Room" with 10 base points assigned to "Teenager"
        When I update the "Teenager" role multiplier to 1.5
        And I create a daily task instance for "Emma"
        And "Emma" completes the task
        Then "Emma" should receive 20 points
        And the transaction should show multiplier 1.5
