#!/usr/bin/env python3
"""
Setup script for Falcon-H1-1B-Base model integration.
This script installs the required dependencies and sets up the environment.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing Dependencies")
    print("=" * 40)
    
    # Install PyTorch (CPU version for compatibility)
    if not run_command(
        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
        "Installing PyTorch (CPU version)"
    ):
        return False
    
    # Install transformers
    if not run_command(
        "pip install transformers>=4.35.0",
        "Installing Transformers"
    ):
        return False
    
    # Install accelerate
    if not run_command(
        "pip install accelerate>=0.24.0",
        "Installing Accelerate"
    ):
        return False
    
    # Install huggingface-hub
    if not run_command(
        "pip install huggingface-hub>=0.17.0",
        "Installing Hugging Face Hub"
    ):
        return False
    
    # Install other requirements
    if not run_command(
        "pip install -r requirements.txt",
        "Installing other requirements"
    ):
        return False
    
    return True

def setup_environment():
    """Set up environment variables."""
    print("\n🔧 Setting up Environment")
    print("=" * 30)
    
    # Create .env file if it doesn't exist
    env_file = ".env"
    if not os.path.exists(env_file):
        print("📝 Creating .env file...")
        env_content = """# K12 LMS Backend Environment Variables

# Security
SECRET_KEY=k12-lms-development-secret-key-2024
ALGORITHM=HS256

# Database
DATABASE_URL=sqlite:///./k12_lms.db

# AI/ML Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SHORT_ANSWER_PASS_THRESHOLD=0.7

# Hugging Face (set your token locally, do not commit)
# HUGGINGFACE_TOKEN=

# CORS
ALLOWED_ORIGIN=http://localhost:3000,http://localhost:3001

# API
API_VERSION=1.0.0
ENVIRONMENT=development
BUILD_TIME=unknown
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    return True

def test_installation():
    """Test the installation."""
    print("\n🧪 Testing Installation")
    print("=" * 25)
    
    # Test imports
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Transformers import failed: {e}")
        return False
    
    try:
        import accelerate
        print(f"✅ Accelerate {accelerate.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Accelerate import failed: {e}")
        return False
    
    try:
        import huggingface_hub
        print(f"✅ Hugging Face Hub {huggingface_hub.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Hugging Face Hub import failed: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Falcon-H1-1B-Base Setup Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n💥 Dependency installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n💥 Environment setup failed. Please check the errors above.")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n💥 Installation test failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Run the test script: python test_falcon_integration.py")
    print("2. Start the server: python -m uvicorn app.main:app --reload --port 8000")
    print("3. Test the API endpoints at: http://localhost:8000/docs")
    print("\n🔗 Falcon API Endpoints:")
    print("- POST /api/falcon/feedback - Generate enhanced feedback")
    print("- POST /api/falcon/learning-tips - Generate learning tips")
    print("- POST /api/falcon/analyze-misconceptions - Analyze misconception patterns")
    print("- GET /api/falcon/model-info - Get model information")
    print("- GET /api/falcon/health - Health check")

if __name__ == "__main__":
    main()

