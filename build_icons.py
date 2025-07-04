from PIL import Image
from pathlib import Path
import sys

def create_icons():
    SRC = Path("icon.png")
    DST_ICO = Path("icon.ico")
    DST_ICNS = Path("icon.icns")
    DST_JPEG = Path("icon.jpeg")

    # Check if source file exists
    if not SRC.exists():
        print(f"Error: {SRC} not found!")
        print("Please make sure you have an icon.png file in the current directory.")
        return False

    try:
        # Open the source image
        print(f"Opening {SRC}...")
        img = Image.open(SRC).convert("RGBA")
        
        # Print original image info
        print(f"Original image size: {img.size}")
        print(f"Original image mode: {img.mode}")

        # Save as .ico with multiple sizes for Windows
        print("Creating Windows .ico file...")
        sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
        ico_images = []
        for size in sizes:
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            ico_images.append(resized_img)
        
        ico_images[0].save(DST_ICO, sizes=[(img.width, img.height) for img in ico_images])
        print(f"✓ Created {DST_ICO}")

        # Save as .icns for macOS
        print("Creating macOS .icns file...")
        # For macOS, we need to create a 1024x1024 version
        macos_img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
        macos_img.save(DST_ICNS, format='ICNS')
        print(f"✓ Created {DST_ICNS}")

        # Also save as JPEG for compatibility
        print("Creating JPEG version...")
        jpeg_img = img.convert("RGB")
        jpeg_img.save(DST_JPEG, "JPEG", quality=95)
        print(f"✓ Created {DST_JPEG}")

        print("\n🎉 All icon files created successfully!")
        print(f"  - {DST_ICO} (Windows)")
        print(f"  - {DST_ICNS} (macOS)")
        print(f"  - {DST_JPEG} (JPEG format)")
        
        return True

    except Exception as e:
        print(f"Error creating icons: {e}")
        return False

if __name__ == "__main__":
    success = create_icons()
    sys.exit(0 if success else 1) 