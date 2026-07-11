# --- Use standard Gunicorn workers, not gevent ---
# Render's free tier has very low memory limits (512MB).
# Eventlet/Gevent workers consume significant memory during startup.
# We will use the default sync worker which is memory-efficient.
web: gunicorn -w 1 -t 60 -k gevent "app:create_app()"
