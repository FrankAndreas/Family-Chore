# Test & QA Standards Checklist

Evaluate the codebase against these core standards.

## 1. Test Coverage & Strategy
- **Critical Paths**: Are the most critical user flows and business logic paths adequately covered?
- **Edge Cases**: Are boundary conditions, null inputs, and expected failure states tested?
- **Pyramid Balance**: Is there a healthy balance of Unit, Integration, and E2E tests?

## 2. Mocking & Stubbing Strategy
- **Over-mocking**: Are tests mocking so much of the system that they no longer test real behavior? Are they tightly coupled to implementation details?
- **External Dependencies**: Are 3rd party APIs, databases, and network calls properly stubbed/mocked to ensure fast, deterministic tests?
- **Mock Cleanup**: Are mocks cleared/reset between tests to prevent state leakage?

## 3. Assertion Quality & Clarity
- **Meaningful Assertions**: Do the tests actually verify behavior (e.g. `expect(x).toEqual(y)`), or just that functions were called?
- **One Concept per Test**: Does each test verify a single logical concept or behavior?
- **Failure Readability**: If an assertion fails, will the error message clearly indicate *what* broke in business terms?

## 4. Test Reliability & Flakiness
- **Determinism**: Do tests rely on exact timestamps, random generation, or network speeds?
- **Wait States**: Do UI/E2E tests use intelligent polling/waiting instead of hardcoded `sleep()` timeouts?
- **Shared State**: Is shared database state or global variables causing test pollution?

## 5. Organization & Hygiene
- **Structure**: Are tests structured using Arrange-Act-Assert (Given-When-Then) patterns?
- **Setup/Teardown**: Is redundant setup code extracted into fixtures (`pytest`) or `beforeEach` blocks cleanly?
- **Naming Conventions**: Are test names descriptive of the behavior being tested?
