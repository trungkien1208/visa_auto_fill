# Distribution Guide for Visa GUI Application

This guide explains how to distribute your built application to other MacBooks and ensure it works properly.

## What's Changed in the Latest Build

✅ **Auto-Install Browsers**: The app now automatically downloads and installs Chromium browser on first run
✅ **User Permission Dialog**: Shows a friendly dialog asking for permission to install browsers  
✅ **Better Error Messages**: Clear instructions if installation fails
✅ **Cross-Platform Support**: Works on macOS, Windows, and Linux

## Method 1: Simple Distribution (Recommended)

### For the Recipient:
1. **Download** the `visa_gui.app` file you send them
2. **Move** it to Applications folder (optional but recommended)
3. **First Run**: Double-click the app
   - A dialog will appear asking to install browser components
   - Click "Yes" to proceed (one-time setup)
   - Wait for installation to complete (~2-5 minutes)
4. **Subsequent Runs**: App will start normally

### For You (Sender):
1. Build the app: `python build_app.py` or `make build`
2. Compress the app: Right-click `dist/visa_gui.app` → "Compress"
3. Send the `.zip` file to the recipient
4. Include the simple instructions above

## Method 2: Pre-Bundle Browsers (Large but Self-Contained)

If you want to create a completely self-contained app with browsers included:

```bash
# Create a distribution package with browsers
python create_distribution.py
```

This creates a larger file (~300MB) but requires no internet connection on the target machine.

## Method 3: Distribution with Installer Script

Create a simple installer that handles everything:

```bash
# This creates an installer package
python create_installer.py
```

## Troubleshooting for Recipients

### macOS Security Issues
If macOS says "App can't be opened because it's from an unidentified developer":

1. **Right-click** the app → **Open**
2. Click **"Open"** in the security dialog
3. Or go to **System Preferences** → **Security & Privacy** → **General** → Click **"Open Anyway"**

### Browser Installation Fails
If automatic browser installation fails:

1. **Manual Installation**:
   ```bash
   # Install Python (if not installed)
   # Download from https://python.org
   
   # Install Playwright and browsers
   pip install playwright
   playwright install chromium
   ```

2. **Check Internet Connection**: Browser download requires internet
3. **Check Disk Space**: Ensure at least 500MB free space
4. **Try Again**: Close app and reopen

### App Won't Start
1. **Check macOS Version**: Requires macOS 10.13 or later
2. **Check Architecture**: This build is for Apple Silicon (M1/M2). For Intel Macs, you need to build with `--target-arch x86_64`
3. **Check Permissions**: Make sure the app has necessary permissions

## Building for Different Mac Types

### For Apple Silicon (M1/M2) - Default
```bash
python build_app.py
# or
pyinstaller visa_gui.spec --clean
```

### For Intel Macs
```bash
pyinstaller visa_gui.spec --clean --target-arch x86_64
```

### Universal Binary (Both Intel and Apple Silicon)
```bash
pyinstaller visa_gui.spec --clean --target-arch universal2
```

## File Sizes to Expect

- **App Only**: ~150-200MB (without browsers)
- **With Browsers**: ~300-400MB (browsers included)
- **Compressed**: ~50-100MB (app only, compressed)

## Best Practices for Distribution

### 1. Test Before Distributing
- Test on a clean Mac without Python installed
- Test on both Intel and Apple Silicon if possible
- Verify first-run browser installation works

### 2. Provide Clear Instructions
- Always include setup instructions
- Mention the one-time browser installation
- Provide troubleshooting steps

### 3. Consider Your Audience
- **Technical Users**: Simple app distribution is fine
- **Non-Technical Users**: Consider pre-bundled browsers or installer
- **Enterprise**: May need code signing certificates

### 4. Handle Updates
- Include version numbers in your app
- Provide clear update instructions
- Consider auto-update mechanisms for future versions

## Code Signing (Optional but Recommended)

For professional distribution, consider code signing:

1. **Get Apple Developer Account** ($99/year)
2. **Create Signing Certificate**
3. **Sign the App**:
   ```bash
   codesign --force --deep --sign "Developer ID Application: Your Name" dist/visa_gui.app
   ```
4. **Notarize** (for macOS 10.15+):
   ```bash
   xcrun notarytool submit dist/visa_gui.app.zip --apple-id your-email --team-id YOUR_TEAM_ID --password app-specific-password
   ```

## Distribution Checklist

Before sending your app:

- [ ] App builds successfully
- [ ] Test on a clean machine
- [ ] Browser auto-installation works
- [ ] Include user instructions
- [ ] Test with recipient's macOS version
- [ ] Consider file size and compression
- [ ] Include troubleshooting guide

## Future Improvements

Consider implementing:
- [ ] Auto-update functionality
- [ ] Better progress indicators during browser installation
- [ ] Offline mode with pre-bundled browsers
- [ ] Installer package (.pkg) for easier distribution
- [ ] Digital signatures for security

---

**Note**: The latest build includes smart browser auto-installation, so most users should be able to run your app without any technical knowledge! 