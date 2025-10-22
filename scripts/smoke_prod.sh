#!/usr/bin/env bash
"""
Production smoke test script for Ahoy Indie Media
Tests critical endpoints to verify service health
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${BASE_URL:-https://ahoy-indie-media.onrender.com}"
TIMEOUT=30

echo -e "${GREEN}Starting production smoke test...${NC}"
echo -e "${GREEN}Target: ${BASE_URL}${NC}"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Helper function to run test
run_test() {
    local test_name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    echo -n "Testing ${test_name}... "
    
    if response=$(curl -s -w "%{http_code}" -o /dev/null --max-time $TIMEOUT "$url" 2>/dev/null); then
        if [[ "$response" == "$expected_status" ]]; then
            echo -e "${GREEN}PASS${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}FAIL (got $response, expected $expected_status)${NC}"
            ((TESTS_FAILED++))
            FAILED_TESTS+=("$test_name")
        fi
    else
        echo -e "${RED}FAIL (timeout/error)${NC}"
        ((TESTS_FAILED++))
        FAILED_TESTS+=("$test_name")
    fi
}

# Run smoke tests
echo -e "\n${YELLOW}Running smoke tests...${NC}"

run_test "Health Check" "${BASE_URL}/healthz" "200"
run_test "Readiness Check" "${BASE_URL}/readyz" "200"
run_test "Home Page" "${BASE_URL}/" "200"
run_test "Music Page" "${BASE_URL}/music" "200"
run_test "Shows Page" "${BASE_URL}/shows" "200"
run_test "Artists Page" "${BASE_URL}/artists" "200"

# Test API endpoints
run_test "API Health" "${BASE_URL}/api/health" "200" 2>/dev/null || run_test "API Health" "${BASE_URL}/healthz" "200"

# Test error handling
run_test "404 Page" "${BASE_URL}/nonexistent-page" "404"

echo -e "\n${YELLOW}Test Summary:${NC}"
echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"

if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
    echo -e "\n${RED}Failed tests:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "  - ${RED}${test}${NC}"
    done
fi

# Generate JSON report
cat << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "base_url": "$BASE_URL",
  "tests_passed": $TESTS_PASSED,
  "tests_failed": $TESTS_FAILED,
  "total_tests": $((TESTS_PASSED + TESTS_FAILED)),
  "status": "$([ $TESTS_FAILED -eq 0 ] && echo "PASS" || echo "FAIL")",
  "failed_tests": [$(printf '"%s",' "${FAILED_TESTS[@]}" | sed 's/,$//')]
}
EOF

# Exit with appropriate code
if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed!${NC}"
    exit 1
fi
