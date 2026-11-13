import sys
import subprocess
import time
import os

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=== STARTING T20 PRESSURE INTELLIGENCE LAB SERVERS ===")
print(f"Workspace: {WORKSPACE}")

# 1. Start FastAPI Backend on port 8000
backend_cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"]
print(f"Launching Backend: {' '.join(backend_cmd)}")
backend_proc = subprocess.Popen(backend_cmd, cwd=WORKSPACE)

# 2. Start Next.js Frontend on port 3000
next_bin = os.path.join(WORKSPACE, "frontend", "node_modules", "next", "dist", "bin", "next")
frontend_cmd = ["node", next_bin, "start", "frontend", "-p", "3000"]
print(f"Launching Frontend: {' '.join(frontend_cmd)}")
frontend_proc = subprocess.Popen(frontend_cmd, cwd=WORKSPACE)

print("\n-----------------------------------------------------------")
print("T20 PRESSURE INTELLIGENCE LAB IS RUNNING LOCALLY:")
print("  - Frontend Dashboard: http://localhost:3000")
print("  - Backend FastAPI:    http://127.0.0.1:8000/docs")
print("-----------------------------------------------------------\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down servers...")
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Shutdown complete.")
