#!/usr/bin/env python3
"""
🎬 AI VIDEO GENERATION MANAGER
==================================
Inspired by: 4.5M Instagram followers in 3 weeks! 🔥

STRATEGY: Instead of generic B-roll, generate contextual AI videos
that show EXACTLY what you're talking about (Instagram viral formula)

FREE AI VIDEO SERVICES:
1. Leonardo.ai Motion - 150 free generations/month ⭐ BEST
2. Runway Gen-2 - $12 free credits (professional quality)
3. Stable Video Diffusion - Open source (local)
4. Animated fallback - Always works

WHY THIS WORKS:
✅ Shows what you talk about (contextual)
✅ Higher retention (visual storytelling)
✅ Unique content (not stock footage)
✅ Viral potential (like Instagram!)
"""

import os
import sys
import logging
import requests
import time
import subprocess
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIVideoGenerator:
    """Generate contextual AI videos instead of generic B-roll"""
    
    def __init__(self):
        # API keys from environment
        self.leonardo_key = os.getenv('LEONARDO_API_KEY', '').strip()
        self.runway_key = os.getenv('RUNWAY_API_KEY', '').strip()
        
        # Track usage to stay within free tiers
        self.leonardo_credits_used = 0
        self.leonardo_monthly_limit = 150  # Free tier
        
        logger.info("🎬 AI Video Generator initialized")
        logger.info(f"📊 Leonardo API: {'✅ Available' if self.leonardo_key else '❌ Not configured'}")
        logger.info(f"📊 Runway API: {'✅ Available' if self.runway_key else '❌ Not configured'}")
        
    def generate_contextual_video(
        self,
        topic: str,
        narration: str,
        duration: float = 10.0,
        output_path: str = "temp/ai_video.mp4"
    ) -> Optional[str]:
        """
        Generate AI video that matches the narration content
        Like your Instagram - showing what you talk about!
        
        Args:
            topic: Main topic (e.g., "AI productivity tools")
            narration: What the video is about
            duration: Target duration in seconds
            output_path: Where to save video
        
        Returns:
            Path to generated video or None if failed
        """
        
        # Extract visual concepts from narration
        visual_prompt = self._create_visual_prompt(topic, narration)
        
        logger.info(f"🎨 Generating AI video: '{visual_prompt[:60]}...'")
        
        video_path = None
        
        # Try services in order of quality/cost
        
        # 1. Leonardo.ai Motion (Best free tier)
        if self.leonardo_key and self.leonardo_credits_used < self.leonardo_monthly_limit:
            video_path = self._generate_leonardo_motion(visual_prompt, duration, output_path)
            if video_path:
                self.leonardo_credits_used += 1
                logger.info(f"✅ Leonardo video generated ({self.leonardo_credits_used}/{self.leonardo_monthly_limit} used)")
                return video_path
        
        # 2. Runway Gen-2 (Professional quality, $12 free credits)
        if self.runway_key:
            video_path = self._generate_runway_gen2(visual_prompt, duration, output_path)
            if video_path:
                return video_path
        
        # 3. Fallback: Animated gradient video
        logger.warning("⚠️ All AI video APIs unavailable, using animated fallback...")
        video_path = self._generate_animated_fallback(visual_prompt, duration, output_path)
        
        return video_path
    
    def _create_visual_prompt(self, topic: str, narration: str) -> str:
        """
        Extract visual concepts from narration
        Like Instagram - show what you're talking about
        """
        
        # Map keywords to cinematic visual concepts
        visual_keywords = {
            'ai': 'futuristic AI holographic interface with neural networks, blue glowing data streams',
            'productivity': 'modern organized workspace, clean minimal desk setup, productivity apps glowing',
            'automation': 'robotic arms working seamlessly, automated digital processes, tech machinery',
            'business': 'professional modern office, growth charts rising, successful entrepreneur workspace',
            'technology': 'cutting-edge tech devices, sleek interfaces, innovation lab, glowing circuits',
            'coding': 'dark theme code editor with syntax highlighting, developer typing, terminal commands',
            'design': 'creative design studio, adobe tools, graphic elements floating, artistic workspace',
            'marketing': 'social media dashboard with rising metrics, viral content, engagement graphs',
            'data': 'data visualization flowing, analytics dashboards, 3D graphs, information networks',
            'social media': 'social network connections visualized, content creation, viral growth animation',
            'money': 'cash flow, dollar bills, profit charts rising, wealth building visuals',
            'growth': 'exponential growth curves, scaling business, upward trends, success metrics',
            'video': 'video editing timeline, premiere pro, youtube studio, content creation',
            'instagram': 'instagram interface, reels scrolling, followers growing, engagement notifications',
            'tiktok': 'tiktok feed, viral videos, for you page, trending content',
            'youtube': 'youtube studio analytics, subscribers growing, monetization, views counter',
        }
        
        # Find matching concepts
        topic_lower = topic.lower()
        narration_lower = narration.lower()
        
        matched_visuals = []
        for keyword, visual in visual_keywords.items():
            if keyword in topic_lower or keyword in narration_lower:
                matched_visuals.append(visual)
        
        if matched_visuals:
            base_prompt = matched_visuals[0]
        else:
            # Generic but premium looking
            base_prompt = "modern digital workspace, innovative technology, sleek interface"
        
        # Add cinematic enhancement
        prompt = f"{base_prompt}, cinematic lighting, professional, ultra high quality 4k, smooth motion, dynamic camera movement"
        
        return prompt
    
    def _generate_leonardo_motion(
        self,
        prompt: str,
        duration: float,
        output_path: str
    ) -> Optional[str]:
        """
        Generate video using Leonardo.ai Motion
        150 free credits per month - BEST FREE TIER!
        """
        
        if not self.leonardo_key:
            return None
        
        try:
            logger.info("🎨 Trying Leonardo.ai Motion...")
            
            # Leonardo Motion API endpoint
            url = "https://cloud.leonardo.ai/api/rest/v1/generations-motion"
            
            headers = {
                "Authorization": f"Bearer {self.leonardo_key}",
                "Content-Type": "application/json"
            }
            
            # Create motion generation
            payload = {
                "prompt": prompt,
                "num_images": 1,
                "motion_strength": 8,  # Higher = more motion (1-10)
                "width": 720,
                "height": 1280,  # Vertical format for Shorts
                "isPublic": False
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Leonardo API error: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            generation_id = data.get("sdGenerationJob", {}).get("generationId")
            
            if not generation_id:
                logger.warning("No generation ID returned from Leonardo")
                return None
            
            # Poll for completion (Leonardo takes 20-60 seconds)
            logger.info("⏳ Waiting for Leonardo generation...")
            
            max_attempts = 40  # 2 minutes max
            for attempt in range(max_attempts):
                time.sleep(3)
                
                # Check status
                status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
                status_response = requests.get(status_url, headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    generation = status_data.get("generations_by_pk", {})
                    status = generation.get("status")
                    
                    logger.info(f"Leonardo status: {status} (attempt {attempt+1}/{max_attempts})")
                    
                    if status == "COMPLETE":
                        # Get video URL
                        images = generation.get("generated_images", [])
                        if images and images[0].get("motionMP4URL"):
                            video_url = images[0]["motionMP4URL"]
                            
                            # Download video
                            logger.info("⬇️ Downloading Leonardo video...")
                            video_response = requests.get(video_url, timeout=120)
                            
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)
                            
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                                logger.info(f"✅ Leonardo video generated: {output_path}")
                                return output_path
                            else:
                                logger.warning("Downloaded video is too small")
                                return None
                    
                    elif status == "FAILED":
                        logger.warning("Leonardo generation failed")
                        return None
            
            logger.warning("Leonardo generation timed out")
            return None
            
        except Exception as e:
            logger.warning(f"Leonardo error: {e}")
            return None
    
    def _generate_runway_gen2(
        self,
        prompt: str,
        duration: float,
        output_path: str
    ) -> Optional[str]:
        """
        Generate video using Runway Gen-2
        $12 free credits for new accounts (professional quality)
        """
        
        if not self.runway_key:
            return None
        
        try:
            logger.info("🎬 Trying Runway Gen-2...")
            
            url = "https://api.runwayml.com/v1/gen2"
            
            headers = {
                "Authorization": f"Bearer {self.runway_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text_prompt": prompt,
                "duration": min(int(duration), 10),  # Max 10s for free tier
                "aspect_ratio": "9:16",  # Vertical
                "output_format": "mp4"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code not in [200, 201]:
                logger.warning(f"Runway API error: {response.status_code}")
                return None
            
            data = response.json()
            task_id = data.get("id")
            
            # Poll for completion
            logger.info("⏳ Processing with Runway...")
            
            for attempt in range(60):  # 3 minutes max
                time.sleep(3)
                
                status_url = f"https://api.runwayml.com/v1/tasks/{task_id}"
                status_response = requests.get(status_url, headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    
                    logger.info(f"Runway status: {status}")
                    
                    if status == "succeeded":
                        video_url = status_data.get("output_url")
                        
                        if video_url:
                            logger.info("⬇️ Downloading Runway video...")
                            video_response = requests.get(video_url, timeout=120)
                            
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)
                            
                            logger.info(f"✅ Runway video generated: {output_path}")
                            return output_path
                    
                    elif status == "failed":
                        logger.warning("Runway generation failed")
                        return None
            
            logger.warning("Runway generation timed out")
            return None
            
        except Exception as e:
            logger.warning(f"Runway error: {e}")
            return None
    
    def _generate_animated_fallback(
        self,
        prompt: str,
        duration: float,
        output_path: str
    ) -> Optional[str]:
        """
        Fallback: Generate animated gradient video using FFmpeg
        Creates smooth zoom/pan effect with dynamic colors
        ALWAYS WORKS - No API needed
        """
        
        try:
            logger.info("🎨 Using animated gradient fallback...")
            
            # Determine color scheme from prompt
            if 'ai' in prompt.lower() or 'technology' in prompt.lower():
                color1 = "0x4B0082"  # Purple
                color2 = "0x0096FF"  # Blue
            elif 'business' in prompt.lower() or 'money' in prompt.lower():
                color1 = "0x006400"  # Dark green
                color2 = "0xFFD700"  # Gold
            elif 'social' in prompt.lower() or 'viral' in prompt.lower():
                color1 = "0xFF1493"  # Pink
                color2 = "0xFF6347"  # Red-orange
            else:
                color1 = "0xFF6600"  # Orange
                color2 = "0xFFC800"  # Yellow
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # FFmpeg command to create animated gradient with zoom effect
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c={color1}:s=720x1280:d={duration}',
                '-f', 'lavfi',
                '-i', f'color=c={color2}:s=720x1280:d={duration}',
                '-filter_complex',
                f'[0:v][1:v]blend=all_mode=overlay:all_opacity=0.5,zoompan=z=\'min(zoom+0.0015,1.5)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={int(duration*30)}:s=720x1280,format=yuv420p[v]',
                '-map', '[v]',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '23',
                '-t', str(duration),
                output_path
            ]
            
            logger.info("🎬 Generating animated gradient...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Animated fallback video created: {output_path}")
                return output_path
            else:
                logger.error(f"FFmpeg fallback failed: {result.stderr[:200]}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Animated fallback failed: {e}")
            return None
    
    def generate_multi_scene_video(
        self,
        scenes: List[Dict],
        output_path: str = "temp/multi_scene.mp4"
    ) -> Optional[str]:
        """
        Generate video with multiple AI-generated scenes
        Like Instagram viral videos - rapid scene changes for retention
        
        Args:
            scenes: List of dicts with 'prompt' and 'duration'
                Example: [
                    {"prompt": "AI coding assistant", "duration": 3},
                    {"prompt": "Automated workflow", "duration": 3}
                ]
            output_path: Final video path
        
        Returns:
            Path to concatenated video or None
        """
        
        try:
            logger.info(f"🎬 Generating {len(scenes)} scene video...")
            
            scene_paths = []
            
            for i, scene in enumerate(scenes):
                prompt = scene.get('prompt', '')
                duration = scene.get('duration', 5.0)
                
                scene_path = f"temp/scene_{i}.mp4"
                
                # Generate each scene
                result = self.generate_contextual_video(
                    topic=prompt,
                    narration=prompt,
                    duration=duration,
                    output_path=scene_path
                )
                
                if result and os.path.exists(result):
                    scene_paths.append(result)
                    logger.info(f"✅ Scene {i+1}/{len(scenes)} generated")
            
            if not scene_paths:
                logger.error("No scenes generated successfully")
                return None
            
            # Concatenate all scenes using FFmpeg
            concat_list_path = "temp/concat_scenes.txt"
            with open(concat_list_path, 'w') as f:
                for path in scene_paths:
                    abs_path = os.path.abspath(path).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
            
            concat_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',
                output_path
            ]
            
            logger.info("🔗 Concatenating scenes...")
            subprocess.run(concat_cmd, check=True, capture_output=True, timeout=60)
            
            if os.path.exists(output_path):
                logger.info(f"✅ Multi-scene video created: {output_path}")
                
                # Cleanup temp scene files
                for path in scene_paths:
                    try:
                        os.remove(path)
                    except:
                        pass
                
                return output_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Multi-scene generation failed: {e}")
            return None


# ==================== TEST FUNCTION ====================
def test_ai_video_generation():
    """Test the AI video generator"""
    
    print("\n" + "="*60)
    print("🧪 TESTING AI VIDEO GENERATION")
    print("="*60)
    
    generator = AIVideoGenerator()
    
    # Test 1: Single contextual video
    print("\n📹 Test 1: Single contextual video...")
    
    video_path = generator.generate_contextual_video(
        topic="AI productivity tools",
        narration="Discover the power of AI automation to save 10 hours per week and boost productivity",
        duration=5.0,
        output_path="test_ai_video.mp4"
    )
    
    if video_path and os.path.exists(video_path):
        print(f"✅ Video generated: {video_path}")
        print(f"   Size: {os.path.getsize(video_path) / 1024:.1f} KB")
    else:
        print("❌ Video generation failed")
    
    # Test 2: Multi-scene video (Instagram style)
    print("\n📹 Test 2: Multi-scene video (Instagram viral style)...")
    
    scenes = [
        {"prompt": "AI coding assistant interface with code generation", "duration": 3},
        {"prompt": "Automated workflow dashboard showing tasks completing", "duration": 3},
        {"prompt": "Productivity metrics growing exponentially", "duration": 3}
    ]
    
    multi_path = generator.generate_multi_scene_video(
        scenes=scenes,
        output_path="test_multi_scene.mp4"
    )
    
    if multi_path and os.path.exists(multi_path):
        print(f"✅ Multi-scene video generated: {multi_path}")
        print(f"   Size: {os.path.getsize(multi_path) / 1024:.1f} KB")
    else:
        print("❌ Multi-scene generation failed")
    
    print("\n" + "="*60)
    print("✅ TESTS COMPLETE")
    print("="*60)
    print("\nNEXT STEPS:")
    print("1. Get Leonardo.ai API key (150 free videos/month)")
    print("   → https://leonardo.ai → Settings → API")
    print("2. Add to .env: LEONARDO_API_KEY=your_key_here")
    print("3. Integrate into master_automation.py")
    print("4. Deploy and watch retention improve! 📈")


if __name__ == "__main__":
    test_ai_video_generation()
