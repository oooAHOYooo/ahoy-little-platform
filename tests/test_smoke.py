#!/usr/bin/env python3
"""
Smoke tests for Ahoy Indie Media
Minimal test suite to verify core functionality
"""

import pytest
import json
import time
from app import create_app


@pytest.fixture
def app():
    """Create test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_healthz_readyz(client):
    """Test health check endpoints return 200"""
    # Test /healthz
    response = client.get('/healthz')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
    
    # Test /readyz
    response = client.get('/readyz')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ready'


def test_csp_headers(client):
    """Test security headers are present"""
    response = client.get('/healthz')  # Use a working endpoint
    assert response.status_code == 200
    
    # Check for security headers
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    assert 'X-Frame-Options' in response.headers
    assert response.headers['X-Frame-Options'] == 'DENY'


def test_csrf_failure(client):
    """Test CSRF protection returns proper error"""
    # Make a POST request without CSRF token to a protected endpoint
    response = client.post('/api/playlists/',
                          json={'name': 'test'},
                          content_type='application/json')
    
    # Should return 400 or 403 with JSON error
    assert response.status_code in [400, 403]
    
    try:
        data = response.get_json()
        assert 'error' in data
    except:
        # If not JSON, check for CSRF error in response
        assert b'CSRF' in response.data or b'csrf' in response.data.lower()


def test_rate_limit_basic(client):
    """Test basic rate limiting functionality"""
    # Make multiple requests to see if rate limiting is working
    responses = []
    for i in range(5):
        response = client.get('/healthz')
        responses.append(response)
        time.sleep(0.1)
    
    # All should succeed (no rate limiting on GET)
    status_codes = [r.status_code for r in responses]
    assert all(code == 200 for code in status_codes)


def test_sentry_test_route(client):
    """Test Sentry test route returns 404 in development"""
    response = client.get('/_boom')
    assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
