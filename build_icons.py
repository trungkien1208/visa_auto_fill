from PIL import Image
from pathlib import Path

SRC = Path("icon.jpeg")
DST_ICO = Path("icon.ico")
DST_ICNS = Path("icon.icns")

# Open the source image
img = Image.open(SRC).convert("RGBA")

# Save as .ico with multiple sizes for Windows
sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
img.save(DST_ICO, sizes=sizes)
print(f"Created {DST_ICO}")

# Save as .icns for macOS (requires pillow-icns)
img.resize((1024, 1024), Image.Resampling.LANCZOS).save(DST_ICNS)
print(f"Created {DST_ICNS}") 