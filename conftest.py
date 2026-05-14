import os

# Set TESTING=True before any backend modules are imported so that
# the rate limiter (and other TESTING guards) are properly disabled.
os.environ.setdefault("TESTING", "True")
