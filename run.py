#!/usr/bin/env python3
"""
Personal Finance Tracker - Run Script
=====================================

Simple script to start the Personal Finance Tracker application.
This script will start the FastAPI server and open the application in your browser.

Usage:
    python run.py
    
Or make it executable and run directly:
    chmod +x run.py
    ./run.py
"""

import os
import sys
import subprocess
import webbrowser
import time
import socket
from pathlib import Path

def check_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def find_available_port(start_port=8000):
    """Find an available port starting from start_port"""
    port = start_port
    while port < start_port + 100:  # Try 100 ports
        if check_port_available(port):
            return port
        port += 1
    return None

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pandas
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\n📦 Please install dependencies first:")
        print("   pip install -r backend/requirements.txt")
        return False

def main():
    """Main function to run the application"""
    print("🚀 Starting Personal Finance Tracker...")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        print("   Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    # Change to backend directory for uvicorn to work properly
    os.chdir(backend_dir)
    print(f"📁 Working directory: {backend_dir}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Find available port
    port = find_available_port(8000)
    if port is None:
        print("❌ No available ports found (tried 8000-8099)")
        sys.exit(1)
    
    print(f"🌐 Starting server on port {port}...")
    
    # Prepare the command
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", str(port)
    ]
    
    try:
        # Start the server
        print("🔄 Launching FastAPI server...")
        print(f"   Command: {' '.join(cmd)}")
        print()
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)  # Wait for server to start
            url = f"http://localhost:{port}"
            print(f"🌍 Opening browser at: {url}")
            webbrowser.open(url)
        
        # Start browser opening in background
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the server (this will block)
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Thanks for using Personal Finance Tracker!")
    except FileNotFoundError:
        print("❌ uvicorn not found!")
        print("   Please install it with: pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()