# -*- mode: python ; coding: utf-8 -*-
# Windows-specific PyInstaller spec file

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from pathlib import Path
import playwright, os

# Icon configuration
try:
    PROJECT_ROOT = Path(__file__).resolve().parent
except NameError:
    PROJECT_ROOT = Path.cwd()

ICON_PATH = PROJECT_ROOT / "icon.ico"  # Windows icon

# Check if icon exists and provide feedback
if ICON_PATH.exists():
    print(f"🎨 Using Windows icon: {ICON_PATH}")
else:
    print(f"⚠️  Icon not found at: {ICON_PATH}")
    print("   The app will be built without a custom icon")

_playwright_hiddenimports = collect_submodules('playwright')
_playwright_datas        = collect_data_files('playwright')

a = Analysis(
    ['visa_gui.py'],
    pathex=[],
    binaries=[],
    datas=_playwright_datas,
    hiddenimports=['playwright', 'playwright.sync_api'] + _playwright_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='visa_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,  # Windows uses .ico format
) 