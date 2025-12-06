#!/usr/bin/env python3
"""
Installation script for MediAlert Pro v2.0
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("Installing MediAlert Pro v2.0 dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_fixed.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration"""
    env_example = "../config/.env.example"
    env_file = "../config/.env"
    
    if not os.path.exists(env_file) and os.path.exists(env_example):
        print("Setting up environment configuration...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"Created {env_file} from template")
        print("Please update the API keys in the .env file")
    
    return True

def main():
    """Main installation process"""
    print("MediAlert Pro v2.0 Installation")
    print("=" * 40)
    
    if install_dependencies():
        setup_environment()
        print("\nInstallation completed!")
        print("Next steps:")
        print("1. Update API keys in config/.env")
        print("2. Run: python run.py")
    else:
        print("Installation failed!")
        return False
    
    return True

if __name__ == "__main__":
    main()