#!/usr/bin/env python3
"""
Production startup script for Render.com
Uses Gunicorn WSGI server for proper production deployment
"""

import os
import subprocess
import sys

if __name__ == '__main__':
    # Get port from environment (Render always sets this)
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🚀 Starting Ahoy Indie Media in PRODUCTION mode...")
    print(f"📍 Port: {port}")
    print(f"🌐 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    # Use Gunicorn for production deployment
    # This is what Render expects for Python web services
    try:
        subprocess.run([
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--preload',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'app:app'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn failed: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("⚠️  Gunicorn not found, falling back to Flask development server")
        print("⚠️  This is not recommended for production!")
        
        # Fallback to Flask development server
        from app import app
        app.run(host='0.0.0.0', port=port, debug=False)
