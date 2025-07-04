#!/usr/bin/env python3
"""
Creates a distribution package for the Visa GUI application.
This script packages the app with user instructions for easy distribution.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_instructions_file():
    """Create a simple instruction file for recipients."""
    instructions = """
# Visa GUI Application - Setup Instructions

## Quick Start
1. Extract this ZIP file to your Desktop
2. Double-click on "visa_gui.app" to run
3. When prompted, click "Yes" to install browser components (one-time setup)
4. Wait for installation to complete (~2-5 minutes)
5. The application will start automatically

## First Time Setup
The application needs to download Chromium browser to function. This happens automatically on first run and requires an internet connection.

## Troubleshooting

### Security Warning
If macOS shows a security warning:
1. Right-click the app → "Open"
2. Click "Open" in the security dialog
OR
1. System Preferences → Security & Privacy → General
2. Click "Open Anyway" next to the blocked app

### Browser Installation Issues
If browser installation fails:
- Check your internet connection
- Ensure you have ~500MB free disk space
- Try running the app again
- Contact the sender for support

### Technical Support
If you encounter any issues:
1. Try restarting the application
2. Check that you're running macOS 10.13 or later
3. Contact the person who sent you this application

## What This App Does
This is a visa application automation tool that helps fill out visa forms automatically using data from spreadsheets.

---
For more information, visit: [Your support contact]
"""
    return instructions

def create_distribution_package():
    """Create a distribution package with the app and instructions."""
    
    # Check if the app exists
    app_path = Path("dist/visa_gui.app")
    if not app_path.exists():
        print("❌ Application not found at dist/visa_gui.app")
        print("Please build the application first with: python build_app.py")
        return False
    
    # Create distribution directory
    dist_dir = Path("distribution")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    print("📦 Creating distribution package...")
    
    # Copy the app
    print("  Copying application...")
    shutil.copytree(app_path, dist_dir / "visa_gui.app")
    
    # Create instructions
    print("  Creating instructions...")
    instructions_file = dist_dir / "README - START HERE.txt"
    with open(instructions_file, 'w') as f:
        f.write(create_instructions_file())
    
    # Get version info
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create ZIP file
    zip_filename = f"visa_gui_app_{timestamp}.zip"
    print(f"  Creating ZIP file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the app
        for root, dirs, files in os.walk(dist_dir / "visa_gui.app"):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(dist_dir)
                zipf.write(file_path, arc_path)
        
        # Add instructions
        zipf.write(instructions_file, "README - START HERE.txt")
    
    # Clean up temp directory
    shutil.rmtree(dist_dir)
    
    # Get file size
    zip_size = Path(zip_filename).stat().st_size / (1024 * 1024)  # MB
    
    print("✅ Distribution package created successfully!")
    print(f"📁 File: {zip_filename}")
    print(f"📏 Size: {zip_size:.1f} MB")
    print()
    print("📤 Distribution Instructions:")
    print("1. Send the ZIP file to recipients")
    print("2. Recipients should extract and read 'README - START HERE.txt'")
    print("3. App will auto-install browsers on first run")
    print()
    print("💡 Tips:")
    print("- Test on another Mac before distributing")
    print("- Include your contact info for support")
    print("- Mention the one-time browser setup in your message")
    
    return True

def main():
    """Main function."""
    print("🚀 Visa GUI Distribution Package Creator")
    print("=" * 50)
    
    if not create_distribution_package():
        sys.exit(1)
    
    print("\n🎉 Ready for distribution!")

if __name__ == "__main__":
    main() 