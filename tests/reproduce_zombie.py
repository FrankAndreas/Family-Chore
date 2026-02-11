
import subprocess
import time
import os
import signal
import sys
import socket


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def reproduce_zombie():
    port = 8000
    if is_port_in_use(port):
        print(f"Port {port} is already in use. Please clear it first.")
        sys.exit(1)

    print("Starting uvicorn with --reload...")
    # Start uvicorn as a subprocess
    process = subprocess.Popen(
        ["venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid  # Create a new process group
    )

    print(f"Server started with PID: {process.pid}")
    time.sleep(5)  # Wait for it to start up

    if not is_port_in_use(port):
        print("Server failed to start or bind to port.")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        sys.exit(1)

    print("Sending SIGINT to simulate Ctrl+C...")
    os.killpg(os.getpgid(process.pid), signal.SIGINT)

    print("Waiting for shutdown...")
    time.sleep(5)  # Give it time to shut down

    if is_port_in_use(port):
        print(f"❌ FAILURE: Port {port} is still in use! Zombie process detected.")
        # Try to force kill to clean up
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        sys.exit(1)
    else:
        print(f"✅ SUCCESS: Port {port} is free. Clean shutdown confirmed.")
        sys.exit(0)


if __name__ == "__main__":
    reproduce_zombie()
