#!/usr/bin/env python3
"""Create microphone icon variants with different colors"""

from PIL import Image, ImageDraw, ImageOps
import os

def create_mic_icons():
    """Create microphone icons with different colors for different states"""

    # Create base microphone icon (simplified version of the provided design)
    size = 22

    def draw_microphone(draw, color, bg_color=(0, 0, 0, 0)):
        # Chat bubble background
        bubble_margin = 1
        draw.rounded_rectangle([bubble_margin, bubble_margin, size-bubble_margin-6, size-bubble_margin],
                             radius=3, fill="white", outline=color, width=2)

        # Microphone icon inside bubble
        mic_x = size//2 - 7
        mic_y = size//2 - 4

        # Mic capsule
        draw.rounded_rectangle([mic_x+2, mic_y, mic_x+6, mic_y+6],
                             radius=2, fill=color, outline=color)

        # Mic stand
        draw.rectangle([mic_x+3, mic_y+6, mic_x+5, mic_y+9], fill=color)

        # Mic base
        draw.rectangle([mic_x+1, mic_y+9, mic_x+7, mic_y+10], fill=color)

        # Circle background for mic symbol
        circle_x = size - 11
        circle_y = size - 11
        draw.ellipse([circle_x, circle_y, circle_x+10, circle_y+10],
                    fill="white", outline=color, width=2)

        # Small microphone in circle
        small_mic_x = circle_x + 3
        small_mic_y = circle_y + 2
        draw.rounded_rectangle([small_mic_x, small_mic_y, small_mic_x+4, small_mic_y+4],
                             radius=1, fill=color)
        draw.rectangle([small_mic_x+1, small_mic_y+4, small_mic_x+3, small_mic_y+6], fill=color)
        draw.rectangle([small_mic_x, small_mic_y+6, small_mic_x+4, small_mic_y+7], fill=color)

    # Create icons with different colors
    icons = {
        "stopped": "#808080",    # Gray
        "ready": "#00AA00",      # Green
        "recording": "#DD0000",  # Red
        "processing": "#0066CC"  # Blue
    }

    for name, color in icons.items():
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw_microphone(draw, color)

        # Save as PNG
        filename = f"icon_{name}.png"
        img.save(filename)
        print(f"Created {filename} with color {color}")

if __name__ == "__main__":
    create_mic_icons()