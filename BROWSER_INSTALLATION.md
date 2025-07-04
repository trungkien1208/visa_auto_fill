# Browser Installation Guide

This application requires a Chromium-based browser to function. This guide will help you install and troubleshoot browser installation issues.

## Quick Start

### Option 1: Automatic Installation (Recommended)
1. Run the main application
2. When prompted, allow the application to download Chromium automatically
3. The application will handle the entire installation process

### Option 2: Manual Installation
If automatic installation fails, follow the platform-specific instructions below.

## Platform-Specific Instructions

### macOS

#### Easiest: Install Google Chrome
1. Visit https://www.google.com/chrome/
2. Download and install Google Chrome
3. Restart the application

#### Alternative: Install Chromium via Homebrew
1. Open Terminal (Applications > Utilities > Terminal)
2. Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
3. Install Chromium: `brew install --cask chromium`
4. Restart the application

#### Manual Installation
1. Open Finder and press `Cmd+Shift+G`
2. Go to: `~/Library/Caches/ms-playwright/`
3. Create folder: `chromium-131000`
4. Download Chromium from: https://download-chromium.appspot.com/
5. Extract to the `chromium-131000` folder
6. Restart the application

### Windows

#### Easiest: Install Google Chrome
1. Visit https://www.google.com/chrome/
2. Download and install Google Chrome
3. Restart the application

#### Alternative: Install Chromium
1. Visit https://www.chromium.org/getting-involved/download-chromium
2. Download Chromium for Windows
3. Install and restart the application

#### Command Line Installation
1. Open Command Prompt as Administrator
2. Install Python 3 from https://python.org
3. Run: `pip install playwright`
4. Run: `playwright install chromium`
5. Restart the application

### Linux

#### Easiest: Install Chromium
```bash
sudo apt-get update
sudo apt-get install chromium-browser
```

#### Alternative: Install Google Chrome
1. Visit https://www.google.com/chrome/
2. Download and install Google Chrome
3. Restart the application

#### Python Installation
```bash
sudo apt-get install python3 python3-pip
pip3 install playwright
playwright install chromium
```

## Troubleshooting

### Common Issues

#### 1. Network Connectivity Problems
- Check your internet connection
- Try disabling VPN or proxy
- Check firewall settings
- Try using a different network

#### 2. Corporate Network Restrictions
- Contact your IT department
- Ask them to whitelist `storage.googleapis.com`
- Use a personal network if possible

#### 3. Insufficient Disk Space
- Ensure you have at least 1GB of free space
- Clear temporary files and downloads
- Move large files to external storage

#### 4. Permission Issues (macOS/Linux)
- Ensure the application has necessary permissions
- Try running with elevated privileges if needed
- Check file permissions in the cache directory

### Diagnostic Tools

#### Test Browser Installation
Run the diagnostic script to check your installation:
```bash
python3 test_browser_install.py
```

This script will:
- Check if browsers are properly installed
- Verify Playwright can find the browsers
- Test network connectivity
- Provide detailed error information

#### Check Cache Directory
The application stores browsers in:
- **macOS**: `~/Library/Caches/ms-playwright/`
- **Windows**: `%LOCALAPPDATA%\ms-playwright\`
- **Linux**: `~/.cache/ms-playwright/`

### Environment Variables

The application uses these environment variables:
- `PLAYWRIGHT_BROWSERS_PATH`: Path to browser cache directory
- `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`: Path to specific Chromium executable

### Manual Browser Setup

If all else fails, you can manually set up the browser:

1. **Download Chromium** from https://download-chromium.appspot.com/
2. **Extract** to the appropriate cache directory
3. **Set permissions** (macOS/Linux): `chmod +x /path/to/chromium`
4. **Set environment variable**: `export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/path/to/chromium`

## Support

If you continue to experience issues:

1. Run the diagnostic script and note the output
2. Check the application logs for detailed error messages
3. Contact support with:
   - Your operating system and version
   - The diagnostic script output
   - Any error messages from the application
   - Steps you've already tried

## Technical Details

### Browser Versions
The application tries to download these Chromium versions in order:
- 131000 (latest)
- 120000 (recent stable)
- 110000 (older stable)
- 100000 (much older)
- 90000 (fallback)
- 80000 (final fallback)

### Download Methods
The application tries multiple download methods:
1. **urllib** with SSL context (Python built-in)
2. **curl** (macOS/Linux)
3. **requests** (if available)
4. **wget** (Linux)

### File Structure
After successful installation, the browser will be located at:
- **macOS**: `~/Library/Caches/ms-playwright/chromium-{version}/chrome-mac/Chromium.app/Contents/MacOS/Chromium`
- **Windows**: `%LOCALAPPDATA%\ms-playwright\chromium-{version}\chrome-win\chrome.exe`
- **Linux**: `~/.cache/ms-playwright/chromium-{version}/chrome-linux/chrome` 