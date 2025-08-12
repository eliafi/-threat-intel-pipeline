#!/usr/bin/env python3
"""
Test script to run the dashboard locally before Docker
"""
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def install_requirements():
    """Install required packages"""
    import subprocess
    
    print("📦 Installing dashboard requirements...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "streamlit", "pandas", "plotly", "boto3", "botocore"
        ])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def run_dashboard():
    """Run the Streamlit dashboard"""
    import subprocess
    
    print("🚀 Starting Threat Intelligence Dashboard...")
    print("🌐 Dashboard will open at: http://localhost:8501")
    print("🔧 Use Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

def main():
    """Main function"""
    print("🛡️ Threat Intelligence Dashboard Setup")
    print("=" * 50)
    
    # Check if requirements are installed
    try:
        import streamlit
        import plotly
        import boto3
        print("✅ All requirements already installed!")
    except ImportError:
        if not install_requirements():
            print("❌ Failed to install requirements. Please install manually:")
            print("   pip install streamlit pandas plotly boto3")
            return
    
    # Run dashboard
    run_dashboard()

if __name__ == "__main__":
    main()
