#!/usr/bin/env python3
"""
Render validation script for Ahoy Indie Media
Validates deployment health and functionality
"""

import os
import sys
import json
import requests
import time
from typing import Dict, Any


def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request and return standardized result"""
    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        return {
            "status": "pass" if response.status_code < 400 else "fail",
            "status_code": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "error": None
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "fail",
            "status_code": None,
            "response_time_ms": None,
            "error": str(e)
        }


def validate_health_endpoints(base_url: str) -> Dict[str, Any]:
    """Validate health check endpoints"""
    results = {}
    
    # Test /healthz
    healthz_result = make_request("GET", f"{base_url}/healthz")
    results["healthz"] = healthz_result
    
    # Test /readyz
    readyz_result = make_request("GET", f"{base_url}/readyz")
    results["readyz"] = readyz_result
    
    return results


def validate_sentry_test(base_url: str) -> Dict[str, Any]:
    """Validate Sentry test route (only if enabled)"""
    sentry_test_enabled = os.getenv("SENTRY_TEST_ROUTE") == "true"
    
    if not sentry_test_enabled:
        return {
            "status": "skip",
            "reason": "SENTRY_TEST_ROUTE not enabled"
        }
    
    # Test /_boom endpoint
    boom_result = make_request("GET", f"{base_url}/_boom")
    
    # Should return 500 (exception) or 404 (disabled)
    if boom_result["status_code"] in [500, 404]:
        boom_result["status"] = "pass"
    else:
        boom_result["status"] = "fail"
        boom_result["error"] = f"Expected 500 or 404, got {boom_result['status_code']}"
    
    return boom_result


def main():
    """Main validation function"""
    base_url = os.getenv("BASE_URL", "http://localhost:5000")
    
    print(f"Validating deployment at {base_url}")
    print("=" * 50)
    
    # Run validations
    health_results = validate_health_endpoints(base_url)
    sentry_result = validate_sentry_test(base_url)
    
    # Compile results
    all_results = {
        "timestamp": time.time(),
        "base_url": base_url,
        "checks": {
            "healthz": health_results["healthz"],
            "readyz": health_results["readyz"],
            "sentry_test": sentry_result
        }
    }
    
    # Print results
    print("\nValidation Results:")
    print("-" * 30)
    
    for check_name, result in all_results["checks"].items():
        status = result["status"]
        if status == "pass":
            print(f"✅ {check_name}: PASS")
        elif status == "fail":
            print(f"❌ {check_name}: FAIL")
            if result.get("error"):
                print(f"   Error: {result['error']}")
        elif status == "skip":
            print(f"⏭️  {check_name}: SKIP ({result.get('reason', 'No reason')})")
        
        if result.get("response_time_ms"):
            print(f"   Response time: {result['response_time_ms']:.1f}ms")
    
    # Determine overall status
    failed_checks = [name for name, result in all_results["checks"].items() 
                    if result["status"] == "fail"]
    
    if failed_checks:
        print(f"\n❌ Validation failed: {', '.join(failed_checks)}")
        sys.exit(1)
    else:
        print(f"\n✅ All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
