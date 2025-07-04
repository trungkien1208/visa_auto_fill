#!/usr/bin/env python3
"""
Debug script to test browser installation issues.
Run this on the target Mac to diagnose what's going wrong.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_system_info():
    """Print system information."""
    print("🖥️  System Information:")
    print(f"   Platform: {platform.platform()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print(f"   PyInstaller frozen: {getattr(sys, 'frozen', False)}")
    if hasattr(sys, '_MEIPASS'):
        print(f"   Bundle temp path: {sys._MEIPASS}")
    print()

def check_python_packages():
    """Check if required packages are available."""
    print("📦 Checking Python packages:")
    
    packages = ['playwright', 'PyQt5', 'pandas']
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}: Available")
        except ImportError as e:
            print(f"   ❌ {package}: Missing - {e}")
    print()

def test_playwright_import():
    """Test Playwright import and basic functionality."""
    print("🎭 Testing Playwright:")
    
    try:
        from playwright.sync_api import sync_playwright
        print("   ✅ Playwright import: Success")
        
        with sync_playwright() as p:
            try:
                browser_path = p.chromium.executable_path
                print(f"   ✅ Browser path: {browser_path}")
                
                if os.path.exists(browser_path):
                    print("   ✅ Browser executable: Found")
                else:
                    print("   ❌ Browser executable: Not found")
                    
            except Exception as e:
                print(f"   ❌ Browser check failed: {e}")
                
    except Exception as e:
        print(f"   ❌ Playwright import failed: {e}")
    print()

def check_browser_installation_paths():
    """Check browser installation paths."""
    print("📂 Checking browser paths:")
    
    system = platform.system().lower()
    if system == "darwin":
        browser_cache = Path.home() / "Library" / "Caches" / "ms-playwright"
    elif system == "windows":
        browser_cache = Path.home() / "AppData" / "Local" / "ms-playwright"
    else:
        browser_cache = Path.home() / ".cache" / "ms-playwright"
    
    print(f"   Expected browser cache: {browser_cache}")
    print(f"   Cache exists: {browser_cache.exists()}")
    
    if browser_cache.exists():
        chromium_dirs = list(browser_cache.glob("chromium-*"))
        print(f"   Chromium directories: {len(chromium_dirs)}")
        for dir in chromium_dirs:
            print(f"     - {dir.name}")
    print()

def test_browser_install():
    """Test browser installation."""
    print("🌐 Testing browser installation:")
    
    try:
        print("   Running: python3 -m playwright install chromium")
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("   ✅ Browser installation: Success")
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}...")
        else:
            print("   ❌ Browser installation: Failed")
            print(f"   Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   ❌ Browser installation: Timed out")
    except Exception as e:
        print(f"   ❌ Browser installation: Exception - {e}")
    print()

def test_gui_creation():
    """Test GUI creation."""
    print("🖼️  Testing GUI:")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            
        print("   ✅ QApplication: Created")
        
        # Test message box
        msg = QMessageBox()
        msg.setText("Test message")
        print("   ✅ QMessageBox: Created")
        
    except Exception as e:
        print(f"   ❌ GUI test failed: {e}")
    print()

def main():
    """Main diagnostic function."""
    print("🔍 Visa GUI Application - Browser Debug Tool")
    print("=" * 60)
    print()
    
    print_system_info()
    check_python_packages()
    test_playwright_import()
    check_browser_installation_paths()
    
    # Ask user if they want to test installation
    try:
        response = input("🤔 Do you want to test browser installation? (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            test_browser_install()
    except KeyboardInterrupt:
        print("\n   Skipped browser installation test")
        print()
    
    test_gui_creation()
    
    print("🏁 Diagnostic completed!")
    print()
    print("📋 Next steps:")
    print("1. Share this output with the app developer")
    print("2. If browser installation failed, try manual installation:")
    print("   pip3 install playwright")
    print("   playwright install chromium")
    print("3. If GUI failed, check PyQt5 installation:")
    print("   pip3 install PyQt5")

if __name__ == "__main__":
    main() 