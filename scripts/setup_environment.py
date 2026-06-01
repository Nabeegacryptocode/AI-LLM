"""
Environment setup script
Installs all required dependencies and verifies the setup
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("  Fahm Faris - Environment Setup")
    print("="*60)
    
    # Get backend directory
    backend_dir = Path(__file__).parent.parent / "backend"
    
    # Check if we're in the right directory
    if not backend_dir.exists():
        print(f"✗ Error: Backend directory not found at {backend_dir}")
        sys.exit(1)
    
    print(f"\nBackend directory: {backend_dir}")
    print(f"Python version: {sys.version}")
    
    # Install main dependencies
    success = run_command(
        f"pip install -r {backend_dir / 'requirements.txt'}",
        "Installing main dependencies"
    )
    
    if not success:
        print("\n✗ Failed to install main dependencies")
        print("Please check the error messages above and try again")
        sys.exit(1)
    
    # Install test dependencies
    test_req = backend_dir / "requirements-test.txt"
    if test_req.exists():
        success = run_command(
            f"pip install -r {test_req}",
            "Installing test dependencies"
        )
        
        if not success:
            print("\n⚠ Warning: Failed to install test dependencies")
            print("Tests may not work properly")
    
    # Verify installation
    print("\n" + "="*60)
    print("  Verifying Installation")
    print("="*60)
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "openai",
        "pinecone",
        "pydantic",
        "python-dotenv"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} NOT installed")
            all_installed = False
    
    # Check for .env file
    print("\n" + "="*60)
    print("  Configuration Check")
    print("="*60)
    
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if env_file.exists():
        print(f"✓ .env file found")
    else:
        print(f"⚠ .env file not found")
        if env_example.exists():
            print(f"  Copy {env_example} to {env_file} and configure it")
        else:
            print(f"  Create .env file with required environment variables")
    
    # Final summary
    print("\n" + "="*60)
    print("  Setup Summary")
    print("="*60)
    
    if all_installed:
        print("\n✓ All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Configure your .env file with API keys")
        print("2. Run: python scripts/setup_pinecone.py")
        print("3. Start the server: uvicorn app.main:app --reload")
    else:
        print("\n✗ Some dependencies failed to install")
        print("Please review the errors above and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
