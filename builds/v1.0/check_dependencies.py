#!/usr/bin/env python3
"""
Check and install required dependencies for Copycat Chess Engine.
"""

import sys
import os
import subprocess
import pkg_resources

def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 6)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: Python {current_version[0]}.{current_version[1]}.{current_version[2]}")
        return False
    
    print(f"Python version check passed: {current_version[0]}.{current_version[1]}.{current_version[2]}")
    return True

def get_requirements():
    """Get the list of required packages."""
    requirements = [
        "chess>=1.9.0",
        "numpy>=1.19.0",
        "pandas>=1.0.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "jupyter>=1.0.0",
        "notebook>=6.0.0",
        "pyinstaller>=5.0.0",  # For building the executable
    ]
    return requirements

def check_dependencies():
    """Check if all required dependencies are installed."""
    requirements = get_requirements()
    missing = []
    outdated = []
    
    for requirement in requirements:
        package = requirement.split('>=')[0]
        required_version = requirement.split('>=')[1] if '>=' in requirement else None
        
        try:
            installed = pkg_resources.get_distribution(package)
            print(f"✓ {package} {installed.version} is installed")
            
            # Check version if specified
            if required_version and pkg_resources.parse_version(installed.version) < pkg_resources.parse_version(required_version):
                outdated.append((package, installed.version, required_version))
        except pkg_resources.DistributionNotFound:
            print(f"✗ {package} is not installed")
            missing.append(package)
    
    return missing, outdated

def install_dependencies(missing, outdated):
    """Install missing or outdated dependencies."""
    if not missing and not outdated:
        print("\nAll dependencies are installed and up to date!")
        return True
    
    print("\nInstalling dependencies...")
    
    # Install missing packages
    if missing:
        print(f"\nInstalling missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        except subprocess.CalledProcessError:
            print("Error installing missing packages.")
            return False
    
    # Upgrade outdated packages
    if outdated:
        print(f"\nUpgrading outdated packages:")
        for package, installed_version, required_version in outdated:
            print(f"  {package}: {installed_version} -> {required_version}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}>={required_version}", "--upgrade"])
            except subprocess.CalledProcessError:
                print(f"Error upgrading {package}.")
                return False
    
    return True

def main():
    """Main function to check and install dependencies."""
    print("Checking dependencies for Copycat Chess Engine...\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    print("\nChecking required packages:")
    missing, outdated = check_dependencies()
    
    # Install or upgrade dependencies if needed
    if missing or outdated:
        print("\nSome dependencies are missing or outdated.")
        choice = input("Do you want to install/upgrade them now? [y/N]: ").strip().lower()
        
        if choice == 'y':
            if install_dependencies(missing, outdated):
                print("\nAll dependencies have been installed successfully!")
                return True
            else:
                print("\nFailed to install some dependencies.")
                return False
        else:
            print("\nDependency installation skipped.")
            return False
    
    return True

if __name__ == "__main__":
    success = main()
    
    print("\nDependency check completed.")
    
    if not success:
        print("There were issues with the dependencies. Please resolve them before continuing.")
        sys.exit(1)
    
    print("All dependencies are satisfied. You can now run the Copycat Chess Engine!")
