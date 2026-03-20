import os
import sys
import socket
import uvicorn

# Optional: auto-activate venv if exists
HERE = os.path.dirname(__file__)
VENV_PY = os.path.join(HERE, "venv", "Scripts", "python.exe")
if os.path.exists(VENV_PY):
    try:
        current = os.path.abspath(sys.executable)
        venv_py = os.path.abspath(VENV_PY)
        if os.path.normcase(current) != os.path.normcase(venv_py):
            os.execv(venv_py, [venv_py] + sys.argv)
    except Exception:
        pass

def find_free_port(start=8000, max_tries=50):
    """Find a free port, fallback if needed"""
    for p in range(start, start + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", p))  # bind to all interfaces
                return p
            except OSError:
                continue
    return None

if __name__ == "__main__":
    # Read HOST and PORT from environment
    host = os.getenv("HOST", "0.0.0.0")  # 0.0.0.0 allows LAN access
    port = int(os.getenv("PORT", 5000))

    # Reserve a free port (optional)
    free_port = find_free_port(port, 50)
    if free_port != port:
        print(f"Port {port} in use, starting on {free_port} instead")
        port = free_port

    print(f"Starting FastAPI on http://{host}:{port}")

    # Use import string for reload=True (hot reload)
    uvicorn.run("app.server:app", host=host, port=port, reload=True)
    