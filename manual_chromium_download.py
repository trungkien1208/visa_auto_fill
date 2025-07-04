#!/usr/bin/env python3
"""
Manual Chromium download script.
Use this script if the automatic browser installation fails.
"""

import os
import sys
import platform
import urllib.request
import zipfile
import subprocess
from pathlib import Path

def get_chromium_url(version="131000"):
    """Get the appropriate Chromium download URL for the current system."""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "darwin":  # macOS
        if "arm" in arch or "m1" in arch or "m2" in arch:
            return f"https://storage.googleapis.com/chromium-browser-snapshots/Mac_Arm/{version}/chrome-mac.zip"
        else:
            return f"https://storage.googleapis.com/chromium-browser-snapshots/Mac/{version}/chrome-mac.zip"
    elif system == "windows":  # Windows
        if "64" in arch:
            return f"https://storage.googleapis.com/chromium-browser-snapshots/Win_x64/{version}/chrome-win.zip"
        else:
            return f"https://storage.googleapis.com/chromium-browser-snapshots/Win/{version}/chrome-win.zip"
    else:  # Linux
        return f"https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/{version}/chrome-linux.zip"

def get_cache_directory():
    """Get the Playwright cache directory for the current system."""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        return Path.home() / "Library" / "Caches" / "ms-playwright"
    elif system == "windows":  # Windows
        return Path.home() / "AppData" / "Local" / "ms-playwright"
    else:  # Linux
        return Path.home() / ".cache" / "ms-playwright"

def download_chromium(version="131000"):
    """Download Chromium manually."""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"🔍 System: {system}, Architecture: {arch}")
    print(f"📥 Downloading Chromium version {version}...")
    
    # Get download URL
    download_url = get_chromium_url(version)
    print(f"🔗 Download URL: {download_url}")
    
    # Get cache directory
    cache_dir = get_cache_directory()
    chromium_dir = cache_dir / f"chromium-{version}"
    
    print(f"📁 Cache directory: {cache_dir}")
    print(f"📁 Chromium directory: {chromium_dir}")
    
    # Create directories
    cache_dir.mkdir(parents=True, exist_ok=True)
    chromium_dir.mkdir(parents=True, exist_ok=True)
    
    # Download file
    zip_path = chromium_dir / "chromium.zip"
    print(f"📦 Downloading to: {zip_path}")
    
    try:
        # Create SSL context
        import ssl
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
        urllib.request.install_opener(opener)
        
        # Download with progress
        def show_progress(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\r📥 Downloading... {percent}%", end="", flush=True)
        
        urllib.request.urlretrieve(download_url, zip_path, show_progress)
        print()  # New line after progress
        
        # Verify download
        if not zip_path.exists() or zip_path.stat().st_size < 1000000:
            print("❌ Download failed - file too small or missing")
            return False
        
        print(f"✅ Download completed: {zip_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Extract
        print("📦 Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(chromium_dir)
        
        # Clean up
        zip_path.unlink()
        print("✅ Extraction completed")
        
        # Set permissions (macOS/Linux)
        if system in ["darwin", "linux"]:
            if system == "darwin":
                executable_path = chromium_dir / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
                app_path = chromium_dir / "chrome-mac" / "Chromium.app"
            else:
                executable_path = chromium_dir / "chrome-linux" / "chrome"
                app_path = None
            
            if executable_path.exists():
                executable_path.chmod(0o755)
                print(f"✅ Set permissions for: {executable_path}")
            
            if app_path and app_path.exists():
                subprocess.run(["chmod", "-R", "+x", str(app_path)], check=False)
                print(f"✅ Set permissions for app bundle")
        
        print("✅ Chromium installation completed!")
        print(f"📁 Location: {chromium_dir}")
        
        # Set environment variable
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(cache_dir)
        print(f"🔧 Set PLAYWRIGHT_BROWSERS_PATH to: {cache_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        # Clean up failed download
        try:
            if zip_path.exists():
                zip_path.unlink()
        except:
            pass
        return False

def main():
    """Main function."""
    print("🔧 Manual Chromium Download Tool")
    print("=" * 40)
    print()
    
    # Available versions
    versions = ["131000", "120000", "110000", "100000", "90000", "80000"]
    
    print("Available Chromium versions:")
    for i, version in enumerate(versions, 1):
        print(f"  {i}. {version}")
    
    print()
    
    # Get user choice
    try:
        choice = input("Select version to download (1-6, or press Enter for latest): ").strip()
        if not choice:
            selected_version = "131000"
        else:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(versions):
                selected_version = versions[choice_idx]
            else:
                print("❌ Invalid choice, using latest version")
                selected_version = "131000"
    except ValueError:
        print("❌ Invalid input, using latest version")
        selected_version = "131000"
    
    print(f"🎯 Selected version: {selected_version}")
    print()
    
    # Download
    success = download_chromium(selected_version)
    
    if success:
        print()
        print("🎉 Chromium downloaded successfully!")
        print("🔄 Please restart your application.")
    else:
        print()
        print("❌ Download failed.")
        print("💡 Try:")
        print("   - Check your internet connection")
        print("   - Try a different version")
        print("   - Install Google Chrome instead")
        print("   - Contact support for help")

if __name__ == "__main__":
    main() 