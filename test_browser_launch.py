#!/usr/bin/env python3
"""
Simple test script to verify browser launch functionality.
"""

import sys
from pathlib import Path

# Add the current directory to the path so we can import visa_autofill
sys.path.insert(0, str(Path(__file__).parent))

def test_browser_launch():
    """Test that we can launch a browser successfully."""
    print("🧪 Testing browser launch functionality...")
    
    try:
        # Import and test browser setup
        from visa_autofill import ensure_browsers_available
        print("✅ Browser setup function imported successfully")
        
        # Ensure browsers are available
        ensure_browsers_available()
        print("✅ Browser setup completed successfully")
        
        # Test actual browser launch
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            print("🚀 Launching browser...")
            browser = p.chromium.launch(headless=True)
            print("✅ Browser launched successfully")
            
            print("🌐 Creating page...")
            page = browser.new_page()
            print("✅ Page created successfully")
            
            print("📄 Navigating to test page...")
            page.goto("https://www.google.com")
            print("✅ Navigation successful")
            
            print("📝 Getting page title...")
            title = page.title()
            print(f"✅ Page title: {title}")
            
            print("🔒 Closing browser...")
            browser.close()
            print("✅ Browser closed successfully")
        
        print("\n🎉 All tests passed! Browser functionality is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 This indicates the browser installation issue you encountered.")
        print("🔧 Try these solutions:")
        print("   1. Install Google Chrome from https://www.google.com/chrome/")
        print("   2. Run the application again and allow browser download when prompted")
        print("   3. Check your internet connection")
        print("   4. See BROWSER_INSTALLATION.md for detailed instructions")
        return False

if __name__ == "__main__":
    success = test_browser_launch()
    sys.exit(0 if success else 1) 