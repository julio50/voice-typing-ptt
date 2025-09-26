#!/usr/bin/env python3
"""Create better colored variants of the microphone icon"""

from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import os

def create_better_icons():
    """Create colored variants using a better method"""

    # Load the base icon
    base_path = "/dev/shm/note.png"
    if not os.path.exists(base_path):
        print(f"Error: {base_path} not found!")
        return

    base_img = Image.open(base_path)
    print(f"Original image size: {base_img.size}")

    # Resize to good system tray size while maintaining quality
    target_size = 32  # Good balance of quality and size
    if base_img.size != (target_size, target_size):
        base_img = base_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        print(f"Resized to: {base_img.size}")

    # Ensure RGBA mode
    if base_img.mode != 'RGBA':
        base_img = base_img.convert('RGBA')

    # Define colors for different states (RGB values)
    colors = {
        "stopped": "#808080",    # Gray
        "ready": "#00AA00",      # Green
        "recording": "#DD0000",  # Red
        "processing": "#0066CC"  # Blue
    }

    for state, hex_color in colors.items():
        # Convert hex to RGB
        color = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

        # Create a copy of the base image
        colored_img = base_img.copy()
        pixels = colored_img.load()
        width, height = colored_img.size

        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]

                # Only modify non-transparent pixels
                if a > 0:
                    # Check if pixel is black/dark (the icon lines)
                    brightness = (r + g + b) / 3

                    if brightness < 128:  # Dark pixels (the icon itself)
                        # Replace with our color
                        pixels[x, y] = (*color, a)
                    # Leave light pixels (background) as they are

        # Save the colored variant
        filename = f"tray_icon_{state}.png"
        colored_img.save(filename)
        print(f"Created {filename} with color {hex_color}")

if __name__ == "__main__":
    create_better_icons()