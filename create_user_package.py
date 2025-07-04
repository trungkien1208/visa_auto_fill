#!/usr/bin/env python3
"""
Create a user-friendly distribution package.
This script creates a complete package with the app and all necessary documentation.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

def create_user_package():
    """Create a complete user package with app and documentation."""
    print("📦 Creating User Distribution Package")
    print("=" * 50)
    
    # Check if the app exists
    app_path = Path("dist/visa_gui.app")
    if not app_path.exists():
        print("❌ App not found! Please build the app first:")
        print("   python3 build_app.py")
        return False
    
    # Create package directory
    package_dir = Path("user_package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print("📁 Creating package directory...")
    
    # Copy the app
    print("📱 Copying application...")
    shutil.copytree(app_path, package_dir / "visa_gui.app")
    
    # Copy documentation files
    print("📚 Copying documentation...")
    docs_to_copy = [
        "USER_INSTALLATION_GUIDE.md",
        "BROWSER_INSTALLATION.md",
        "README.md"
    ]
    
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy2(doc, package_dir)
            print(f"   ✅ Copied {doc}")
        else:
            print(f"   ⚠️  {doc} not found")
    
    # Copy user tools
    print("🔧 Copying user tools...")
    tools_to_copy = [
        "user_browser_fix.py",
        "quick_browser_fix.py",
        "test_browser_install.py"
    ]
    
    for tool in tools_to_copy:
        if Path(tool).exists():
            shutil.copy2(tool, package_dir)
            print(f"   ✅ Copied {tool}")
        else:
            print(f"   ⚠️  {tool} not found")
    
    # Create a simple README for the package
    print("📝 Creating package README...")
    package_readme = package_dir / "README.txt"
    
    readme_content = """Visa Autofill Application Package

This package contains everything you need to run the Visa Autofill application.

📱 APPLICATION:
- visa_gui.app - The main application

📚 DOCUMENTATION:
- USER_INSTALLATION_GUIDE.md - Step-by-step installation guide
- BROWSER_INSTALLATION.md - Detailed browser installation help
- README.md - Technical documentation

🔧 TOOLS:
- quick_browser_fix.py - Quick browser fix script
- user_browser_fix.py - User-friendly browser diagnostic tool
- test_browser_install.py - Advanced browser diagnostic tool

🚀 QUICK START:
1. Right-click on visa_gui.app and select "Open"
2. Click "Open" in the security dialog
3. When prompted, allow browser download
4. Follow the on-screen instructions

📞 NEED HELP?
- Read USER_INSTALLATION_GUIDE.md first
- Run user_browser_fix.py for diagnostics
- Contact support if issues persist

System Requirements:
- macOS 10.15 (Catalina) or later
- Internet connection
- At least 1GB free disk space
"""
    
    with open(package_readme, 'w') as f:
        f.write(readme_content)
    
    # Create ZIP file
    print("🗜️  Creating ZIP archive...")
    zip_path = Path("visa_gui_user_package.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in package_dir.rglob('*'):
            if item.is_file():
                arcname = item.relative_to(package_dir)
                zipf.write(item, arcname)
                print(f"   📦 Added {arcname}")
    
    # Create DMG instructions
    print("💿 DMG Creation Instructions:")
    print("   To create a DMG file for professional distribution:")
    print("   1. Install DMG Canvas or use hdiutil")
    print("   2. Create a DMG with the contents of the user_package folder")
    print("   3. Include a link to Applications folder")
    print("   4. Set background image if desired")
    
    print("\n✅ Package created successfully!")
    print(f"📦 Package location: {package_dir}")
    print(f"🗜️  ZIP file: {zip_path}")
    print(f"📏 Package size: {get_folder_size(package_dir):.1f} MB")
    print(f"🗜️  ZIP size: {zip_path.stat().st_size / (1024*1024):.1f} MB")
    
    print("\n📋 Distribution Instructions:")
    print("1. Share the ZIP file with users")
    print("2. Include USER_INSTALLATION_GUIDE.md")
    print("3. Provide support contact information")
    print("4. Test on a clean Mac before distribution")
    
    return True

def get_folder_size(folder_path):
    """Get the size of a folder in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # Convert to MB

def main():
    """Main function."""
    print("🚀 Visa Autofill - User Package Creator")
    print("=" * 50)
    
    if not Path("dist/visa_gui.app").exists():
        print("❌ App not found! Please build the app first:")
        print("   python3 build_app.py")
        sys.exit(1)
    
    if create_user_package():
        print("\n🎉 Package creation completed!")
        print("You can now distribute the package to users.")
    else:
        print("\n❌ Package creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 