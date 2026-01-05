# Story 1: System Initialization (User & Role Setup)
# AC 1.1-1.5: User creation, role assignment, login, permissions

Feature: User Management and Authentication
    As an Admin/Primary Planner
    I want to set up user profiles and assign system roles
    So that all family members can log in with correct permissions

    Background:
        Given the system is initialized with default roles
        And the following roles exist:
            | name        | multiplier_value |
            | Admin       | 1.0              |
            | Contributor | 1.0              |
            | Teenager    | 1.2              |
            | Child       | 1.5              |

    Scenario: AC 1.2 - Create new user with nickname and PIN
        When I create a new user with:
            | nickname | login_pin | role_name |
            | TestUser | 5678      | Teenager  |
        Then the user should be created successfully
        And the user should have role "Teenager"

    Scenario: AC 1.3 - User must have exactly one role
        When I create a new user with:
            | nickname | login_pin | role_name |
            | Alice    | 1111      | Child     |
        Then the user should be assigned to role "Child"
        And the user should have multiplier value 1.5

    Scenario: AC 1.4 - User can login with nickname and PIN
        Given a user exists with:
            | nickname | login_pin | role_name |
            | Bob      | 2222      | Contributor |
        When I login with nickname "Bob" and PIN "2222"
        Then the login should be successful
        And I should receive user details

    Scenario: Login fails with incorrect PIN
        Given a user exists with:
            | nickname | login_pin | role_name |
            | Charlie  | 3333      | Admin     |
        When I login with nickname "Charlie" and PIN "9999"
        Then the login should fail with error "Incorrect PIN"

    Scenario: Login fails with non-existent user
        When I login with nickname "NonExistent" and PIN "0000"
        Then the login should fail with error "User not found"

    Scenario: AC 1.5 - User permissions apply after login
        Given a user exists with:
            | nickname | login_pin | role_name |
            | David    | 4444      | Teenager  |
        When I login with nickname "David" and PIN "4444"
        Then the user should have role "Teenager"
        And the user should have multiplier value 1.2
