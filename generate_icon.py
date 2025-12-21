from PIL import Image, ImageDraw
import math

def create_icon(path):
    size = 256
    # Create image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background: Rounded Rectangle with Purple Gradient
    # Manually simulating gradient by drawing concentric shapes or just a solid cool purple for simplicity + slickness
    # "Bora" means Purple. Let's use a rich violet/purple.
    
    # Modern "Squircle" shape
    rect_margin = 16
    rect_coords = [rect_margin, rect_margin, size - rect_margin, size - rect_margin]
    corner_radius = 60
    
    # Base color: #8A2BE2 (BlueViolet) to #9400D3 (DarkViolet)
    # Let's do a simple vertical gradient
    for y in range(rect_margin, size - rect_margin):
        # Calculate color interpolation
        ratio = (y - rect_margin) / (size - 2 * rect_margin)
        
        # Color 1: #9B59B6 (Wisteria - Lighter Purple) -> (155, 89, 182)
        # Color 2: #8E44AD (Wisteria - Darker Purple) -> (142, 68, 173)
        # Taking a slightly more vibrant "Bora" gradient
        # Top: #B15EFF (Neon Purple-ish) -> (177, 94, 255)
        # Bot: #5D00B8 (Deep Purple) -> (93, 0, 184)
        
        r = int(177 + (93 - 177) * ratio)
        g = int(94 + (0 - 94) * ratio)
        b = int(255 + (184 - 255) * ratio)
        
        # Draw line limited by rounded rect mask?
        # Simpler: just fill solid Deep Purple for now, gradients are hard to clip in pure PIL without numpy
        # Let's stick to a nice solid vibrant purple
        pass

    # Draw solid rounded rectangle
    purple_color = (138, 43, 226) # BlueViolet
    draw.rounded_rectangle(rect_coords, radius=corner_radius, fill=purple_color)

    # 2. Icon Symbol: Crop/Capture Frame
    # White lines
    stroke_width = 20
    white = (255, 255, 255, 240)
    
    margin = 70
    # Top-Left corner
    draw.line([(margin, margin), (margin + 60, margin)], fill=white, width=stroke_width)
    draw.line([(margin, margin - stroke_width/2), (margin, margin + 60)], fill=white, width=stroke_width)
    
    # Bottom-Right corner
    draw.line([(size-margin-60, size-margin), (size-margin, size-margin)], fill=white, width=stroke_width)
    draw.line([(size-margin, size-margin-60), (size-margin, size-margin+stroke_width/2)], fill=white, width=stroke_width)

    # Center circle (Lens)
    center = size // 2
    radius = 35
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], outline=white, width=stroke_width)
    
    # Add a "Flash" dot
    dot_radius = 6
    dot_x = center + 15
    dot_y = center - 15
    # draw.ellipse([dot_x-dot_radius, dot_y-dot_radius, dot_x+dot_radius, dot_y+dot_radius], fill=white)

    img.save(path)
    print(f"Icon saved to {path}")

if __name__ == "__main__":
    create_icon("assets/icon.png")
