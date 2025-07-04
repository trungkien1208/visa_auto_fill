#!/usr/bin/env python3
"""
Script to prepare macOS app for distribution.
This script handles common issues that prevent macOS apps from running on other Macs.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_app_exists():
    """Check if the app bundle exists."""
    app_path = Path("dist/visa_gui.app")
    if not app_path.exists():
        print("❌ App bundle not found at dist/visa_gui.app")
        print("Please run the build script first: python3 build_app.py")
        return False
    return True

def remove_quarantine_flag(app_path):
    """Remove quarantine flag from the app."""
    print("🔓 Removing quarantine flag...")
    try:
        subprocess.run([
            "xattr", "-rd", "com.apple.quarantine", str(app_path)
        ], check=True)
        print("✅ Quarantine flag removed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not remove quarantine flag: {e}")
        return False

def check_quarantine_flag(app_path):
    """Check if app has quarantine flag."""
    try:
        result = subprocess.run([
            "xattr", "-p", "com.apple.quarantine", str(app_path)
        ], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def create_dmg(app_path):
    """Create a DMG file for easier distribution."""
    print("📦 Creating DMG file...")
    dmg_path = Path("dist/visa_gui.dmg")
    
    try:
        # Remove existing DMG
        if dmg_path.exists():
            dmg_path.unlink()
        
        # Create DMG
        subprocess.run([
            "hdiutil", "create", "-volname", "Visa Autofill",
            "-srcfolder", str(app_path), str(dmg_path)
        ], check=True)
        
        print(f"✅ DMG created: {dmg_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create DMG: {e}")
        return False

def create_zip_archive(app_path):
    """Create a ZIP archive for distribution."""
    print("📦 Creating ZIP archive...")
    zip_path = Path("dist/visa_gui.zip")
    
    try:
        # Remove existing ZIP
        if zip_path.exists():
            zip_path.unlink()
        
        # Create ZIP
        shutil.make_archive(
            str(zip_path.with_suffix('')),  # Remove .zip extension
            'zip',
            app_path.parent,
            app_path.name
        )
        
        print(f"✅ ZIP created: {zip_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create ZIP: {e}")
        return False

def add_notarization_info():
    """Add information about notarization."""
    print("\n📋 Distribution Notes:")
    print("=" * 50)
    print("For distribution to other Macs, consider these options:")
    print()
    print("1. 🍎 Apple Developer Program (Recommended):")
    print("   - Sign up for Apple Developer Program ($99/year)")
    print("   - Code sign your app with a Developer ID")
    print("   - Notarize your app with Apple")
    print("   - Users can run without security warnings")
    print()
    print("2. 🔓 Manual Installation (Current):")
    print("   - Users need to right-click and 'Open' the first time")
    print("   - Or go to System Preferences > Security & Privacy")
    print("   - Click 'Open Anyway' for visa_gui.app")
    print()
    print("3. 🛡️  Gatekeeper Bypass Instructions for Users:")
    print("   - Right-click on visa_gui.app")
    print("   - Select 'Open' from the context menu")
    print("   - Click 'Open' in the security dialog")
    print("   - Or: System Preferences > Security & Privacy > General > Open Anyway")

def main():
    """Main function."""
    print("🍎 macOS Distribution Preparation")
    print("=" * 40)
    
    # Check if app exists
    if not check_app_exists():
        sys.exit(1)
    
    app_path = Path("dist/visa_gui.app")
    
    # Check current quarantine status
    if check_quarantine_flag(app_path):
        print("⚠️  App has quarantine flag (normal for downloaded apps)")
        remove_quarantine_flag(app_path)
    else:
        print("✅ App does not have quarantine flag")
    
    # Create distribution packages
    print("\n📦 Creating distribution packages...")
    
    # Create ZIP
    create_zip_archive(app_path)
    
    # Try to create DMG (macOS only)
    try:
        subprocess.run(["hdiutil"], capture_output=True, check=True)
        create_dmg(app_path)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  hdiutil not available, skipping DMG creation")
    
    # Show distribution info
    add_notarization_info()
    
    print("\n✅ Distribution preparation completed!")
    print(f"📁 App location: {app_path}")
    print(f"📦 ZIP archive: dist/visa_gui.zip")
    
    # Check for DMG
    dmg_path = Path("dist/visa_gui.dmg")
    if dmg_path.exists():
        print(f"📦 DMG archive: {dmg_path}")

if __name__ == "__main__":
    main() 