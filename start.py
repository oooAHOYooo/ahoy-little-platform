#!/usr/bin/env python3
"""
Simple startup script for Render.com
This ensures the app always binds to 0.0.0.0
"""

import os
from app import app

if __name__ == '__main__':
    # Get port from environment (Render always sets this)
    port = int(os.environ.get('PORT', 10000))
    
    # Always bind to 0.0.0.0 for Render
    host = '0.0.0.0'
    
    print(f"🚀 Starting Ahoy Indie Media on {host}:{port}")
    print(f"🌐 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    # Run the app
    app.run(host=host, port=port, debug=False)
