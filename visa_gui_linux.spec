# -*- mode: python ; coding: utf-8 -*-
# Linux-specific PyInstaller spec file

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from pathlib import Path
import playwright, os

# Icon configuration
try:
    PROJECT_ROOT = Path(__file__).resolve().parent
except NameError:
    PROJECT_ROOT = Path.cwd()

# Try different icon formats for Linux
ICON_ICO = PROJECT_ROOT / "icon.ico"
ICON_PNG = PROJECT_ROOT / "icon.png"

# Use ICO first, fall back to PNG
if ICON_ICO.exists():
    ICON_PATH = ICON_ICO
    print(f"🎨 Using Linux icon: {ICON_PATH}")
elif ICON_PNG.exists():
    ICON_PATH = ICON_PNG
    print(f"🎨 Using Linux icon: {ICON_PATH}")
else:
    ICON_PATH = None
    print(f"⚠️  No suitable icon found (tried: {ICON_ICO}, {ICON_PNG})")
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_PATH) if ICON_PATH else None,  # Linux can use ICO or PNG format
) 