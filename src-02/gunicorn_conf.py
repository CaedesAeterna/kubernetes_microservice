# Basic prod-ish defaults; tune for your env
bind = "0.0.0.0:8000"
workers = 2 # or: multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "-" # stdout
errorlog = "-" # stderr
loglevel = "info"
keepalive = 5
timeout = 30