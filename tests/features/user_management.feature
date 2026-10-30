# Story 1: System Initialization (User & Role Setup)
# Since 2026-10-30 the family comes from the family hub: name, login and parent/child are managed there. Parents are
# Admin here; a parent picks a child's game role (and with it the points multiplier) here.

Feature: Game roles of the family
    As an Admin/Primary Planner
    I want to give each child a game role
    So that their points follow the right multiplier

    Background:
        Given the system is initialized with default roles
        And the following roles exist:
            | name        | multiplier_value |
            | Admin       | 1.0              |
            | Contributor | 1.0              |
            | Teenager    | 1.2              |
            | Child       | 1.5              |

    Scenario: A child starts with their role and its multiplier
        Given a family member "Alice" with role "Child"
        Then the user should have role "Child"
        And the user should have multiplier value 1.5

    Scenario: A parent gives a child another game role
        Given a family member "David" with role "Child"
        When a parent gives "David" the role "Teenager"
        Then the user should have role "Teenager"
        And the user should have multiplier value 1.2

    Scenario: The Admin role comes from the family hub
        Given a family member "Bob" with role "Child"
        When a parent gives "Bob" the role "Admin"
        Then the change should be refused with "admin_from_hub"
