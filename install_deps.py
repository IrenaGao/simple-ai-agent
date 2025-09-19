#!/usr/bin/env python3
"""Installation script for Multi-Agent Telemetry Visualizer dependencies."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_python_deps():
    """Install Python dependencies."""
    # First, uninstall old pinecone-client if it exists
    print("🔄 Checking for old pinecone-client package...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "pinecone-client", "-y"], 
                   capture_output=True)
    
    # Install requirements
    return run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing Python dependencies")

def install_frontend_deps():
    """Install frontend dependencies."""
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found. Please install Node.js first.")
        return False
    
    return run_command("cd frontend && npm install", 
                      "Installing frontend dependencies")

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        print("🔄 Creating .env file from template...")
        try:
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file and add your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  No env.example file found, creating basic .env file...")
        try:
            with open(env_file, 'w') as f:
                f.write("# Multi-Agent Telemetry Visualizer Environment\n")
                f.write("# Add your API keys here\n\n")
                f.write("ANTHROPIC_API_KEY=your_anthropic_api_key_here\n")
                f.write("PINECONE_API_KEY=your_pinecone_api_key_here\n")
                f.write("PINECONE_INDEX_NAME=developer-quickstart-py\n")
                f.write("PINECONE_NAMESPACE=kb-namespace\n")
                f.write("USE_LLM_DIAGRAMMER=false\n")
            print("✅ Basic .env file created")
            print("⚠️  Please edit .env file and add your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False

def test_installation():
    """Test that the installation works."""
    print("🔄 Testing installation...")
    try:
        result = subprocess.run([sys.executable, "test_basic.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Installation test passed")
            return True
        else:
            print("❌ Installation test failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Installation test timed out")
        return False
    except Exception as e:
        print(f"❌ Installation test error: {e}")
        return False

def main():
    """Main installation function."""
    print("🎯 Multi-Agent Telemetry Visualizer - Dependency Installer")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_deps():
        print("❌ Python dependency installation failed")
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_deps():
        print("❌ Frontend dependency installation failed")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: python3 start_server.py")
    print("3. Open http://localhost:3000 in your browser")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
