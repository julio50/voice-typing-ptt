#!/usr/bin/env python3
"""Create simple PNG icon files for the system tray"""

from PIL import Image, ImageDraw
import os

def create_icon_files():
    """Create simple colored circle icons as PNG files"""
    size = 22

    icons = {
        "stopped": "#808080",    # Gray
        "ready": "#00AA00",      # Green
        "recording": "#DD0000",  # Red
        "processing": "#0066CC"  # Blue
    }

    for name, color in icons.items():
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw filled circle
        margin = 2
        draw.ellipse([margin, margin, size-margin, size-margin],
                    fill=color, outline="white", width=2)

        # Add small center dot for visibility
        center = size // 2
        draw.ellipse([center-2, center-2, center+2, center+2],
                    fill="white")

        # Save as PNG
        filename = f"icon_{name}.png"
        img.save(filename)
        print(f"Created {filename}")

if __name__ == "__main__":
    create_icon_files()