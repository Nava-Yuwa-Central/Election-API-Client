#!/usr/bin/env python3
"""
Simple local setup script for Nepal Entity Service
Uses SQLite for local development without Docker
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def setup_local_environment():
    """Setup local development environment"""
    print("🇳🇵 Nepal Entity Service - Local Setup")
    print("=" * 50)
    
    # Check Python
    print("🐍 Checking Python...")
    try:
        import sys
        print(f"✅ Python {sys.version} found")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Create virtual environment
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Activate and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate && "
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate && "
    
    if not run_command(f"{activate_cmd}pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Setup SQLite database
    print("🗄️ Setting up SQLite database...")
    db_path = "nepal_entity_local.db"
    if os.path.exists(db_path):
        print("✅ Database file already exists")
    else:
        # Create empty database file
        conn = sqlite3.connect(db_path)
        conn.close()
        print("✅ Created SQLite database file")
    
    # Run migrations
    if not run_command(f"{activate_cmd}alembic upgrade head", "Running database migrations"):
        return False
    
    # Load sample data
    print("📊 Loading sample data...")
    if not run_command(f"{activate_cmd}python scripts/seed_sample_data.py", "Loading sample data"):
        print("⚠️ Sample data loading failed, but continuing...")
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n🚀 To start the server, run:")
    print("   run_server.bat  (Windows)")
    print("   or manually:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8195")
    
    print("\n🌐 Then access:")
    print("   Main App: http://localhost:8195")
    print("   API Docs: http://localhost:8195/docs")
    print("   Leaders: http://localhost:8195/leaders.html")
    print("   Parties: http://localhost:8195/parties.html")
    
    return True

if __name__ == "__main__":
    success = setup_local_environment()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    
    # Ask if user wants to start the server
    try:
        start_server = input("\n🚀 Start the server now? (y/n): ").lower().strip()
        if start_server in ['y', 'yes']:
            print("\n🌟 Starting server...")
            if os.name == 'nt':
                os.system("venv\\Scripts\\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8195")
            else:
                os.system("source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8195")
    except KeyboardInterrupt:
        print("\n👋 Setup complete. Run the server when ready!")