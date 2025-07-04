# visa_gui.spec
# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller build recipe for the Visa-GUI application **without Playwright browsers bundled**.

Users will download Chromium from the internet when needed.
This significantly reduces the application size.
"""

# --- disable PyInstaller's automatic ad‑hoc codesigning on macOS ------------
import os; os.environ["PYINSTALLER_CODESIGN_DISABLE"] = "1"

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# ---------------------------------------------------------------------------
# Compatibility shim for older PyInstaller versions without `Tree`
# ---------------------------------------------------------------------------
try:
    from PyInstaller.utils.hooks import Tree  # PyInstaller ≥ 5.0
except ImportError:  # pragma: no cover – fallback for very old versions
    def Tree(src, prefix=None, excludes=(), typecode="DATA"):
        """Return a TOC-style list that mimics PyInstaller's `Tree` helper.

        Each entry is a 2-tuple ``(src_name, dest_name)`` so we can
        mark *every* file in ``src`` as plain data (``typecode='DATA'``).
        The implementation is minimal but sufficient for our purpose here and returns 2-item
        tuples (``src_name``, ``dest_name``) expected by PyInstaller ≥ 6.14.
        """

        src = Path(src).resolve()
        toc = []
        for path in src.rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(src)
            if any(path.match(pat) or rel.match(pat) for pat in excludes):
                continue
            dest = Path(prefix or "").joinpath(rel).as_posix()
            # Return a *pair* (src, dest); PyInstaller marks data files itself.
            toc.append((str(path), dest))
        return toc

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
try:
    # When the spec file is executed directly (e.g. `python visa_gui.spec`) the
    # magic variable ``__file__`` is available.  When PyInstaller loads the
    # spec via ``exec()`` it *removes* the variable, so we fall back to the
    # current working directory in that situation.
    PROJECT_ROOT = Path(__file__).resolve().parent  # <repo-root>
except NameError:  # __file__ not defined
    PROJECT_ROOT = Path.cwd()

RUNTIME_HOOK = PROJECT_ROOT / "playwright_browsers_env.py"  # created next to this spec
ICON_PATH = PROJECT_ROOT / "icon.icns"  # App icon

# ---------------------------------------------------------------------------
# Data files (no browser cache - users download from internet)
# ---------------------------------------------------------------------------
datas = []
print("📦 Building without bundled browsers - users will download from internet")

# Check if icon exists and provide feedback
if ICON_PATH.exists():
    print(f"🎨 Using icon: {ICON_PATH}")
else:
    print(f"⚠️  Icon not found at: {ICON_PATH}")
    print("   The app will be built without a custom icon")

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    ["visa_gui.py"],                # entry-point script
    pathex=[str(PROJECT_ROOT)],     # search path for local imports
    binaries=[],
    datas=datas,
    hiddenimports=list(collect_submodules("playwright")),
    hookspath=[],
    runtime_hooks=[str(RUNTIME_HOOK)],
    hooksconfig={},
    excludes=[],
    noarchive=False,
)

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
pyz = PYZ(a.pure)

# Create a proper macOS app bundle
app = BUNDLE(
    exe := EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name="visa_gui",
        debug=False,
        upx=False,          # set to False if UPX unavailable
        console=False,      # Set to False for a proper macOS app bundle
        icon=str(ICON_PATH) if ICON_PATH.exists() else None,  # Use icon if it exists
        # macOS: disable automatic adhoc code-signing of every embedded Mach-O
        # binary – signing Chromium's nested frameworks fails.  We leave the app
        # unsigned; you can post-sign the final bundle later if desired.
        codesign_identity=None,
        entitlements_file=None,
    ),
    name="visa_gui.app",
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,  # Use icon for the app bundle
    bundle_identifier="com.visa.autofill.app",
    info_plist={
        'CFBundleName': 'Visa Autofill',
        'CFBundleDisplayName': 'Visa Autofill',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',  # macOS 10.15 (Catalina) or later
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
)