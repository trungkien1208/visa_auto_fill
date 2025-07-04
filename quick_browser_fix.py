#!/usr/bin/env python3
"""
Quick Browser Fix Script
This script provides an immediate solution for the browser installation issue.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def main():
    """Main fix function."""
    print("🔧 Quick Browser Fix for Visa Autofill")
    print("=" * 50)
    print("This script will help fix the browser installation issue.")
    print()
    
    system = platform.system().lower()
    
    # Step 1: Clear any problematic environment variables
    print("1️⃣ Clearing problematic environment variables...")
    vars_to_clear = [
        "PLAYWRIGHT_BROWSERS_PATH",
        "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"
    ]
    
    cleared = []
    for var in vars_to_clear:
        if var in os.environ:
            del os.environ[var]
            cleared.append(var)
    
    if cleared:
        print(f"   ✅ Cleared: {', '.join(cleared)}")
    else:
        print("   ℹ️  No problematic variables found")
    
    # Step 2: Check for system browsers
    print("\n2️⃣ Checking for system browsers...")
    
    if system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ]
    elif system == "windows":
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome"
        ]
    
    found_browsers = []
    for path in chrome_paths:
        if Path(path).exists():
            found_browsers.append(path)
            print(f"   ✅ Found: {path}")
    
    if not found_browsers:
        print("   ❌ No system browsers found")
        print("\n🔧 SOLUTION: Install Google Chrome")
        print("   1. Visit https://www.google.com/chrome/")
        print("   2. Download and install Google Chrome")
        print("   3. Restart the Visa Autofill application")
        return
    
    # Step 3: Try to install Playwright browsers
    print("\n3️⃣ Attempting to install Playwright browsers...")
    
    python_executables = [sys.executable, "python3", "python"]
    
    for python_exe in python_executables:
        try:
            # Test if this Python has playwright
            test_result = subprocess.run(
                [python_exe, "-c", "import playwright.sync_api"],
                capture_output=True,
                timeout=10
            )
            
            if test_result.returncode != 0:
                continue
            
            print(f"   🔍 Trying with: {python_exe}")
            
            # Install browsers
            result = subprocess.run(
                [python_exe, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("   ✅ Playwright browsers installed successfully!")
                print("\n🎉 Fix completed! Try running the Visa Autofill application again.")
                return
            else:
                print(f"   ❌ Installation failed: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Failed with {python_exe}: {e}")
            continue
    
    # Step 4: Provide manual solutions
    print("\n4️⃣ Manual solutions:")
    print("=" * 30)
    
    if system == "darwin":  # macOS
        print("🔧 EASIEST SOLUTION:")
        print("   1. Install Google Chrome from https://www.google.com/chrome/")
        print("   2. Restart the Visa Autofill application")
        print()
        print("🔧 ALTERNATIVE SOLUTION:")
        print("   1. Open Terminal")
        print("   2. Run: brew install --cask chromium")
        print("   3. Restart the Visa Autofill application")
        print()
        print("🔧 ADVANCED SOLUTION:")
        print("   1. Open Terminal")
        print("   2. Run: pip3 install playwright")
        print("   3. Run: playwright install chromium")
        print("   4. Restart the Visa Autofill application")
    
    elif system == "windows":
        print("🔧 EASIEST SOLUTION:")
        print("   1. Install Google Chrome from https://www.google.com/chrome/")
        print("   2. Restart the Visa Autofill application")
        print()
        print("🔧 ALTERNATIVE SOLUTION:")
        print("   1. Open Command Prompt as Administrator")
        print("   2. Run: pip install playwright")
        print("   3. Run: playwright install chromium")
        print("   4. Restart the Visa Autofill application")
    
    else:  # Linux
        print("🔧 EASIEST SOLUTION:")
        print("   1. Run: sudo apt-get install chromium-browser")
        print("   2. Restart the Visa Autofill application")
        print()
        print("🔧 ALTERNATIVE SOLUTION:")
        print("   1. Install Google Chrome from https://www.google.com/chrome/")
        print("   2. Restart the Visa Autofill application")
    
    print("\n📞 Need more help?")
    print("   Contact support with this error message and your system information.")

if __name__ == "__main__":
    main() 