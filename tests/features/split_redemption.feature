Feature: Split Redemption
    As a family member
    I want to split the cost of a reward with other family members
    So that we can pool our points for shared experiences

    Scenario: Users can split the cost of a reward evenly
        Given a reward "Pizza Party" costs 100 points
        And user "Alice" has 60 points
        And user "Bob" has 50 points
        When they redeem "Pizza Party" splitting 50 points each
        Then the redemption should be successful
        And "Alice" should have 10 points remaining
        And "Bob" should have 0 points remaining

    Scenario: Redemption fails if total contribution is insufficient
        Given a reward "Movie Night" costs 80 points
        And user "Alice" has 30 points
        And user "Bob" has 30 points
        When they attempt to redeem "Movie Night" contributing 30 points each
        Then the redemption should fail with error "Total contribution (60) does not equal reward cost (80)"

    Scenario: Redemption fails if a user does not have enough points
        Given a reward "Gifts" costs 50 points
        And user "Charlie" has 10 points
        And user "Dave" has 100 points
        When they attempt to redeem "Gifts" with "Charlie" contributing 25 points and "Dave" contributing 25 points
        Then the redemption should fail with error containing "Charlie has only 10 pts"
