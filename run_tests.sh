#!/bin/bash
# ChoreSpec Test Runner Script

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Set PYTHONPATH
export PYTHONPATH=/home/andreas/work/family-chore

echo -e "${BLUE}ChoreSpec Test Runner${NC}"
echo "====================="
echo ""

# Parse command line arguments
TEST_TYPE=${1:-all}

case $TEST_TYPE in
  all)
    echo -e "${GREEN}Running all tests...${NC}"
    ./venv/bin/pytest tests/ -v --cov=backend --cov-report=term-missing --cov-report=html
    ;;
  
  bdd)
    echo -e "${GREEN}Running BDD tests only...${NC}"
    ./venv/bin/pytest tests/step_defs/ -v
    ;;
  
  unit)
    echo -e "${GREEN}Running unit tests only...${NC}"
    ./venv/bin/pytest tests/unit/ -v
    ;;
  
  user)
    echo -e "${GREEN}Running User Management tests...${NC}"
    ./venv/bin/pytest tests/step_defs/test_user_management.py -v
    ;;
  
  task)
    echo -e "${GREEN}Running Task Creation tests...${NC}"
    ./venv/bin/pytest tests/step_defs/test_task_creation.py -v
    ;;
  
  coverage)
    echo -e "${GREEN}Running tests with detailed coverage...${NC}"
    ./venv/bin/pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing
    echo ""
    echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
    ;;
  
  quick)
    echo -e "${GREEN}Running quick test (no coverage)...${NC}"
    ./venv/bin/pytest tests/ -v --tb=line
    ;;
  
  watch)
    echo -e "${GREEN}Running tests in watch mode...${NC}"
    ./venv/bin/pytest-watch tests/ -v
    ;;
  
  *)
    echo -e "${YELLOW}Usage: $0 [all|bdd|unit|user|task|coverage|quick]${NC}"
    echo ""
    echo "Options:"
    echo "  all       - Run all tests with coverage (default)"
    echo "  bdd       - Run only BDD tests"
    echo "  unit      - Run only unit tests"
    echo "  user      - Run User Management BDD tests"
    echo "  task      - Run Task Creation BDD tests"
    echo "  coverage  - Run all tests with detailed coverage report"
    echo "  quick     - Run all tests without coverage (faster)"
    exit 1
    ;;
esac

echo ""
echo -e "${GREEN}✓ Tests complete!${NC}"
