#!/usr/bin/env python3
"""
Documentation build and serve script for Edgework.
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
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False


def build_docs():
    """Build the documentation."""
    return run_command("mkdocs build --clean", "Building documentation")


def serve_docs():
    """Serve the documentation locally."""
    print("🌐 Starting documentation server...")
    print("📖 Documentation will be available at: http://127.0.0.1:8000/edgework/")
    print("🛑 Press Ctrl+C to stop the server")
    try:
        subprocess.run("mkdocs serve", shell=True, check=True)
    except KeyboardInterrupt:
        print("\n👋 Documentation server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start documentation server: {e}")


def install_docs_deps():
    """Install documentation dependencies."""
    deps = [
        "mkdocs>=1.5.0",
        "mkdocs-material>=9.4.0",
        "mkdocstrings[python]>=0.24.0",
        "pymdown-extensions>=10.0.0"
    ]
    
    # Check if uv is available
    try:
        subprocess.run("uv --version", shell=True, check=True, capture_output=True)
        pip_cmd = "uv pip install"
        print("📦 Using uv for package installation")
    except subprocess.CalledProcessError:
        pip_cmd = "pip install"
        print("📦 Using pip for package installation")
    
    for dep in deps:
        if not run_command(f"{pip_cmd} {dep}", f"Installing {dep}"):
            return False
    return True


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("📚 Edgework Documentation Helper")
        print("\nUsage:")
        print("  python docs.py install    - Install documentation dependencies")
        print("  python docs.py build      - Build documentation")
        print("  python docs.py serve      - Serve documentation locally")
        print("  python docs.py deploy     - Build and serve documentation")
        return

    command = sys.argv[1].lower()
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    if command == "install":
        install_docs_deps()
    elif command == "build":
        build_docs()
    elif command == "serve":
        serve_docs()
    elif command == "deploy":
        if build_docs():
            serve_docs()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python docs.py' to see available commands.")


if __name__ == "__main__":
    main()
