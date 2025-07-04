#!/usr/bin/env python3
"""
Browser installation fix script.
Use this script if you encounter browser installation issues.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def clear_playwright_cache():
    """Clear Playwright cache to force fresh installation."""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        cache_dir = Path.home() / "Library" / "Caches" / "ms-playwright"
    elif system == "windows":  # Windows
        cache_dir = Path.home() / "AppData" / "Local" / "ms-playwright"
    else:  # Linux
        cache_dir = Path.home() / ".cache" / "ms-playwright"
    
    if cache_dir.exists():
        print(f"🗑️  Clearing Playwright cache: {cache_dir}")
        try:
            import shutil
            shutil.rmtree(cache_dir)
            print("✅ Cache cleared successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to clear cache: {e}")
            return False
    else:
        print("ℹ️  No Playwright cache found")
        return True

def clear_environment_variables():
    """Clear any Playwright-related environment variables."""
    vars_to_clear = [
        "PLAYWRIGHT_BROWSERS_PATH",
        "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH",
        "PLAYWRIGHT_FIREFOX_EXECUTABLE_PATH",
        "PLAYWRIGHT_WEBKIT_EXECUTABLE_PATH"
    ]
    
    cleared = []
    for var in vars_to_clear:
        if var in os.environ:
            del os.environ[var]
            cleared.append(var)
    
    if cleared:
        print(f"🧹 Cleared environment variables: {', '.join(cleared)}")
    else:
        print("ℹ️  No Playwright environment variables found")
    
    return True

def install_playwright_browsers():
    """Install Playwright browsers using the standard method."""
    print("📦 Installing Playwright browsers...")
    
    try:
        # Try different Python executables
        python_executables = [
            sys.executable,
            "/usr/bin/python3",
            "/usr/local/bin/python3",
            "/opt/homebrew/bin/python3",
            "python3",
            "python"
        ]
        
        for python_exe in python_executables:
            try:
                print(f"🔍 Trying with: {python_exe}")
                
                # Test if this Python has playwright
                test_result = subprocess.run(
                    [python_exe, "-c", "import playwright.sync_api"],
                    capture_output=True,
                    timeout=10
                )
                
                if test_result.returncode != 0:
                    print(f"   ❌ {python_exe} doesn't have playwright")
                    continue
                
                print(f"   ✅ {python_exe} has playwright, installing browsers...")
                
                # Install browsers
                result = subprocess.run(
                    [python_exe, "-m", "playwright", "install", "chromium"],
                    capture_output=False,
                    text=True,
                    check=True,
                    timeout=600
                )
                
                print("✅ Playwright browsers installed successfully!")
                return True
                
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"   ❌ Failed with {python_exe}: {e}")
                continue
        
        print("❌ Failed to install browsers with any Python executable")
        return False
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def test_browser_installation():
    """Test if the browser installation worked."""
    print("🧪 Testing browser installation...")
    
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
            print("✅ Browser test successful!")
            return True
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return False

def main():
    """Main fix function."""
    print("🔧 Browser Installation Fix Script")
    print("=" * 40)
    
    # Step 1: Clear environment variables
    print("\n1️⃣ Clearing environment variables...")
    clear_environment_variables()
    
    # Step 2: Clear cache
    print("\n2️⃣ Clearing Playwright cache...")
    clear_playwright_cache()
    
    # Step 3: Install browsers
    print("\n3️⃣ Installing Playwright browsers...")
    if not install_playwright_browsers():
        print("\n❌ Automatic installation failed.")
        print("💡 Manual solutions:")
        print("   1. Install Google Chrome from https://www.google.com/chrome/")
        print("   2. Run: pip install playwright && playwright install chromium")
        print("   3. See BROWSER_INSTALLATION.md for detailed instructions")
        return False
    
    # Step 4: Test installation
    print("\n4️⃣ Testing browser installation...")
    if not test_browser_installation():
        print("\n❌ Browser test failed after installation.")
        print("💡 Try running the application again or see BROWSER_INSTALLATION.md")
        return False
    
    print("\n🎉 Browser installation fixed successfully!")
    print("✅ You can now run the visa application.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 