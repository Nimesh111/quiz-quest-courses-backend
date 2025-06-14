#!/usr/bin/env python3
"""
Startup script for Quiz Quest Backend API Server
This script initializes the database with sample data and starts the FastAPI server
"""

import os
import sys
import subprocess
import importlib.util
import time

def check_virtual_env():
    """Check if we're running in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def kill_port_8000():
    """Kill any process using port 8000"""
    try:
        print("🔧 Checking for processes on port 8000...")
        # Try to find processes using port 8000
        result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"📍 Found {len(pids)} process(es) using port 8000")
            
            # Kill the processes
            for pid in pids:
                if pid:
                    try:
                        subprocess.run(['kill', '-9', pid], check=True)
                        print(f"✅ Killed process {pid}")
                    except subprocess.CalledProcessError:
                        print(f"⚠️  Could not kill process {pid}")
            
            # Wait a moment for processes to cleanup
            time.sleep(1)
            print("✅ Port 8000 is now available")
        else:
            print("✅ Port 8000 is already available")
            
    except FileNotFoundError:
        # lsof command not available (might be on Windows or different system)
        print("⚠️  lsof command not available, skipping port check")
        # Try alternative method for different systems
        try:
            # For Windows or systems without lsof
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
            else:
                # Alternative Unix method
                subprocess.run(['pkill', '-f', 'uvicorn.*8000'], capture_output=True)
            print("✅ Attempted to clear port using alternative method")
        except:
            print("⚠️  Could not clear port, continuing anyway...")
    except Exception as e:
        print(f"⚠️  Error clearing port 8000: {e}")
        print("Continuing anyway...")

def install_dependencies():
    """Install dependencies if they're missing"""
    required_packages = ['fastapi', 'uvicorn', 'pydantic']
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("📦 Installing missing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully!")

def seed_database():
    """Initialize the database with sample data"""
    try:
        print("🌱 Seeding database with sample data...")
        from seed_data import main as seed_main
        seed_main()
        print("✅ Database seeded successfully!")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False
    return True

def start_server():
    """Start the FastAPI server"""
    try:
        print("🚀 Starting Quiz Quest Backend Server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔧 Alternative API docs: http://localhost:8000/redoc")
        print("\n💡 To stop the server, press Ctrl+C")
        print("-" * 50)
        
        # Start the server
        os.system("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    return True

def main():
    """Main function to orchestrate the startup process"""
    print("🎯 Quiz Quest Backend - Starting up...")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if not check_virtual_env():
        print("⚠️  Warning: Not running in a virtual environment!")
        print("💡 It's recommended to activate your virtual environment first:")
        print("   source venv/bin/activate  # On Unix/macOS")
        print("   venv\\Scripts\\activate     # On Windows")
        print()
    
    # Kill any existing processes on port 8000
    kill_port_8000()
    
    # Install dependencies if needed
    try:
        install_dependencies()
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return 1
    
    # Seed the database
    if not seed_database():
        print("⚠️  Warning: Database seeding failed, but continuing...")
    
    # Start the server
    if not start_server():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 