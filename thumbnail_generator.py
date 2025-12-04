"""
Thumbnail Generator for YouTube Shorts
Creates eye-catching thumbnails with text overlays
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import logging

logger = logging.getLogger(__name__)

class ThumbnailGenerator:
    """Generate eye-catching thumbnails for YouTube Shorts"""
    
    def __init__(self):
        self.width = 1280
        self.height = 720  # YouTube standard thumbnail size
    
    def create_thumbnail(
        self, 
        background_image_path: str = None,
        text: str = "AI Tools",
        output_path: str = "thumbnail.jpg"
    ) -> str:
        """
        Create thumbnail with text overlay
        
        Args:
            background_image_path: Path to background image (avatar or video frame)
            text: Text to overlay
            output_path: Where to save thumbnail
        """
        try:
            # Create or load background
            if background_image_path and os.path.exists(background_image_path):
                img = Image.open(background_image_path)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            else:
                # Create gradient background
                img = self._create_gradient_background()
            
            # Add slight blur for depth
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            
            # Create drawing context
            draw = ImageDraw.Draw(img)
            
            # Add dark overlay for text readability
            overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 120))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            # Add text
            self._add_text(img, text)
            
            # Convert back to RGB and save
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=95)
            
            logger.info(f"✅ Thumbnail created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Thumbnail generation failed: {e}")
            return None
    
    def _create_gradient_background(self):
        """Create a vibrant gradient background"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Create purple to blue gradient
        for y in range(self.height):
            r = int(138 + (30 - 138) * y / self.height)
            g = int(43 + (144 - 43) * y / self.height)
            b = int(226 + (255 - 226) * y / self.height)
            draw.rectangle([(0, y), (self.width, y + 1)], fill=(r, g, b))
        
        return img.convert('RGBA')
    
    def _add_text(self, img, text):
        """Add text overlay with styling"""
        draw = ImageDraw.Draw(img)
        
        # Try to use a bold font, fallback to default
        try:
            # Try system fonts
            font_size = 120
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("Arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Wrap text if too long
        max_chars_per_line = 15
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= max_chars_per_line:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate total text height
        line_height = font_size + 20
        total_height = len(lines) * line_height
        
        # Start position (centered vertically)
        y = (self.height - total_height) // 2
        
        # Draw each line
        for line in lines:
            # Get text bounding box
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            
            # Draw text shadow
            shadow_offset = 4
            draw.text((x + shadow_offset, y + shadow_offset), line, 
                     fill=(0, 0, 0, 200), font=font)
            
            # Draw main text
            draw.text((x, y), line, fill=(255, 255, 255, 255), font=font)
            
            y += line_height
        
        # Add emoji or badge
        badge_text = "🔥 AI"
        badge_font_size = 60
        try:
            badge_font = ImageFont.truetype("arial.ttf", badge_font_size)
        except:
            badge_font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        badge_width = bbox[2] - bbox[0]
        badge_x = self.width - badge_width - 40
        badge_y = 40
        
        # Badge background
        draw.rectangle(
            [(badge_x - 20, badge_y - 10), (badge_x + badge_width + 20, badge_y + badge_font_size + 10)],
            fill=(255, 50, 50, 200),
            outline=(255, 255, 255, 255),
            width=3
        )
        
        # Badge text
        draw.text((badge_x, badge_y), badge_text, fill=(255, 255, 255, 255), font=badge_font)


if __name__ == "__main__":
    # Test the thumbnail generator
    logging.basicConfig(level=logging.INFO)
    
    gen = ThumbnailGenerator()
    gen.create_thumbnail(
        text="This Changed Everything",
        output_path="test_thumbnail.jpg"
    )
    print("Test thumbnail created!")
