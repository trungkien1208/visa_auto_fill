#!/usr/bin/env python3
"""
Cross-platform build script for visa_gui application.
Automatically detects the platform and uses the appropriate PyInstaller spec file.
Browsers are not bundled - users will download Chromium from the internet when needed.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_platform_info():
    """Get platform information and return appropriate spec file."""
    system = platform.system().lower()
    
    if system == "darwin":
        return {
            "name": "macOS",
            "spec_file": "visa_gui.spec",
            "icon_file": "icon.icns",
            "output_dir": "visa_gui.app"
        }
    elif system == "windows":
        return {
            "name": "Windows", 
            "spec_file": "visa_gui_windows.spec",
            "icon_file": "icon.ico",
            "output_dir": "visa_gui.exe"
        }
    elif system == "linux":
        return {
            "name": "Linux",
            "spec_file": "visa_gui_linux.spec", 
            "icon_file": None,
            "output_dir": "visa_gui"
        }
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def check_requirements():
    """Check if all required files and dependencies are present."""
    required_files = ["visa_gui.py", "visa_autofill.py"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    # Check if Playwright is installed
    try:
        import playwright
        print(f"✅ Playwright found")
    except ImportError:
        print("❌ Playwright not found. Install with: pip install playwright")
        return False
    
    return True

def build_application(platform_info, clean=True):
    """Build the application using PyInstaller."""
    spec_file = platform_info["spec_file"]
    
    if not Path(spec_file).exists():
        print(f"❌ Spec file {spec_file} not found!")
        return False
    
    # Check if icon file exists (if required)
    if platform_info["icon_file"] and not Path(platform_info["icon_file"]).exists():
        print(f"⚠️  Icon file {platform_info['icon_file']} not found, building without icon")
    
    print(f"🔨 Building for {platform_info['name']}...")
    print(f"📄 Using spec file: {spec_file}")
    print("🌐 Note: Browsers will be downloaded from internet when needed")
    
    # Build command
    cmd = ["pyinstaller", spec_file]
    if clean:
        cmd.append("--clean")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print(f"📦 Output location: dist/{platform_info['output_dir']}")
        
        # Show any warnings
        if result.stderr:
            print("⚠️  Build warnings:")
            print(result.stderr)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Main build function."""
    print("🚀 Visa GUI Application Builder")
    print("=" * 50)
    print("🌐 Browser download mode: Chromium will be downloaded from internet")
    print()
    
    # Get platform info
    try:
        platform_info = get_platform_info()
        print(f"🖥️  Platform: {platform_info['name']}")
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed!")
        sys.exit(1)
    
    # Ask about clean build
    clean_choice = input("\n🧹 Clean build (remove previous build files)? (Y/n): ").lower().strip()
    clean = clean_choice not in ['n', 'no']
    
    # Build the application
    print("\n" + "=" * 50)
    if build_application(platform_info, clean):
        print("\n🎉 Build completed successfully!")
        print(f"You can find your application in the 'dist' folder.")
        print("\n📋 Important notes:")
        print("• Application size is significantly smaller (no bundled browsers)")
        print("• Users will download Chromium from internet on first run")
        print("• Make sure users have internet connection for browser download")
        print("• Check BROWSER_INSTALLATION.md for troubleshooting")
        
        # Platform-specific instructions
        if platform_info['name'] == 'macOS':
            print("\nTo run: open dist/visa_gui.app")
            print("To prepare for distribution: python3 prepare_macos_distribution.py")
        elif platform_info['name'] == 'Windows':
            print("\nTo run: dist\\visa_gui.exe")
        else:
            print("\nTo run: ./dist/visa_gui")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 