from PIL import Image, ImageDraw

def create_icon(name, size=20, color="#FFFFFF"):
    """Generates simple, crisp geometric vector icons using Pillow."""
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Anti-aliasing scaling factor
    scale = 4
    large_size = size * scale
    l_img = Image.new("RGBA", (large_size, large_size), (255, 255, 255, 0))
    l_draw = ImageDraw.Draw(l_img)
    
    pad = 2 * scale
    
    if name == "play":
        # Sleek play triangle
        points = [
            (pad + 2*scale, pad),
            (large_size - pad, large_size // 2),
            (pad + 2*scale, large_size - pad)
        ]
        l_draw.polygon(points, fill=color)
        
    elif name == "stop":
        # Rounded square
        l_draw.rounded_rectangle(
            [pad + 1*scale, pad + 1*scale, large_size - pad - 1*scale, large_size - pad - 1*scale],
            radius=2*scale, fill=color
        )
        
    elif name == "close":
        # Sleek X
        w = 2 * scale
        l_draw.line([pad, pad, large_size - pad, large_size - pad], fill=color, width=w)
        l_draw.line([large_size - pad, pad, pad, large_size - pad], fill=color, width=w)
        
    elif name == "folder":
        # Folder shape
        l_draw.rounded_rectangle([pad, pad*2, large_size-pad, large_size-pad], radius=1*scale, outline=color, width=2*scale)
        l_draw.polygon([(pad, pad*2), (pad+4*scale, pad*2), (pad+6*scale, pad), (large_size-pad, pad), (large_size-pad, pad*2)], fill=color)

    # Downsample for perfect anti-aliasing
    return l_img.resize((size, size), resample=Image.Resampling.LANCZOS)
