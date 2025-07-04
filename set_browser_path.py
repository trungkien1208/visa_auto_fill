#!/usr/bin/env python3
"""
Helper script to set Playwright browser path for development and testing.
This can be useful if you want to use system browsers instead of bundled ones.
"""

import os
import subprocess
from pathlib import Path

def find_system_chromium():
    """Try to find system-installed Chromium/Chrome."""
    possible_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def main():
    print("Setting up Playwright browser paths...")
    
    # Try to find system browser
    system_browser = find_system_chromium()
    if system_browser:
        print(f"Found system browser: {system_browser}")
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.dirname(system_browser)
        print(f"Set PLAYWRIGHT_BROWSERS_PATH to: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
    else:
        print("No system browser found, using default Playwright browsers")
    
    # Install Playwright browsers if not found
    try:
        result = subprocess.run(["playwright", "install", "chromium"], 
                              capture_output=True, text=True, check=True)
        print("Playwright browsers installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing browsers: {e}")
        print("You may need to run: pip install playwright && playwright install")

if __name__ == "__main__":
    main() 