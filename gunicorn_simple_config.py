# Gunicorn configuration file for simple WSGI script
import multiprocessing

# WSGI application module
wsgi_app = "simple_wsgi:application"

# Server socket - runs on port 8081 as required
bind = "127.0.0.1:8081"
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
proc_name = "simple_wsgi_gunicorn"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None
