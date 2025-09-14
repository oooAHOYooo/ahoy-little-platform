# Gunicorn Configuration for Production Deployment
# This file contains optimized settings for Render.com deployment

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
backlog = 2048

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Max 4 workers for free tier
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Preload app for better performance
preload_app = True

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "ahoy-indie-media"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in future)
# keyfile = None
# certfile = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
# worker_tmp_dir = "/dev/shm"  # Use memory for temporary files (Linux only)
# Use default temp directory for cross-platform compatibility

# Graceful shutdown
graceful_timeout = 30

# Print configuration on startup
def on_starting(server):
    server.log.info("🚀 Starting Ahoy Indie Media with Gunicorn")
    server.log.info(f"📍 Binding to: {server.address}")
    server.log.info(f"👥 Workers: {server.cfg.workers}")
    server.log.info(f"⏱️  Timeout: {server.cfg.timeout}s")
    server.log.info(f"🔄 Max requests per worker: {server.cfg.max_requests}")

def on_reload(server):
    server.log.info("🔄 Reloading Ahoy Indie Media...")

def worker_int(worker):
    worker.log.info("👷 Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info(f"👷 Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    server.log.info(f"✅ Worker spawned (pid: {worker.pid})")

def worker_abort(worker):
    worker.log.info("❌ Worker received SIGABRT signal")
