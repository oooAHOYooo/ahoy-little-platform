#!/usr/bin/env python3
"""
Production startup script for Render.com
Uses optimized Gunicorn configuration for production deployment
"""

import os
import subprocess
import sys

def main():
    """Main startup function with comprehensive error handling"""
    
    # Get environment variables
    port = int(os.environ.get('PORT', 10000))
    flask_env = os.environ.get('FLASK_ENV', 'production')
    render = os.environ.get('RENDER', 'false').lower() == 'true'
    
    print("🚀 Starting Ahoy Indie Media in PRODUCTION mode...")
    print(f"📍 Port: {port}")
    print(f"🌐 Environment: {flask_env}")
    print(f"☁️  Render: {render}")
    print(f"🐍 Python: {sys.version}")
    
    # Check if Gunicorn is available
    try:
        import gunicorn
        print(f"✅ Gunicorn version: {gunicorn.__version__}")
    except ImportError:
        print("❌ Gunicorn not installed!")
        print("Installing Gunicorn...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn==21.2.0'], check=True)
    
    # Use Gunicorn with configuration file
    gunicorn_config = 'gunicorn.conf.py'
    
    if os.path.exists(gunicorn_config):
        print(f"📋 Using Gunicorn config: {gunicorn_config}")
        cmd = ['gunicorn', '-c', gunicorn_config, 'app:app']
    else:
        print("⚠️  Gunicorn config not found, using command line options")
        cmd = [
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
            '--log-level', 'info',
            'app:app'
        ]
    
    print(f"🔧 Command: {' '.join(cmd)}")
    
    try:
        # Start Gunicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Gunicorn failed with exit code: {e.returncode}")
        print("🔄 Attempting fallback to Flask development server...")
        
        # Fallback to Flask development server
        try:
            from app import app
            print("⚠️  Using Flask development server (NOT recommended for production)")
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as flask_error:
            print(f"❌ Flask fallback also failed: {flask_error}")
            sys.exit(1)
    except FileNotFoundError:
        print("❌ Gunicorn command not found!")
        print("🔄 Attempting fallback to Flask development server...")
        
        # Fallback to Flask development server
        try:
            from app import app
            print("⚠️  Using Flask development server (NOT recommended for production)")
            app.run(host='0.0.0.0', port=port, debug=False)
        except Exception as flask_error:
            print(f"❌ Flask fallback also failed: {flask_error}")
            sys.exit(1)

if __name__ == '__main__':
    main()
