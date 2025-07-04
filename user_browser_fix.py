#!/usr/bin/env python3
"""
Simple browser fix script for end users.
This script helps diagnose and fix browser installation issues.
"""

import os
import sys
import platform
from pathlib import Path

def print_header():
    """Print a user-friendly header."""
    print("🔧 Visa Autofill - Browser Fix Tool")
    print("=" * 50)
    print("This tool will help fix browser installation issues.")
    print()

def check_system():
    """Check system information."""
    print("📋 System Information:")
    print(f"   Operating System: {platform.system()} {platform.release()}")
    print(f"   Architecture: {platform.machine()}")
    print(f"   Python Version: {sys.version.split()[0]}")
    print()

def check_internet():
    """Check internet connectivity."""
    print("🌐 Checking internet connection...")
    
    try:
        import urllib.request
        import ssl
        
        # Create SSL context that ignores certificate issues
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
        urllib.request.install_opener(opener)
        
        # Test multiple URLs
        test_urls = [
            "https://www.google.com",
            "https://storage.googleapis.com",
            "https://www.chromium.org"
        ]
        
        working_urls = 0
        for url in test_urls:
            try:
                response = urllib.request.urlopen(url, timeout=10)
                print(f"   ✅ {url} - Working")
                working_urls += 1
            except Exception as e:
                print(f"   ❌ {url} - Failed: {e}")
        
        if working_urls > 0:
            print("   ✅ Internet connection is working")
            return True
        else:
            print("   ❌ Internet connection issues detected")
            return False
            
    except Exception as e:
        print(f"   ❌ Could not test internet: {e}")
        return False

def check_browsers():
    """Check for existing browsers."""
    print("\n🔍 Checking for existing browsers...")
    
    system = platform.system().lower()
    found_browsers = []
    
    if system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            Path.home() / "Applications" / "Google Chrome.app" / "Contents" / "MacOS" / "Google Chrome",
            Path.home() / "Applications" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
        ]
    elif system == "windows":
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
    
    for path in chrome_paths:
        if Path(path).exists():
            print(f"   ✅ Found: {path}")
            found_browsers.append(str(path))
        else:
            print(f"   ❌ Not found: {path}")
    
    if found_browsers:
        print(f"   ✅ Found {len(found_browsers)} browser(s)")
        return True
    else:
        print("   ❌ No browsers found")
        return False

def check_playwright_cache():
    """Check Playwright browser cache."""
    print("\n📁 Checking Playwright browser cache...")
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        cache_dir = Path.home() / "Library" / "Caches" / "ms-playwright"
    elif system == "windows":
        cache_dir = Path.home() / "AppData" / "Local" / "ms-playwright"
    else:  # Linux
        cache_dir = Path.home() / ".cache" / "ms-playwright"
    
    print(f"   Cache directory: {cache_dir}")
    print(f"   Exists: {cache_dir.exists()}")
    
    if cache_dir.exists():
        chromium_dirs = list(cache_dir.glob("chromium-*"))
        print(f"   Chromium installations: {len(chromium_dirs)}")
        
        for dir in chromium_dirs:
            print(f"     - {dir.name}")
            
            # Check if executable exists
            if system == "darwin":
                exec_path = dir / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
            elif system == "windows":
                exec_path = dir / "chrome-win" / "chrome.exe"
            else:
                exec_path = dir / "chrome-linux" / "chrome"
            
            if exec_path.exists():
                print(f"       ✅ Executable found")
            else:
                print(f"       ❌ Executable missing")
        
        return len(chromium_dirs) > 0
    else:
        print("   ❌ No Playwright cache found")
        return False

def provide_solutions():
    """Provide solutions based on the diagnosis."""
    print("\n🔧 SOLUTIONS:")
    print("=" * 50)
    
    print("1️⃣ SIMPLE SOLUTION (Recommended):")
    print("   • Close the Visa Autofill application")
    print("   • Make sure you have internet connection")
    print("   • Run the application again")
    print("   • When prompted, click 'Yes' to download browser")
    print("   • Wait for download to complete (~150 MB)")
    print()
    
    print("2️⃣ ALTERNATIVE SOLUTION:")
    print("   • Install Google Chrome from https://www.google.com/chrome/")
    print("   • Restart the Visa Autofill application")
    print()
    
    print("3️⃣ IF INTERNET IS THE PROBLEM:")
    print("   • Check your internet connection")
    print("   • Try disabling VPN or proxy")
    print("   • Try using a different network (mobile hotspot)")
    print()
    
    print("4️⃣ IF NOTHING WORKS:")
    print("   • Contact support with this diagnostic information")
    print("   • Try on a different computer")
    print()

def main():
    """Main function."""
    print_header()
    
    # Check system
    check_system()
    
    # Check internet
    internet_ok = check_internet()
    
    # Check browsers
    browsers_ok = check_browsers()
    
    # Check Playwright cache
    cache_ok = check_playwright_cache()
    
    # Provide solutions
    provide_solutions()
    
    # Summary
    print("📊 SUMMARY:")
    print("=" * 50)
    print(f"Internet Connection: {'✅ Working' if internet_ok else '❌ Issues'}")
    print(f"System Browsers: {'✅ Found' if browsers_ok else '❌ Not found'}")
    print(f"Playwright Cache: {'✅ Found' if cache_ok else '❌ Not found'}")
    print()
    
    if not internet_ok:
        print("⚠️  Internet connection issues detected!")
        print("   The app needs internet to download browsers.")
        print("   Please check your connection and try again.")
    elif not browsers_ok and not cache_ok:
        print("⚠️  No browsers found!")
        print("   The app will need to download a browser on first run.")
        print("   Make sure to allow the download when prompted.")
    else:
        print("✅ Everything looks good!")
        print("   Try running the Visa Autofill application again.")
    
    print("\n💡 Need help? Contact support with this diagnostic information.")

if __name__ == "__main__":
    main() 