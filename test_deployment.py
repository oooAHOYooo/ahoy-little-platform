#!/usr/bin/env python3
"""
Test script to verify deployment configuration
"""

import os
import sys
import requests
import time

def test_local_development():
    """Test local development mode"""
    print("🧪 Testing local development mode...")
    
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['RENDER'] = 'false'
    
    try:
        from app import app
        print("✅ App imports successfully")
        
        # Test basic functionality
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Home page loads successfully")
            
            response = client.get('/debug')
            assert response.status_code == 200
            print("✅ Debug page loads successfully")
            
            response = client.get('/api/music')
            assert response.status_code == 200
            print("✅ API endpoints work")
        
        print("✅ Local development mode test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Local development test failed: {e}")
        return False

def test_production_config():
    """Test production configuration"""
    print("\n🧪 Testing production configuration...")
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    os.environ['RENDER'] = 'true'
    os.environ['PORT'] = '10000'
    
    try:
        from app import app
        print("✅ App imports successfully in production mode")
        
        # Test that app is configured for production
        assert not app.debug, "App should not be in debug mode in production"
        print("✅ Debug mode disabled in production")
        
        print("✅ Production configuration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Production configuration test failed: {e}")
        return False

def test_dependencies():
    """Test that all dependencies are available"""
    print("\n🧪 Testing dependencies...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
        
        import flask_compress
        print(f"✅ Flask-Compress {flask_compress.__version__}")
        
        import jinja2
        print(f"✅ Jinja2 {jinja2.__version__}")
        
        print("✅ All dependencies available!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Ahoy Indie Media - Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_local_development,
        test_production_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment!")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
