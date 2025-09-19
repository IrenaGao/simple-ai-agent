#!/usr/bin/env python3
"""Startup script for the Multi-Agent Telemetry Visualizer."""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✓ Python dependencies found")
    except ImportError as e:
        print(f"✗ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if frontend dependencies are installed
    frontend_path = Path("frontend")
    if frontend_path.exists():
        node_modules = frontend_path / "node_modules"
        if not node_modules.exists():
            print("✗ Frontend dependencies not found")
            print("Please run: cd frontend && npm install")
            return False
        print("✓ Frontend dependencies found")
    
    return True

def check_env_file():
    """Check if environment file exists."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found")
        print("Please copy env.example to .env and add your API keys")
        return False
    print("✓ Environment file found")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FastAPI backend server...")
    try:
        # Set environment variables
        os.environ.setdefault("USE_LLM_DIAGRAMMER", "false")
        
        # Start the server
        subprocess.run([
            sys.executable, "api_server.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start backend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
        return True

def start_frontend():
    """Start the React frontend development server."""
    print("🚀 Starting React frontend server...")
    try:
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            print("✗ Frontend directory not found")
            return False
        
        # Change to frontend directory and start dev server
        subprocess.run([
            "npm", "run", "dev"
        ], cwd=frontend_path, check=True)
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start frontend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
        return True

def main():
    """Main startup function."""
    print("🎯 Multi-Agent Telemetry Visualizer")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    env_ok = check_env_file()
    if not env_ok:
        print("\n⚠️  Continuing without .env file (some features may not work)")
    
    print("\nChoose startup mode:")
    print("1. Backend only (FastAPI server)")
    print("2. Frontend only (React dev server)")
    print("3. Both (requires two terminals)")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        start_backend()
    elif choice == "2":
        start_frontend()
    elif choice == "3":
        print("\n🔄 Starting both servers...")
        print("Backend will start in this terminal.")
        print("Please open another terminal and run:")
        print("  cd frontend && npm run dev")
        print("\nPress Ctrl+C to stop the backend server.")
        start_backend()
    elif choice == "4":
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()
