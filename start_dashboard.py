#!/usr/bin/env python3
"""
Simple dashboard runner using existing Airflow environment
"""
import subprocess
import sys
import os

def run_dashboard_in_airflow():
    """Run dashboard using Airflow worker container"""
    print("🚀 Starting Threat Intelligence Dashboard via Airflow Container")
    print("=" * 60)
    
    # First, install streamlit in the airflow worker
    print("📦 Installing Streamlit in Airflow container...")
    
    install_cmd = [
        "docker-compose", "exec", "airflow-worker", 
        "pip", "install", "streamlit", "plotly"
    ]
    
    try:
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Streamlit installed successfully!")
        else:
            print(f"⚠️ Install output: {result.stdout}")
            print(f"⚠️ Install errors: {result.stderr}")
    except Exception as e:
        print(f"❌ Error installing Streamlit: {e}")
        return False
    
    # Copy dashboard files to airflow container
    print("📂 Copying dashboard files...")
    
    copy_commands = [
        ["docker", "cp", "dashboard/app.py", "threatintelpipeline-airflow-worker-1:/opt/airflow/"],
    ]
    
    for cmd in copy_commands:
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Copy command failed: {e}")
    
    print("✅ Files copied successfully!")
    
    # Run streamlit
    print("🌐 Starting dashboard on http://localhost:8501")
    print("🔧 Use Ctrl+C to stop")
    print("-" * 60)
    
    run_cmd = [
        "docker-compose", "exec", "-p", "8501:8501", "airflow-worker",
        "streamlit", "run", "/opt/airflow/app.py", 
        "--server.port=8501", "--server.address=0.0.0.0"
    ]
    
    try:
        subprocess.run(run_cmd)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

def main():
    """Main function"""
    print("🛡️ Threat Intelligence Dashboard - Quick Start")
    print("=" * 60)
    
    # Check if docker-compose is available
    try:
        subprocess.run(["docker-compose", "--version"], 
                      capture_output=True, check=True)
        print("✅ Docker Compose is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose not found. Please ensure Docker is installed.")
        return
    
    # Check if Airflow is running
    try:
        result = subprocess.run(["docker-compose", "ps", "airflow-worker"], 
                               capture_output=True, text=True)
        if "Up" in result.stdout:
            print("✅ Airflow worker is running")
            run_dashboard_in_airflow()
        else:
            print("❌ Airflow worker is not running")
            print("💡 Please start Airflow first: docker-compose up -d")
    except Exception as e:
        print(f"❌ Error checking Airflow status: {e}")

if __name__ == "__main__":
    main()
