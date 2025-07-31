#!/usr/bin/env python3
"""
Setup script for AI Text Summarizer
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print application banner"""
    print("🤖 AI Text Summarizer Setup")
    print("=" * 40)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = "backend/.env"
    if os.path.exists(env_path):
        print("✅ .env file already exists")
        return True
    
    print("\n🔧 Creating .env file...")
    try:
        with open(env_path, "w") as f:
            f.write("# Hugging Face API Token\n")
            f.write("HUGGINGFACE_TOKEN=your_token_here\n")
            f.write("\n# Add your Hugging Face token above\n")
            f.write("# Get it from: https://huggingface.co/settings/tokens\n")
        print("✅ .env file created")
        print("   Please edit backend/.env and add your Hugging Face token")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_env_file():
    """Check if .env file has proper token"""
    env_path = "backend/.env"
    if not os.path.exists(env_path):
        return False
    
    try:
        with open(env_path, "r") as f:
            content = f.read()
            if "your_token_here" in content:
                return False
            return "HUGGINGFACE_TOKEN=" in content
    except:
        return False

def run_tests():
    """Run application tests"""
    print("\n🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "test_app.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Check if token is configured
    if not check_env_file():
        print("\n⚠️  IMPORTANT: Please configure your Hugging Face token")
        print("   1. Go to https://huggingface.co/settings/tokens")
        print("   2. Create a new token")
        print("   3. Edit backend/.env and replace 'your_token_here' with your token")
        print("   4. Restart the application")
    
    print("\n🎉 Setup completed!")
    print("\n🚀 To start the application:")
    print("   cd backend")
    print("   python main.py")
    print("\n🌐 Then open http://localhost:8000 in your browser")
    
    # Ask if user wants to run tests
    if check_env_file():
        response = input("\n🧪 Run tests now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            run_tests()

if __name__ == "__main__":
    main() 