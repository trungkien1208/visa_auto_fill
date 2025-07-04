"""Runtime hook executed by PyInstaller.

This file is executed when the bundle starts. Since browsers are not bundled
with the application, users will download Chromium from the internet when needed.
"""

import os
from pathlib import Path

# Since browsers are not bundled, we don't set PLAYWRIGHT_BROWSERS_PATH
# The application will handle browser download and installation automatically
# when needed through the ensure_browsers_available() function.

print("🌐 Browser download mode: Chromium will be downloaded from internet when needed") 