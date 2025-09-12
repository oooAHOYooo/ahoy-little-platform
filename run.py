#!/usr/bin/env python3
"""
Ahoy Indie Media - Flask Application Runner
Simple script to start the Flask development server
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
    # Set default environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', 'True')
    os.environ.setdefault('SECRET_KEY', 'ahoy-indie-media-secret-2025')
    
    print("🎵 Starting Ahoy Indie Media...")
    print("🔍 Checking for available ports...")
    
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
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
