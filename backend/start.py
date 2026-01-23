#!/usr/bin/env python3
"""
Convenience script to start the MyHomeServer backend.
"""

import subprocess
import sys
import os

def main():
    """Start the FastAPI backend server"""
    print("Starting MyHomeServer Backend...")
    print("API will be available at: http://localhost:10500")
    print("API Documentation at: http://localhost:10500/docs")
    print("Health check at: http://localhost:10500/health")
    print()

    try:
        # Run the main FastAPI application
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "127.0.0.1",
            "--port", "10500",
            "--reload",
            "--log-level", "info"
        ], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\nMyHomeServer Backend stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()