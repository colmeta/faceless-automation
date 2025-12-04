#!/usr/bin/env python3
"""
Extract individual avatar images from portfolio collage
"""
from PIL import Image
import os

def extract_avatar_images(portfolio_path: str, output_dir: str = "avatars"):
    """
    Extract individual avatar images from a portfolio collage
    Assumes a grid layout (2x5, 3x4, etc.)
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Load the portfolio image
        img = Image.open(portfolio_path)
        width, height = img.size
        
        print(f"📐 Portfolio size: {width}x{height}")
        
        # Try to detect grid layout by analyzing the image
        # Common layouts: 2x5, 3x4, 4x3, 5x2 for 10 images
        possible_grids = [(2, 5), (5, 2), (3, 4), (4, 3), (1, 10), (10, 1)]
        
        print("\n🔍 Attempting to extract images...")
        print("Please manually verify the grid layout if extraction fails.\n")
        
        for cols, rows in possible_grids:
            if cols * rows == 10:
                print(f"Trying {cols}x{rows} grid...")
                
                cell_width = width // cols
                cell_height = height // rows
                
                count = 0
                for row in range(rows):
                    for col in range(cols):
                        left = col * cell_width
                        top = row * cell_height
                        right = left + cell_width
                        bottom = top + cell_height
                        
                        # Crop the cell
                        cell_img = img.crop((left, top, right, bottom))
                        
                        # Save the cropped image
                        output_path = os.path.join(output_dir, f"avatar_{count+1:02d}.jpg")
                        cell_img.save(output_path, "JPEG", quality=95)
                        count += 1
                        print(f"✅ Extracted: {output_path}")
                
                print(f"\n🎉 Extracted {count} images using {cols}x{rows} grid")
                return True
        
        print("❌ Could not automatically detect grid layout.")
        print("Please manually split the images or provide individual files.")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    portfolio_file = "image portifolio.png"
    
    if os.path.exists(portfolio_file):
        extract_avatar_images(portfolio_file)
    else:
        print(f"❌ {portfolio_file} not found!")
