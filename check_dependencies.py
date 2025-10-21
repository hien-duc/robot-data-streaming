#!/usr/bin/env python3
"""
Dependency Check Script

This script verifies that all required dependencies for the robot data streaming system are installed.
"""

import sys
import importlib

def check_python_version():
    """Check if Python 3.6 or higher is installed"""
    print("Checking Python version...")
    if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
        print(f"✓ Python {sys.version}")
        return True
    else:
        print(f"✗ Python {sys.version} - Please upgrade to Python 3.6 or higher")
        return False

def check_package(package_name, min_version=None):
    """Check if a package is installed"""
    print(f"Checking {package_name}...")
    try:
        package = importlib.import_module(package_name)
        if hasattr(package, '__version__'):
            version = package.__version__
            print(f"✓ {package_name} {version} installed")
        else:
            print(f"✓ {package_name} installed")
        return True
    except ImportError:
        print(f"✗ {package_name} not found - Please install with 'pip install {package_name}'")
        return False

def check_mosquitto_cli():
    """Check if Mosquitto CLI tools are available"""
    print("Checking Mosquitto CLI tools...")
    import subprocess
    try:
        result = subprocess.run(['mosquitto_pub', '--help'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 1:  # mosquitto_pub returns 1 for help
            print("✓ Mosquitto CLI tools installed")
            return True
        else:
            print("✗ Mosquitto CLI tools not found - Please install Mosquitto")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Mosquitto CLI tools not found - Please install Mosquitto")
        return False

def main():
    print("Checking dependencies for VDA5050 Robot Data Streaming System...\n")
    
    # Check Python version
    python_ok = check_python_version()
    print()
    
    # Check required Python packages
    packages = ['paho.mqtt', 'json', 'time', 'threading']
    packages_ok = []
    
    for package in packages:
        packages_ok.append(check_package(package))
    print()
    
    # Check Mosquitto CLI tools
    mosquitto_ok = check_mosquitto_cli()
    print()
    
    # Summary
    all_checks = [python_ok, mosquitto_ok] + packages_ok
    if all(all_checks):
        print("✓ All dependencies are installed correctly!")
        print("You're ready to run the robot data streaming system.")
        return 0
    else:
        print("✗ Some dependencies are missing.")
        print("Please install the missing dependencies and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())