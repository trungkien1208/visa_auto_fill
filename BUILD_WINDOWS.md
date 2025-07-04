# Building Visa GUI Application for Windows

This guide helps you build the Visa GUI application on Windows.

## Prerequisites

### 1. Install Python
- Download Python 3.8+ from [python.org](https://www.python.org/downloads/windows/)
- Make sure to check "Add Python to PATH" during installation
- Verify installation: `python --version`

### 2. Install Required Dependencies
```cmd
# Install required packages
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install Playwright browsers
python -m playwright install
```

## Building the Application

### Option 1: Use the Automated Build Script (Recommended)
```cmd
python build_app.py
```

This script will:
- Automatically detect Windows platform
- Check all requirements
- Optionally install/update browsers
- Build the application using the Windows-specific configuration

### Option 2: Manual Build
```cmd
# Clean build (recommended)
pyinstaller visa_gui_windows.spec --clean

# Or regular build
pyinstaller visa_gui_windows.spec
```

## Windows-Specific Configuration

The `visa_gui_windows.spec` file includes Windows-specific settings:

- **Icon**: Uses `icon.ico` (Windows icon format)
- **Console**: Set to `False` for GUI application (change to `True` for debugging)
- **Browser paths**: Configured for Windows file structure
- **Output**: Creates `dist/visa_gui.exe`

## Troubleshooting

### Common Issues

1. **"playwright not found" error**
   ```cmd
   pip install playwright
   python -m playwright install
   ```

2. **"PyInstaller not found" error**
   ```cmd
   pip install pyinstaller
   ```

3. **Browser executable not found**
   - The application will attempt to auto-install browsers on first run
   - Or manually run: `python -m playwright install chromium`

4. **Icon file missing**
   - Make sure `icon.ico` exists in the project directory
   - The build will continue without an icon if the file is missing

### Windows Defender / Antivirus Issues

Windows Defender might flag the built executable as potentially unwanted software. This is common with PyInstaller builds. To resolve:

1. **Temporary solution**: Add the `dist` folder to Windows Defender exclusions
2. **Permanent solution**: Code sign the executable (requires a code signing certificate)

### Building for Distribution

If you're distributing the application:

1. **Include Visual C++ Redistributable**: Some users might need to install Microsoft Visual C++ Redistributable
2. **Test on clean Windows**: Test the built application on a Windows machine without Python installed
3. **Consider code signing**: For professional distribution, consider getting a code signing certificate

## File Structure After Build

```
dist/
└── visa_gui.exe          # The main executable

build/                     # Temporary build files (can be deleted)
├── visa_gui/
└── ...

*.spec                     # PyInstaller configuration files
```

## Environment Variables

The application uses these environment variables on Windows:

- `PLAYWRIGHT_BROWSERS_PATH`: Automatically set to `%USERPROFILE%\AppData\Local\ms-playwright`
- Browser cache location: `%USERPROFILE%\AppData\Local\ms-playwright\chromium-*`

## Performance Notes

- First run might be slower as it downloads/installs browsers
- Subsequent runs should be faster
- The executable size will be ~150-200MB due to bundled dependencies

## Development Tips

### For debugging, you can:

1. Set `console=True` in `visa_gui_windows.spec` to see console output
2. Run the Python script directly: `python visa_gui.py`
3. Check logs in the application directory

### For faster builds:

1. Use `--noconfirm` flag to skip confirmation prompts
2. Remove `--clean` for incremental builds (faster but may have issues)
3. Use virtual environments to reduce dependency conflicts 