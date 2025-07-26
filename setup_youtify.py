#!/usr/bin/env python3
"""
Youtify Setup Script
Helps users set up the application with proper credentials and configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🎵 YOUTIFY SETUP")
    print("YouTube to Spotify Playlist Converter")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_environment():
    """Set up environment configuration"""
    print("\n🔧 Setting up configuration...")
    
    secrets_dir = Path(".streamlit")
    secrets_example = secrets_dir / "secrets.example.toml"
    secrets_file = secrets_dir / "secrets.toml"
    
    # Create .streamlit directory if it doesn't exist
    secrets_dir.mkdir(exist_ok=True)
    
    if secrets_file.exists():
        print("⚠️  secrets.toml file already exists")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Keeping existing secrets.toml file")
            return True
    
    if not secrets_example.exists():
        print("❌ secrets.example.toml file not found")
        return False
    
    # Copy example to secrets.toml
    try:
        with open(secrets_example, 'r') as src, open(secrets_file, 'w') as dst:
            dst.write(src.read())
        print("✅ Created secrets.toml file from template")
        return True
    except Exception as e:
        print(f"❌ Failed to create secrets.toml file: {e}")
        return False

def get_credentials():
    """Guide user through credential setup"""
    print("\n🔑 API Credentials Setup")
    print("You need to get API credentials to use Youtify:")
    print()
    
    print("1. YouTube Data API v3 Key:")
    print("   - Go to: https://console.cloud.google.com/")
    print("   - Create/select a project")
    print("   - Enable YouTube Data API v3")
    print("   - Create credentials (API Key)")
    print()
    
    print("2. Spotify Web API Credentials:")
    print("   - Go to: https://developer.spotify.com/dashboard/")
    print("   - Create a new app")
    print("   - Add redirect URIs:")
    print("     - For local development: http://127.0.0.1:8501/")
    print("     - For production deployment: https://your-app.streamlit.app/")
    print("   - Copy Client ID and Client Secret")
    print()
    
    setup_now = input("Do you want to enter your credentials now? (y/N): ").lower()
    
    if setup_now == 'y':
        return configure_credentials()
    else:
        print("📝 You can add credentials later by editing the .streamlit/secrets.toml file")
        return True

def configure_credentials():
    """Configure API credentials interactively"""
    secrets_file = Path(".streamlit/secrets.toml")
    
    if not secrets_file.exists():
        print("❌ secrets.toml file not found. Run setup first.")
        return False
    
    print("\nEnter your API credentials:")
    
    # Get credentials from user
    youtube_key = input("YouTube API Key: ").strip()
    spotify_id = input("Spotify Client ID: ").strip()
    spotify_secret = input("Spotify Client Secret: ").strip()
    
    if not all([youtube_key, spotify_id, spotify_secret]):
        print("❌ All credentials are required")
        return False
    
    # Update secrets.toml file
    try:
        with open(secrets_file, 'r') as f:
            lines = f.readlines()
        
        # Replace placeholder values
        for i, line in enumerate(lines):
            if line.startswith('client_id ='):
                lines[i] = f'client_id = "{spotify_id}"\n'
            elif line.startswith('client_secret ='):
                lines[i] = f'client_secret = "{spotify_secret}"\n'
            elif line.startswith('api_key ='):
                lines[i] = f'api_key = "{youtube_key}"\n'
        
        with open(secrets_file, 'w') as f:
            f.writelines(lines)
        
        print("✅ Credentials saved to secrets.toml file")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save credentials: {e}")
        return False

def test_setup():
    """Test if setup is working"""
    print("\n🧪 Testing setup...")
    
    try:
        # Try importing main modules
        import streamlit
        import requests
        
        print("✅ All dependencies imported successfully")
        
        # Check if secrets.toml file exists and has credentials
        secrets_file = Path(".streamlit/secrets.toml")
        if secrets_file.exists():
            # Read the secrets file directly
            with open(secrets_file, 'r') as f:
                content = f.read()
            
            # Check for credentials
            if 'api_key = ' in content and 'client_id = ' in content and 'client_secret = ' in content:
                print("✅ API credentials configured")
            else:
                print("❌ API credentials not fully configured")
        else:
            print("⚠️  secrets.toml file not found")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🚀 Setup Complete!")
    print()
    print("Next steps:")
    print("1. Make sure your credentials are configured in .streamlit/secrets.toml")
    print("2. Run the application:")
    print("   streamlit run main.py")
    print()
    print("3. Open your browser to: http://localhost:8501")
    print()
    print("Need help? Check the README.md file or visit:")
    print("https://github.com/yourusername/youtify-poc")
    print()

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Setup environment
    if not setup_environment():
        return False
    
    # Get credentials
    if not get_credentials():
        return False
    
    # Test setup
    if not test_setup():
        print("⚠️  Setup completed with warnings")
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
