# macOS Distribution Guide

This guide explains how to distribute your macOS app to other users and handle common security issues.

## Quick Start

### For Developers (You)

1. **Build the app:**
   ```bash
   python3 build_app.py
   ```

2. **Prepare for distribution:**
   ```bash
   python3 prepare_macos_distribution.py
   ```

3. **Share the files:**
   - `dist/visa_gui.app` - The app bundle
   - `dist/visa_gui.zip` - Compressed version
   - `dist/visa_gui.dmg` - Disk image (if created)

### For Users (Other Macs)

1. **Download and extract** the app
2. **Right-click** on `visa_gui.app`
3. **Select "Open"** from the context menu
4. **Click "Open"** in the security dialog

## Common Issues and Solutions

### Issue: "App can't be opened because it is from an unidentified developer"

**Solution 1: Right-click Method (Easiest)**
1. Right-click on `visa_gui.app`
2. Select "Open" from the context menu
3. Click "Open" in the security dialog
4. The app will now open normally

**Solution 2: System Preferences Method**
1. Go to System Preferences > Security & Privacy
2. Click the "General" tab
3. Look for a message about `visa_gui.app` being blocked
4. Click "Open Anyway"

**Solution 3: Terminal Method**
```bash
# Remove quarantine flag
xattr -rd com.apple.quarantine /path/to/visa_gui.app

# Or allow the app
sudo spctl --master-disable
```

### Issue: "App is damaged and can't be opened"

**Solution:**
1. Open Terminal
2. Run: `xattr -rd com.apple.quarantine /path/to/visa_gui.app`
3. Try opening the app again

### Issue: App opens but crashes immediately

**Solution:**
1. Check if the user has internet connection (needed for browser download)
2. Run the user-friendly diagnostic script: `python3 user_browser_fix.py`
3. Check the application logs
4. See `USER_INSTALLATION_GUIDE.md` for detailed troubleshooting

## Distribution Methods

### Method 1: Direct App Bundle
- Share `visa_gui.app` directly
- Users drag to Applications folder
- Pros: Simple, no installation needed
- Cons: May trigger security warnings

### Method 2: ZIP Archive
- Share `visa_gui.zip`
- Users extract and run
- Pros: Smaller file size, easier to share
- Cons: Same security issues as direct app

### Method 3: DMG File
- Share `visa_gui.dmg`
- Users mount and drag to Applications
- Pros: Standard macOS distribution method
- Cons: Larger file size

### Method 4: Apple Developer Program (Recommended for Production)
- Sign up for Apple Developer Program ($99/year)
- Code sign your app with Developer ID
- Notarize with Apple
- Users can run without security warnings

## Security Considerations

### Gatekeeper
macOS Gatekeeper prevents running unsigned apps by default. Your app is unsigned, so users need to bypass this.

### Quarantine Flag
When apps are downloaded from the internet, macOS adds a quarantine flag. This can be removed with:
```bash
xattr -rd com.apple.quarantine /path/to/visa_gui.app
```

### Code Signing
For production distribution, consider:
1. **Apple Developer Program** - Official code signing
2. **Self-signed certificates** - For internal distribution
3. **Ad-hoc signing** - For testing

## User Instructions Template

Include these instructions when sharing your app:

---

### How to Install and Run Visa Autofill

1. **Download** the app file (`visa_gui.app` or `visa_gui.zip`)

2. **If you downloaded a ZIP file:**
   - Double-click to extract
   - You'll see `visa_gui.app`

3. **Install the app:**
   - Drag `visa_gui.app` to your Applications folder
   - Or keep it in Downloads (either works)

4. **First time opening:**
   - **Right-click** on `visa_gui.app`
   - Select **"Open"** from the menu
   - Click **"Open"** in the security dialog
   - The app will now open normally

5. **Subsequent launches:**
   - Double-click the app normally
   - Or use Spotlight (Cmd+Space, type "visa")

### Troubleshooting

**If you see "App can't be opened because it is from an unidentified developer":**
1. Right-click the app
2. Select "Open"
3. Click "Open" in the dialog

**If the app won't open:**
1. Make sure you have internet connection
2. Try right-clicking and selecting "Open"
3. Check System Preferences > Security & Privacy

**Need help?** Contact support with your macOS version and any error messages.

---

## Advanced Distribution

### Creating a Proper Installer
For professional distribution, consider using:
- **Packages** - Create .pkg installers
- **Install4j** - Cross-platform installer
- **DMG Canvas** - Professional DMG creation

### Automated Distribution
- **GitHub Releases** - For open source projects
- **Sparkle** - Auto-update framework
- **App Store** - Official distribution (requires Apple Developer Program)

## Testing Distribution

Before sharing with users:

1. **Test on a clean Mac** (or different user account)
2. **Test without internet** (to see browser download behavior)
3. **Test on different macOS versions**
4. **Test with different security settings**

## Support

If users have issues:

1. **Collect information:**
   - macOS version
   - Error messages
   - Steps taken
   - Screenshots if possible

2. **Common solutions:**
   - Right-click and "Open"
   - Remove quarantine flag
   - Check internet connection
   - Run diagnostic script

3. **Escalation:**
   - Check application logs
   - Test on your system
   - Consider code signing for production use 