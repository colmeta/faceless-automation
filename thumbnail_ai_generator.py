#!/usr/bin/env python3
"""
🎨 thumbnail_ai_generator.py - SAVE AS THIS FILENAME
====================================================
AI Thumbnail Generator - Professional System

This is a STANDALONE file that you need to:
1. Save as: thumbnail_ai_generator.py
2. Place in same folder as master_automation.py
3. It will be imported and used automatically

✅ Multiple AI Services (Stability AI, Hugging Face, DALL-E)
✅ Smart fallback chain
✅ Viral thumbnail templates
✅ Clickbait text overlays
✅ Free tier optimized
"""

import os
import sys
import io
import json
import logging
import requests
import base64
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== AI THUMBNAIL GENERATOR ====================
class AIThumbnailGenerator:
    """
    Professional AI Thumbnail Generator
    Priority: Stability AI → Hugging Face → DALL-E → Fallback
    """
    
    def __init__(self):
        # API Keys
        self.stability_key = os.getenv('STABILITY_API_KEY', '').strip()
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN', '').strip()
        self.openai_key = os.getenv('OPENAI_API_KEY', '').strip()
        
        # Track usage for free tiers
        self.stability_credits = 150  # Free tier monthly
        self.hf_calls = 0
        self.hf_monthly_limit = 1000
        
        logger.info("🎨 AI Thumbnail Generator initialized")
        logger.info(f"   Stability AI: {'✅' if self.stability_key else '❌'}")
        logger.info(f"   Hugging Face: {'✅' if self.hf_token else '❌'}")
        logger.info(f"   OpenAI DALL-E: {'✅' if self.openai_key else '❌'}")
    
    def generate_thumbnail(
        self, 
        hook: str, 
        topic: str = "AI technology",
        output_path: str = "thumbnail.jpg",
        style: str = "viral"
    ) -> Optional[str]:
        """
        Generate AI thumbnail with smart fallback chain
        
        Args:
            hook: Video hook/title text
            topic: Video topic for visual context
            output_path: Where to save thumbnail
            style: viral, professional, minimal, shock
        
        Returns:
            Path to generated thumbnail or None
        """
        
        logger.info(f"🎨 Generating AI thumbnail: '{hook[:50]}...'")
        logger.info(f"   Topic: {topic}, Style: {style}")
        
        # Create visual prompt
        visual_prompt = self._create_thumbnail_prompt(hook, topic, style)
        
        thumbnail_path = None
        
        # 🥇 PRIORITY 1: Stability AI (Best quality, 150 free/month)
        if self.stability_key and self.stability_credits > 0:
            thumbnail_path = self._generate_stability(visual_prompt, output_path)
            if thumbnail_path:
                self.stability_credits -= 1
                logger.info(f"✅ Stability AI thumbnail ({self.stability_credits} credits left)")
                return self._add_text_overlay(thumbnail_path, hook, style)
        
        # 🥈 PRIORITY 2: Hugging Face (1000 free/month)
        if self.hf_token and self.hf_calls < self.hf_monthly_limit:
            thumbnail_path = self._generate_huggingface(visual_prompt, output_path)
            if thumbnail_path:
                self.hf_calls += 1
                logger.info(f"✅ Hugging Face thumbnail ({self.hf_calls}/{self.hf_monthly_limit})")
                return self._add_text_overlay(thumbnail_path, hook, style)
        
        # 🥉 PRIORITY 3: OpenAI DALL-E (Paid but reliable)
        if self.openai_key:
            thumbnail_path = self._generate_dalle(visual_prompt, output_path)
            if thumbnail_path:
                logger.info("✅ DALL-E thumbnail generated")
                return self._add_text_overlay(thumbnail_path, hook, style)
        
        # 🏁 FALLBACK: Beautiful gradient with text
        logger.warning("⚠️ All AI services unavailable, using premium fallback...")
        return self._generate_premium_fallback(hook, topic, output_path, style)
    
    def _create_thumbnail_prompt(self, hook: str, topic: str, style: str) -> str:
        """Create AI prompt for thumbnail generation"""
        
        # Extract key concepts from hook and topic
        keywords = self._extract_keywords(hook, topic)
        
        # Style-specific templates
        style_prompts = {
            'viral': 'dramatic lighting, vibrant colors, eye-catching composition, trending style, high energy',
            'professional': 'clean minimalist design, corporate aesthetic, professional lighting, modern tech',
            'shock': 'shocking expression, dramatic contrast, intense colors, surprise element',
            'minimal': 'clean simple background, minimal design, single focal point, elegant composition'
        }
        
        style_desc = style_prompts.get(style, style_prompts['viral'])
        
        # Visual concept based on topic
        topic_visuals = {
            'ai': 'futuristic AI interface, holographic displays, neural network visualization, glowing circuits',
            'productivity': 'organized workspace, productivity dashboard, efficient workflow, clean desk setup',
            'technology': 'cutting-edge technology, innovation lab, modern devices, sleek interfaces',
            'business': 'professional office environment, growth charts, success metrics, entrepreneur workspace',
            'social media': 'social network visualization, viral content, engagement metrics, influencer setup',
            'money': 'financial growth, wealth building, profit charts, success indicators',
            'automation': 'automated systems, robotic efficiency, smart technology, workflow automation'
        }
        
        # Match topic to visual
        visual_concept = topic_visuals.get('ai', topic_visuals['ai'])  # Default to AI
        for key in topic_visuals:
            if key in topic.lower():
                visual_concept = topic_visuals[key]
                break
        
        # Combine into professional prompt
        prompt = f"""Professional YouTube thumbnail design: {visual_concept}, {style_desc}, 
ultra high quality 4K, perfect composition, YouTube thumbnail style, 
1280x720 resolution, attention-grabbing, cinematic lighting, 
professional photography, trending on YouTube"""
        
        logger.info(f"   Prompt: {prompt[:80]}...")
        return prompt
    
    def _extract_keywords(self, hook: str, topic: str) -> List[str]:
        """Extract key visual concepts"""
        text = f"{hook} {topic}".lower()
        
        concepts = {
            'ai', 'technology', 'productivity', 'business', 'money', 'growth',
            'automation', 'social', 'viral', 'trending', 'shocking', 'amazing'
        }
        
        found = [word for word in concepts if word in text]
        return found if found else ['technology']
    
    def _generate_stability(self, prompt: str, output_path: str) -> Optional[str]:
        """Generate with Stability AI (SDXL)"""
        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text_prompts": [{"text": prompt, "weight": 1}],
                "cfg_scale": 7,
                "height": 720,
                "width": 1280,
                "samples": 1,
                "steps": 30
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                image_b64 = data['artifacts'][0]['base64']
                
                # Decode and save
                image_data = base64.b64decode(image_b64)
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                if os.path.exists(output_path):
                    return output_path
            else:
                logger.warning(f"Stability API error: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"Stability AI failed: {e}")
        
        return None
    
    def _generate_huggingface(self, prompt: str, output_path: str) -> Optional[str]:
        """Generate with Hugging Face (FLUX or Stable Diffusion)"""
        try:
            # Use FLUX.1-schnell (fast and free)
            api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "width": 1280,
                    "height": 720,
                    "num_inference_steps": 4  # Fast for schnell model
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                if os.path.exists(output_path):
                    return output_path
            else:
                logger.warning(f"Hugging Face error: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"Hugging Face failed: {e}")
        
        return None
    
    def _generate_dalle(self, prompt: str, output_path: str) -> Optional[str]:
        """Generate with OpenAI DALL-E"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_key)
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",  # Closest to 16:9
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download
            img_response = requests.get(image_url, timeout=30)
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            
            # Crop to exact size
            img = Image.open(output_path)
            img = img.resize((1280, 720), Image.Resampling.LANCZOS)
            img.save(output_path)
            
            return output_path
        
        except Exception as e:
            logger.warning(f"DALL-E failed: {e}")
        
        return None
    
    def _add_text_overlay(self, image_path: str, text: str, style: str) -> str:
        """Add professional text overlay to generated image"""
        try:
            img = Image.open(image_path).convert('RGBA')
            
            # Add darkening overlay for text readability
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))
            img = Image.alpha_composite(img, overlay)
            
            # Add text
            draw = ImageDraw.Draw(img)
            
            # Get font
            try:
                font_size = 140 if len(text) < 30 else 100
                font = ImageFont.truetype("impact.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("arialbd.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Split text into lines
            words = text.upper().split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > 1100:  # Max width
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    current_line.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw text with outline
            y = 200 if len(lines) <= 2 else 150
            
            for line in lines[:3]:  # Max 3 lines
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (1280 - text_width) // 2
                
                # Thick black outline
                for offset in range(-8, 9, 2):
                    for offset_y in range(-8, 9, 2):
                        draw.text((x + offset, y + offset_y), line, 
                                 fill=(0, 0, 0, 255), font=font)
                
                # Main text (yellow/white alternating)
                colors = [(255, 255, 0, 255), (255, 255, 255, 255)]
                color = colors[lines.index(line) % 2]
                draw.text((x, y), line, fill=color, font=font)
                
                y += font_size + 20
            
            # Add badge
            self._add_badge(draw, img.size)
            
            # Save
            img = img.convert('RGB')
            img.save(image_path, 'JPEG', quality=95)
            
            return image_path
        
        except Exception as e:
            logger.error(f"Text overlay failed: {e}")
            return image_path
    
    def _add_badge(self, draw, size):
        """Add trending badge"""
        badge_text = "🔥 NEW"
        try:
            badge_font = ImageFont.truetype("arialbd.ttf", 40)
        except:
            badge_font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        badge_w = bbox[2] - bbox[0]
        badge_h = bbox[3] - bbox[1]
        
        padding = 15
        x = size[0] - badge_w - padding * 3
        y = padding
        
        # Rounded rectangle
        draw.rounded_rectangle(
            [(x - padding, y - padding), 
             (x + badge_w + padding, y + badge_h + padding * 2)],
            radius=15,
            fill=(255, 50, 50, 255),
            outline=(255, 255, 255, 255),
            width=3
        )
        
        draw.text((x, y), badge_text, fill=(255, 255, 255, 255), font=badge_font)
    
    def _generate_premium_fallback(
        self, 
        hook: str, 
        topic: str, 
        output_path: str, 
        style: str
    ) -> str:
        """Generate premium gradient fallback thumbnail"""
        
        # Create high-quality gradient
        img = Image.new('RGB', (1280, 720))
        draw = ImageDraw.Draw(img)
        
        # Style-based color schemes
        color_schemes = {
            'viral': [(255, 0, 110), (138, 43, 226), (0, 170, 255)],  # Pink-Purple-Blue
            'professional': [(0, 123, 255), (40, 167, 69), (255, 193, 7)],  # Blue-Green-Yellow
            'shock': [(255, 0, 0), (255, 100, 0), (255, 200, 0)],  # Red-Orange-Yellow
            'minimal': [(70, 70, 90), (120, 120, 140), (170, 170, 190)]  # Gray gradient
        }
        
        colors = color_schemes.get(style, color_schemes['viral'])
        
        # Multi-color gradient
        for y in range(720):
            progress = y / 720
            
            if progress < 0.5:
                ratio = progress * 2
                r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
                g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
                b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
            else:
                ratio = (progress - 0.5) * 2
                r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * ratio)
                g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * ratio)
                b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * ratio)
            
            draw.rectangle([(0, y), (1280, y + 1)], fill=(r, g, b))
        
        # Add noise/texture
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
        
        img.save(output_path, 'JPEG', quality=95)
        
        # Add text overlay
        return self._add_text_overlay(output_path, hook, style)


# ==================== INTEGRATION MODULE ====================
def integrate_into_automation():
    """
    Integration guide for master_automation.py
    """
    
    integration_code = '''
# Add to master_automation.py after video generation (around line 1158)

# Import at top of file
try:
    from thumbnail_ai_generator import AIThumbnailGenerator
    THUMBNAIL_AI_AVAILABLE = True
    logger.info("✅ AI Thumbnail Generator available")
except ImportError:
    THUMBNAIL_AI_AVAILABLE = False
    logger.warning("⚠️ AI Thumbnail Generator not available")

# In MasterOrchestrator.run_daily_automation() method:
# After: self.video_composer.generate_voice_and_video(script, output_path)

# Generate AI Thumbnail
thumbnail_path = None
if THUMBNAIL_AI_AVAILABLE:
    try:
        logger.info("🎨 Generating AI thumbnail...")
        thumbnail_gen = AIThumbnailGenerator()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        thumbnail_path = f"faceless_empire/thumbnails/thumb_{timestamp}.jpg"
        os.makedirs("faceless_empire/thumbnails", exist_ok=True)
        
        # Determine style based on hook
        hook_lower = script['hook'].lower()
        if 'amazing' in hook_lower or 'insane' in hook_lower:
            style = 'shock'
        elif 'professional' in hook_lower or 'business' in hook_lower:
            style = 'professional'
        else:
            style = 'viral'
        
        thumbnail_path = thumbnail_gen.generate_thumbnail(
            hook=script['hook'],
            topic=script.get('topic', 'AI technology'),
            output_path=thumbnail_path,
            style=style
        )
        
        if thumbnail_path:
            logger.info(f"✅ AI Thumbnail generated: {thumbnail_path}")
        else:
            logger.warning("⚠️ Thumbnail generation failed")
        
    except Exception as e:
        logger.error(f"❌ Thumbnail generation error: {e}")
        thumbnail_path = None

# Pass thumbnail to YouTube uploader
if self.youtube_uploader and thumbnail_path:
    upload_result = self.youtube_uploader.upload_shorts_optimized(
        video_path=output_path,
        hook=script['hook'],
        topic=script['topic'],
        hashtags=hashtags,
        affiliate_link=description,
        thumbnail_path=thumbnail_path  # NEW: Add this parameter
    )
'''
    
    return integration_code


# ==================== YOUTUBE UPLOADER ENHANCEMENT ====================
def enhance_youtube_uploader():
    """
    Enhancement for youtube_auto_uploader.py to support thumbnails
    """
    
    enhancement_code = '''
# Add to youtube_auto_uploader.py in upload_video() method

def upload_video(
    self,
    video_path: str,
    title: str,
    description: str,
    tags: list = None,
    category: str = "28",
    privacy: str = "public",
    made_for_kids: bool = False,
    thumbnail_path: str = None  # NEW PARAMETER
) -> Dict:
    """Upload video to YouTube with optional thumbnail"""
    
    # ... existing upload code ...
    
    # After video upload succeeds, set thumbnail
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            logger.info(f"📸 Uploading thumbnail...")
            
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            
            logger.info(f"✅ Thumbnail uploaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Thumbnail upload failed: {e}")
    
    # ... rest of method ...
'''
    
    return enhancement_code


# ==================== TEST FUNCTION ====================
def test_ai_thumbnail_generator():
    """Test the AI thumbnail generator"""
    
    print("\n" + "="*60)
    print("🧪 TESTING AI THUMBNAIL GENERATOR")
    print("="*60)
    
    generator = AIThumbnailGenerator()
    
    test_cases = [
        {
            'hook': 'This AI Tool Changed Everything',
            'topic': 'AI automation',
            'style': 'viral',
            'output': 'test_thumb_viral.jpg'
        },
        {
            'hook': 'The Professional Workflow',
            'topic': 'business productivity',
            'style': 'professional',
            'output': 'test_thumb_professional.jpg'
        },
        {
            'hook': 'You Won\'t Believe This',
            'topic': 'shocking technology',
            'style': 'shock',
            'output': 'test_thumb_shock.jpg'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['style'].upper()} style")
        print(f"   Hook: {test['hook']}")
        
        result = generator.generate_thumbnail(
            hook=test['hook'],
            topic=test['topic'],
            output_path=test['output'],
            style=test['style']
        )
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / 1024
            print(f"   ✅ Generated: {result} ({file_size:.1f} KB)")
        else:
            print(f"   ❌ Failed to generate")
    
    print("\n" + "="*60)
    print("✅ TESTS COMPLETE")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Check generated thumbnails")
    print("2. Add API keys to .env:")
    print("   STABILITY_API_KEY=your_key")
    print("   HUGGINGFACE_TOKEN=your_token")
    print("   OPENAI_API_KEY=your_key")
    print("3. Integrate into master_automation.py (see integration_code)")
    print("4. Deploy and watch CTR improve! 📈")


if __name__ == "__main__":
    test_ai_thumbnail_generator()
