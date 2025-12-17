# Gunicorn configuration file for static WSGI script (for performance testing)
import multiprocessing

# WSGI application module
wsgi_app = "test_static:application"

# Server socket - different port for static testing
bind = "127.0.0.1:8001"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "static_wsgi_gunicorn"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None
