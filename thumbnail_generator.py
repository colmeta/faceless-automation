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
        video_path: str = None,
        text: str = "AI Tools",
        output_path: str = "thumbnail.jpg",
        color_scheme: list = None
    ) -> str:
        """
        Create clickbait-style thumbnail with text overlay and trending elements
        
        Args:
            background_image_path: Path to background image (avatar)
            video_path: Path to video (will extract first frame)
            text: Hook text to overlay
            output_path: Where to save thumbnail
            color_scheme: Optional [(r,g,b), (r,g,b)] gradient colors
        """
        try:
            # Create or load background
            if video_path and os.path.exists(video_path):
                logger.info("📸 Extracting frame from video...")
                img = self._extract_video_frame(video_path)
            elif background_image_path and os.path.exists(background_image_path):
                logger.info(f"📸 Using avatar image: {background_image_path}")
                img = Image.open(background_image_path)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            else:
                # Create gradient background with varied colors
                logger.info("🎨 Creating gradient background...")
                img = self._create_gradient_background(color_scheme)
            
            # Add slight blur for depth (makes text pop)
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
            
            # Add darkening overlay for text readability
            overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 140))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            # Add clickbait text with professional styling
            self._add_clickbait_text(img, text)
            
            # Add trending visual elements
            self._add_visual_elements(img)
            
            # Convert back to RGB and save
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=95)
            
            logger.info(f"✅ Professional thumbnail created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Thumbnail generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_video_frame(self, video_path: str, time_offset: float = 2.0) -> Image:
        """Extract a frame from video at specific time"""
        try:
            from moviepy import VideoFileClip
            clip = VideoFileClip(video_path)
            # Get frame at 2 seconds (usually after intro)
            frame_time = min(time_offset, clip.duration * 0.3)
            frame = clip.get_frame(frame_time)
            clip.close()
            
            # Convert numpy array to PIL Image
            img = Image.fromarray(frame)
            img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            logger.warning(f"⚠️ Video frame extraction failed: {e}")
            # Fallback to gradient
            return self._create_gradient_background()
    
    def _create_gradient_background(self, color_scheme: list = None):
        """Create a vibrant gradient background with varied colors"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Use provided color scheme or default vibrant gradient
        if color_scheme and len(color_scheme) >= 2:
            color1, color2 = color_scheme[0], color_scheme[1]
        else:
            # Default: Purple to Blue gradient
            color1 = (138, 43, 226)  # Purple
            color2 = (30, 144, 255)   # Blue
        
        # Create gradient
        for y in range(self.height):
            r = int(color1[0] + (color2[0] - color1[0]) * y / self.height)
            g = int(color1[1] + (color2[1] - color1[1]) * y / self.height)
            b = int(color1[2] + (color2[2] - color1[2]) * y / self.height)
            draw.rectangle([(0, y), (self.width, y + 1)], fill=(r, g, b))
        
        return img.convert('RGBA')
    
    def _add_clickbait_text(self, img, text):
        """Add clickbait-style text with professional multi-color styling"""
        draw = ImageDraw.Draw(img)
        
        # Try to use bold/impact fonts for clickbait effect
        try:
            font_size = 140 # Larger for impact
            try:
                # Windows fonts
                font = ImageFont.truetype("impact.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("arialbd.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("Arial-Bold.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Split text into lines (max 12 chars per line for thumbnails)
        max_chars_per_line = 12
        words = text.upper().split()  # ALL CAPS for clickbait
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
        
        # Calculate positioning
        line_height = font_size + 30
        total_height = len(lines) * line_height
        y = (self.height - total_height) // 2
        
        # Multi-color text effect (alternating yellow and white)
        colors = [
            (255, 255, 0, 255),   # Yellow
            (255, 255, 255, 255), # White
            (255, 200, 0, 255)    # Orange-Yellow
        ]
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            
            # Thick black outline (stroke effect)
            stroke_width = 8
            for offset_x in range(-stroke_width, stroke_width + 1):
                for offset_y in range(-stroke_width, stroke_width + 1):
                    draw.text((x + offset_x, y + offset_y), line, 
                             fill=(0, 0, 0, 255), font=font)
            
            # Main text with alternating colors
            color = colors[i % len(colors)]
            draw.text((x, y), line, fill=color, font=font)
            
            y += line_height
    
    def _add_visual_elements(self, img):
        """Add trending visual elements (arrows, circles, emojis)"""
        draw = ImageDraw.Draw(img)
        
        # Add corner badge/sticker
        badge_text = "🔥 NEW"
        try:
            badge_font = ImageFont.truetype("arialbd.ttf", 50)
        except:
            badge_font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        badge_width = bbox[2] - bbox[0]
        badge_height = bbox[3] - bbox[1]
        
        # Top-right corner badge
        padding = 15
        badge_x = self.width - badge_width - padding * 3
        badge_y = padding
        
        # Rounded rectangle background
        draw.rounded_rectangle(
            [(badge_x - padding, badge_y - padding), 
             (badge_x + badge_width + padding, badge_y + badge_height + padding * 2)],
            radius=15,
            fill=(255, 50, 50, 255),
            outline=(255, 255, 255, 255),
            width=4
        )
        
        draw.text((badge_x, badge_y), badge_text, fill=(255, 255, 255, 255), font=badge_font)
        
        # Add subtle arrow or pointer (optional - simpler approach)
        # You could add PIL drawing of arrows here if desired


if __name__ == "__main__":
    # Test the thumbnail generator
    logging.basicConfig(level=logging.INFO)
    
    gen = ThumbnailGenerator()
    gen.create_thumbnail(
        text="This Changed Everything",
        output_path="test_thumbnail.jpg"
    )
    print("Test thumbnail created!")
