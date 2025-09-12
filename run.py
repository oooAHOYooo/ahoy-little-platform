#!/usr/bin/env python3
"""
Ahoy Indie Media - Flask Application Runner
Production-ready script for Render.com deployment
"""

import os
import sys
import socket
from app import app

def find_available_port(start_port=5001, end_port=5010):
    """Find an available port between start_port and end_port"""
    for port in range(start_port, end_port + 1):
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            # Port is in use, try next one
            continue
    return None

if __name__ == '__main__':
    # Environment detection
    is_production = os.environ.get('RENDER') == 'true' or os.environ.get('FLASK_ENV') == 'production'
    
    if is_production:
        # Production settings for Render.com
        print("🚀 Starting Ahoy Indie Media in PRODUCTION mode...")
        
        # Get port from Render environment variable
        port = int(os.environ.get('PORT', 10000))
        host = '0.0.0.0'  # Required for Render.com
        
        print(f"📍 Server binding to: {host}:{port}")
        print("🌐 Production deployment ready")
        
        try:
            app.run(debug=False, host=host, port=port)
        except Exception as e:
            print(f"❌ Error starting production server: {e}")
            sys.exit(1)
    else:
        # Development settings
        print("🎵 Starting Ahoy Indie Media in DEVELOPMENT mode...")
        print("🔍 Checking for available ports...")
        
        # Set default environment variables
        os.environ.setdefault('FLASK_ENV', 'development')
        os.environ.setdefault('FLASK_DEBUG', 'True')
        os.environ.setdefault('SECRET_KEY', 'ahoy-indie-media-secret-2025')
        
        # Find available port
        port = find_available_port()
        if port is None:
            print("❌ No available ports found between 5001-5010")
            print("💡 Try closing other applications or use a different port range")
            sys.exit(1)
        
        print(f"📍 Server will be available at: http://localhost:{port}")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        try:
            app.run(debug=True, host='127.0.0.1', port=port)
        except KeyboardInterrupt:
            print("\n👋 Shutting down Ahoy Indie Media...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error starting development server: {e}")
            sys.exit(1)
