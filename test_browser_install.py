#!/usr/bin/env python3
"""
Test script to verify browser installation and diagnose issues.
Run this script to check if Chromium/Chrome is properly installed and accessible.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def test_browser_installation():
    """Test if browsers are properly installed and accessible."""
    print("🔍 Testing browser installation...")
    print(f"System: {platform.system()}")
    print(f"Architecture: {platform.machine()}")
    print()
    
    # Test 1: Check if Playwright can find browsers
    print("📋 Test 1: Playwright browser detection")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser_path = p.chromium.executable_path
            if os.path.exists(browser_path):
                print(f"✅ Playwright found Chromium at: {browser_path}")
            else:
                print(f"❌ Playwright reports Chromium at: {browser_path} (but file doesn't exist)")
                print("   This is the issue you're experiencing!")
    except Exception as e:
        print(f"❌ Playwright browser detection failed: {e}")
    print()
    
    # Test 2: Check system browsers
    print("📋 Test 2: System browser detection")
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            Path.home() / "Applications" / "Google Chrome.app" / "Contents" / "MacOS" / "Google Chrome",
            Path.home() / "Applications" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
        ]
    elif system == "windows":  # Windows
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe"
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/snap/bin/chromium"
        ]
    
    found_browsers = []
    for path in chrome_paths:
        if Path(path).exists():
            print(f"✅ Found system browser: {path}")
            found_browsers.append(str(path))
        else:
            print(f"❌ Not found: {path}")
    
    if not found_browsers:
        print("⚠️  No system browsers found")
    print()
    
    # Test 3: Check Playwright cache directory
    print("📋 Test 3: Playwright cache directory")
    if system == "darwin":
        browser_cache = Path.home() / "Library" / "Caches" / "ms-playwright"
    elif system == "windows":
        browser_cache = Path.home() / "AppData" / "Local" / "ms-playwright"
    else:
        browser_cache = Path.home() / ".cache" / "ms-playwright"
    
    print(f"Cache directory: {browser_cache}")
    print(f"Exists: {browser_cache.exists()}")
    
    if browser_cache.exists():
        chromium_dirs = list(browser_cache.glob("chromium-*"))
        print(f"Chromium directories found: {len(chromium_dirs)}")
        for dir in chromium_dirs:
            print(f"  - {dir.name}")
            # Check if executable exists in this directory
            if system == "darwin":
                exec_path = dir / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
            elif system == "windows":
                exec_path = dir / "chrome-win" / "chrome.exe"
            else:
                exec_path = dir / "chrome-linux" / "chrome"
            
            if exec_path.exists():
                print(f"    ✅ Executable found: {exec_path}")
            else:
                print(f"    ❌ Executable missing: {exec_path}")
    print()
    
    # Test 4: Environment variables
    print("📋 Test 4: Environment variables")
    playwright_browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    playwright_chromium_path = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    
    print(f"PLAYWRIGHT_BROWSERS_PATH: {playwright_browsers_path or 'Not set'}")
    print(f"PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH: {playwright_chromium_path or 'Not set'}")
    print()
    
    # Test 5: Try to launch a browser
    print("📋 Test 5: Browser launch test")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
            print("✅ Successfully launched and closed Chromium browser")
    except Exception as e:
        print(f"❌ Failed to launch browser: {e}")
        print("   This is the main issue you need to fix!")
    print()
    
    # Test 6: Network connectivity
    print("📋 Test 6: Network connectivity")
    test_urls = [
        "https://www.google.com",
        "https://storage.googleapis.com",
        "https://www.chromium.org"
    ]
    
    for url in test_urls:
        try:
            import urllib.request
            import ssl
            
            # Create SSL context that ignores certificate issues
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
            urllib.request.install_opener(opener)
            
            response = urllib.request.urlopen(url, timeout=10)
            print(f"✅ {url} - Accessible")
        except Exception as e:
            print(f"❌ {url} - Failed: {e}")
    
    # Test DNS resolution
    try:
        import socket
        socket.gethostbyname("storage.googleapis.com")
        print("✅ DNS resolution - Working")
    except Exception as e:
        print(f"❌ DNS resolution - Failed: {e}")
    print()
    
    # Test 7: Disk space
    print("📋 Test 7: Disk space")
    try:
        import shutil
        if system == "darwin":
            path_to_check = Path.home() / "Library" / "Caches"
        elif system == "windows":
            path_to_check = Path.home() / "AppData" / "Local"
        else:
            path_to_check = Path.home() / ".cache"
        
        total, used, free = shutil.disk_usage(path_to_check)
        free_gb = free // (1024**3)
        print(f"Available disk space: {free_gb} GB")
        if free_gb < 1:
            print("⚠️  Warning: Less than 1GB available disk space")
        else:
            print("✅ Sufficient disk space available")
    except Exception as e:
        print(f"❌ Could not check disk space: {e}")
    print()
    
    # Summary and recommendations
    print("📋 SUMMARY AND RECOMMENDATIONS:")
    print("=" * 50)
    
    if not found_browsers:
        print("❌ No system browsers found")
        print("💡 RECOMMENDATION: Install Google Chrome or Chromium")
        if system == "darwin":
            print("   - Visit https://www.google.com/chrome/")
            print("   - Or run: brew install --cask chromium")
        elif system == "windows":
            print("   - Visit https://www.google.com/chrome/")
        else:
            print("   - Run: sudo apt-get install chromium-browser")
    
    if not browser_cache.exists() or len(list(browser_cache.glob("chromium-*"))) == 0:
        print("❌ No Playwright browsers installed")
        print("💡 RECOMMENDATION: Allow the application to download browsers")
        print("   - Run the application again")
        print("   - When prompted, allow browser download")
    
    print("\n🔧 QUICK FIXES TO TRY:")
    print("1. Install Google Chrome from https://www.google.com/chrome/")
    print("2. Run the application again and allow browser download when prompted")
    print("3. Check your internet connection")
    print("4. See BROWSER_INSTALLATION.md for detailed instructions")

if __name__ == "__main__":
    test_browser_installation() 