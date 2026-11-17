"""
Gunicorn configuration for production (started by systemd, see deploy/systemd/sensorhub.service).

    gunicorn -c gunicorn_conf.py app:app
"""
# nginx talks to the application through a unix socket: no TCP port is exposed
bind = "unix:/run/sensorhub/sensorhub.sock"

# ONE worker on purpose: the EventBus lives in memory and the MQTT bridge must be a single client.
# With more workers every process would open its own MQTT connection with the same client id
# and an SSE client would only see the events of its own worker.
workers = 1
worker_class = "uvicorn_worker.UvicornWorker"

# Trust X-Forwarded-For / X-Forwarded-Proto: only nginx can open the socket (group www-data, umask 007)
forwarded_allow_ips = "*"

# SSE connections stay open: give them a few seconds to close on restart
graceful_timeout = 10

# Logs go to stdout/stderr and are collected by journald
accesslog = "-"
errorlog = "-"
loglevel = "info"
