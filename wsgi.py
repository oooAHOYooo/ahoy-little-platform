#!/usr/bin/env python3
"""
WSGI entry point for production deployment
This is the standard way to deploy Flask apps on production servers
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the Flask app
from app import app

# This is what Gunicorn will import
application = app

if __name__ == "__main__":
    # This allows running with: python wsgi.py
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
