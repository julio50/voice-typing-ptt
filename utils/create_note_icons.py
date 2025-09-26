#!/usr/bin/env python3
"""Create colored variants of the note.png microphone icon"""

from PIL import Image, ImageOps, ImageEnhance
import os

def create_colored_variants():
    """Create colored variants of the microphone icon"""

    # Load the base icon
    base_path = "/dev/shm/note.png"
    if not os.path.exists(base_path):
        print(f"Error: {base_path} not found!")
        return

    base_img = Image.open(base_path)
    print(f"Original image size: {base_img.size}")

    # Resize to appropriate size for system tray while maintaining quality
    target_size = 64  # Higher resolution for better quality
    if base_img.size != (target_size, target_size):
        base_img = base_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        print(f"Resized to: {base_img.size}")

    # Ensure RGBA mode
    if base_img.mode != 'RGBA':
        base_img = base_img.convert('RGBA')

    # Define colors for different states
    colors = {
        "stopped": (128, 128, 128),    # Gray
        "ready": (0, 170, 0),          # Green
        "recording": (221, 0, 0),      # Red
        "processing": (0, 102, 204)    # Blue
    }

    for state, color in colors.items():
        # Create a copy of the base image
        colored_img = base_img.copy()

        # Convert to grayscale first to remove existing colors
        gray_img = ImageOps.grayscale(colored_img)
        gray_img = gray_img.convert('RGBA')

        # Apply color tint
        # Get the pixels
        pixels = gray_img.load()
        width, height = gray_img.size

        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                if a > 0:  # Only modify non-transparent pixels
                    # Apply color tint based on brightness
                    brightness = r / 255.0  # Use red channel as brightness
                    new_r = int(color[0] * brightness)
                    new_g = int(color[1] * brightness)
                    new_b = int(color[2] * brightness)
                    pixels[x, y] = (new_r, new_g, new_b, a)

        # Save the colored variant
        filename = f"mic_icon_{state}.png"
        gray_img.save(filename)
        print(f"Created {filename} with color {color}")

if __name__ == "__main__":
    create_colored_variants()