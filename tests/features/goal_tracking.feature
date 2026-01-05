# Story 5: Personal Goal Tracking (Wishlist)
# AC 5.1-5.5: Set goals, track progress, visual feedback

Feature: Personal Goal Tracking
    As an Engaged Teenager
    I want to select rewards and track my progress toward them
    So that I stay motivated to keep earning points

    Background:
        Given the system is initialized with default roles
        And a user "Teen" exists with role "Teenager" and 0 points
        And a reward exists:
            | name      | cost_points | description        |
            | Ice Cream | 50          | Favorite dessert   |

    Scenario: AC 5.1 - Set a reward as personal goal
        When "Teen" sets "Ice Cream" as their goal
        Then "Teen" should have "Ice Cream" as their current goal

    Scenario: AC 5.2 - Goal displays cost, earned, and needed points
        Given "Teen" has 20 current points
        And "Teen" has set "Ice Cream" (50 points) as their goal
        Then the goal should show:
            | cost | earned | needed |
            | 50   | 20     | 30     |

    Scenario: AC 5.3 - Progress bar shows percentage toward goal
        Given "Teen" has 25 current points
        And "Teen" has set "Ice Cream" (50 points) as their goal
        Then the progress should be 50 percent

    Scenario: AC 5.4 - Points update in real-time after task completion
        Given "Teen" has 10 current points
        And "Teen" has set "Ice Cream" (50 points) as their goal
        And a task "Homework" with 20 base points assigned to "Teenager"
        And the "Teenager" role has multiplier 1.5
        When I trigger the daily reset
        And "Teen" completes their task
        Then "Teen" should have 40 current points
        And the goal should show 10 points needed

    Scenario: AC 5.5 - Status changes to "READY TO REDEEM" when goal reached
        Given "Teen" has 45 current points
        And "Teen" has set "Ice Cream" (50 points) as their goal
        And a task "Chores" with 10 base points assigned to "Teenager"
        And the "Teenager" role has multiplier 1.0
        When I trigger the daily reset
        And "Teen" completes their task
        Then "Teen" should have 55 current points
        And the goal status should be "READY TO REDEEM"

    Scenario: Progress calculation with zero points
        Given "Teen" has 0 current points
        And "Teen" has set "Ice Cream" (50 points) as their goal
        Then the progress should be 0 percent
        And the goal should show 50 points needed

    Scenario: Progress calculation when exceeding goal
        Given "Teen" has 75 current points
        And "Teen" has set "Ice Cream" (50 points) as their goal
        Then the progress should be 100 percent
        And the goal status should be "READY TO REDEEM"
