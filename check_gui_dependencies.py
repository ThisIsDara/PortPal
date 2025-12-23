#!/usr/bin/env python3
"""
Test script to verify PortPal GUI dependencies are installed correctly
Run this before building the binary to ensure everything works
"""

import sys

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} - OK")
    return True


def check_imports():
    """Check if all required modules can be imported"""
    modules = {
        'PySimpleGUI': 'GUI Framework',
        'http.server': 'HTTP Server (built-in)',
        'socketserver': 'Socket Server (built-in)',
        'json': 'JSON (built-in)',
        'socket': 'Socket (built-in)',
        'threading': 'Threading (built-in)',
        'shutil': 'Shell Utilities (built-in)',
    }
    
    print("\nChecking dependencies:")
    all_ok = True
    
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"  ✅ {module:20} - {description}")
        except ImportError:
            print(f"  ❌ {module:20} - {description} [MISSING]")
            all_ok = False
    
    return all_ok


def check_pyinstaller():
    """Check if PyInstaller is available for building"""
    print("\nChecking build tools:")
    try:
        import pyinstaller
        print("  ✅ PyInstaller - Available (for building binary)")
    except ImportError:
        print("  ⚠️  PyInstaller - Not installed (optional, needed for binary build)")
        print("     Run: pip install pyinstaller")


def main():
    print("=" * 50)
    print("  PortPal GUI - Dependency Checker")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check imports
    if not check_imports():
        print("\n❌ Some dependencies are missing!")
        print("\nFix by running:")
        print("  pip install -r requirements-gui.txt")
        sys.exit(1)
    
    # Check PyInstaller
    check_pyinstaller()
    
    print("\n" + "=" * 50)
    print("  ✅ All checks passed!")
    print("=" * 50)
    print("\nYou can now:")
    print("  1. Run the GUI: python gui_server.py")
    print("  2. Build binary: pyinstaller --onefile --windowed gui_server.py")
    print("  3. Use builder: build_gui.bat (Windows)")
    print()


if __name__ == '__main__':
    main()
