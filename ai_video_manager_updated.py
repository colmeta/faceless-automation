#!/usr/bin/env python3
"""
🎬 AI VIDEO GENERATION MANAGER - UPDATED WITH YOUR APIS!
==================================
Uses YOUR available APIs:
1. Kling AI (access_key + secret_key) ⭐ PRIMARY
2. Runway Gen-2 (you have this!) ⭐ BACKUP
3. Replicate (versatile AI platform) 
4. Pixverse (AI video generation)
5. Animated fallback (always works)

MEMORY OPTIMIZED FOR RENDER 512MB!
"""

import os
import logging
import requests
import time
import subprocess
from typing import Optional, List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIVideoGenerator:
    """Generate contextual AI videos using YOUR APIs"""
    
    def __init__(self):
        # YOUR API KEYS
        self.kling_access_key = os.getenv('KLING_ACCESS_KEY', '').strip()
        self.kling_secret_key = os.getenv('KLING_SECRET_KEY', '').strip()
        self.runway_key = os.getenv('RUNWAY_API_KEY', '').strip()
        self.replicate_key = os.getenv('REPLICATE_API_TOKEN', '').strip()
        self.pixverse_key = os.getenv('PIXVERSE_API_KEY', '').strip()
        
        logger.info("🎬 AI Video Generator initialized")
        logger.info(f"📊 Kling AI: {'✅ Available' if self.kling_access_key else '❌ Not configured'}")
        logger.info(f"📊 Runway: {'✅ Available' if self.runway_key else '❌ Not configured'}")
        logger.info(f"📊 Replicate: {'✅ Available' if self.replicate_key else '❌ Not configured'}")
        logger.info(f"📊 Pixverse: {'✅ Available' if self.pixverse_key else '❌ Not configured'}")
        
    def generate_contextual_video(
        self,
        topic: str,
        narration: str,
        duration: float = 10.0,
        output_path: str = "temp/ai_video.mp4"
    ) -> Optional[str]:
        """Generate AI video using YOUR APIs"""
        
        visual_prompt = self._create_visual_prompt(topic, narration)
        logger.info(f"🎨 Generating: '{visual_prompt[:60]}...'")
        
        # Try services in order of cost/quality
        
        # 1. Kling AI (YOUR PRIMARY - Best quality!)
        if self.kling_access_key:
            video_path = self._generate_kling(visual_prompt, duration, output_path)
            if video_path:
                return video_path
        
        # 2. Runway Gen-2 (YOUR BACKUP)
        if self.runway_key:
            video_path = self._generate_runway(visual_prompt, duration, output_path)
            if video_path:
                return video_path
        
        # 3. Replicate (Good fallback)
        if self.replicate_key:
            video_path = self._generate_replicate(visual_prompt, duration, output_path)
            if video_path:
                return video_path
        
        # 4. Pixverse (Additional fallback)
        if self.pixverse_key:
            video_path = self._generate_pixverse(visual_prompt, duration, output_path)
            if video_path:
                return video_path
        
        # 5. Animated fallback (always works)
        logger.warning("⚠️ All AI APIs unavailable, using animated fallback...")
        return self._generate_animated_fallback(visual_prompt, duration, output_path)
    
    def _create_visual_prompt(self, topic: str, narration: str) -> str:
        """Extract visual concepts from narration"""
        
        visual_keywords = {
            'ai': 'futuristic AI holographic interface, neural networks glowing',
            'productivity': 'modern workspace, productivity dashboard, efficient workflow',
            'automation': 'robotic systems, automated processes, smart technology',
            'business': 'professional office, growth charts, successful entrepreneurs',
            'technology': 'cutting-edge tech, sleek interfaces, innovation',
            'coding': 'code editor syntax highlighting, developer workspace',
            'design': 'creative design studio, graphic elements, artistic workspace',
            'marketing': 'social media analytics, viral content, engagement graphs',
            'money': 'cash flow, profit charts rising, wealth building',
            'instagram': 'instagram reels, followers growing, engagement',
            'youtube': 'youtube analytics, subscribers growing, monetization',
        }
        
        topic_lower = topic.lower()
        narration_lower = narration.lower()
        
        matched_visuals = []
        for keyword, visual in visual_keywords.items():
            if keyword in topic_lower or keyword in narration_lower:
                matched_visuals.append(visual)
        
        base_prompt = matched_visuals[0] if matched_visuals else "modern digital workspace, innovative technology"
        
        return f"{base_prompt}, cinematic lighting, professional 4k, smooth motion"
    
    def _generate_kling(
        self,
        prompt: str,
        duration: float,
        output_path: str
    ) -> Optional[str]:
        """
        Generate video using Kling AI (YOUR PRIMARY API)
        Kling is excellent for high-quality AI videos
        """
        
        if not self.kling_access_key:
            return None
        
        try:
            logger.info("🎨 Trying Kling AI (YOUR PRIMARY)...")
            
            # Kling AI API endpoint
            url = "https://api.klingai.com/v1/videos/text2video"
            
            headers = {
                "Authorization": f"Bearer {self.kling_access_key}",
                "X-Secret-Key": self.kling_secret_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "duration": min(int(duration), 10),  # Max 10s
                "aspect_ratio": "9:16",  # Vertical for Shorts
                "mode": "standard"  # or "professional" for higher quality
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Kling API error: {response.status_code}")
                return None
            
            data = response.json()
            task_id = data.get("task_id")
            
            if not task_id:
                logger.warning("No task ID from Kling")
                return None
            
            # Poll for completion
            logger.info("⏳ Waiting for Kling generation...")
            
            for attempt in range(60):  # 3 minutes max
                time.sleep(3)
                
                status_url = f"https://api.klingai.com/v1/videos/{task_id}"
                status_response = requests.get(status_url, headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    
                    logger.info(f"Kling status: {status}")
                    
                    if status == "succeeded":
                        video_url = status_data.get("video_url")
                        
                        if video_url:
                            logger.info("⬇️ Downloading Kling video...")
                            video_response = requests.get(video_url, timeout=120)
                            
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(video_response.content)
                            
                            logger.info(f"✅ Kling video generated: {output_path}")
                            return output_path
                    
                    elif status == "failed":
                        logger.warning("Kling generation failed")
                        return None
            
            logger.warning("Kling generation timed out")
            return None
            
        except Exception as e:
            logger.warning(f"Kling error: {e}")
            return None
    
    def _generate_runway(
        self,
        prompt: str,
        duration: float,
        output_path: str
    ) -> Optional[str]:
        """Generate video using Runway Gen-2 (YOUR BACKUP)"""
        
        if not self.runway_key:
            return None
        
        try:
            logger.info("🎬 Trying Runway Gen-2 (YOUR BACKUP)...")
            
            url = "https://api.runwayml.com/v1/gen2"
            
            headers = {
                "Authorization": f"Bearer {self.runway_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text_prompt": prompt,
                "duration": min(int(duration), 10),
                "aspect_ratio": "9:16",
                "output_format": "mp4"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code not in [200, 201]:
                logger.warning(f"Runway API error: {response.status_code}")
                return None
            
            data = response.json()
            task_id = data.get("id")
            
            logger.info("⏳ Processing with Runway...")
            
            for attempt in range(60):
                time.sleep(3)
                
                status_url = f"https://api.runwayml.com/v1/tasks/{task_id}"
                status_response = requests.get(status_url, headers=headers, timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    
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
                        return None
            
            return None
            
        except Exception as e:
            logger.warning(f"Runway error: {e}")
            return None
    
    def _generate_replicate(
        self,
        prompt: str,
        duration: float,
        output_path: str
    ) -> Optional[str]:
        """Generate video using Replicate (Stable Video Diffusion)"""
        
        if not self.replicate_key:
            return None
        
        try:
            logger.info("🎨 Trying Replicate...")
            
            import replicate
            
            # Use Zeroscope model (good for text-to-video)
            output = replicate.run(
                "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
                input={
                    "prompt": prompt,
                    "num_frames": int(duration * 8),  # 8 fps
                    "width": 576,
                    "height": 1024
                }
            )
            
            if output:
                video_url = output[0] if isinstance(output, list) else output
                
                logger.info("⬇️ Downloading Replicate video...")
                video_response = requests.get(video_url, timeout=120)
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(video_response.content)
                
                logger.info(f"✅ Replicate video generated: {output_path}")
                return output_path
            
            return None
            
        except Exception as e:
            logger.warning(f"Replicate error: {e}")
            return None
    
    def _generate_pixverse(
        self,
        prompt: str,
        duration: float,
        output_path: str
    ) -> Optional[str]:
        """Generate video using Pixverse"""
        
        if not self.pixverse_key:
            return None
        
        try:
            logger.info("🎨 Trying Pixverse...")
            
            # Pixverse API (adjust based on their actual API)
            url = "https://api.pixverse.com/v1/generate"
            
            headers = {
                "Authorization": f"Bearer {self.pixverse_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "duration": int(duration),
                "aspect_ratio": "9:16"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                video_url = data.get("video_url")
                
                if video_url:
                    logger.info("⬇️ Downloading Pixverse video...")
                    video_response = requests.get(video_url, timeout=120)
                    
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)
                    
                    logger.info(f"✅ Pixverse video generated: {output_path}")
                    return output_path
            
            return None
            
        except Exception as e:
            logger.warning(f"Pixverse error: {e}")
            return None
    
    def _generate_animated_fallback(
        self,
        prompt: str,
        duration: float,
        output_path: str
    ) -> Optional[str]:
        """Fallback: Animated gradient (ALWAYS WORKS, MEMORY EFFICIENT)"""
        
        try:
            logger.info("🎨 Using animated gradient fallback...")
            
            # Color scheme based on prompt
            if 'ai' in prompt.lower():
                color1, color2 = "0x4B0082", "0x0096FF"
            elif 'business' in prompt.lower():
                color1, color2 = "0x006400", "0xFFD700"
            else:
                color1, color2 = "0xFF6600", "0xFFC800"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # FFmpeg command (NO MEMORY USAGE!)
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c={color1}:s=720x1280:d={duration}',
                '-f', 'lavfi',
                '-i', f'color=c={color2}:s=720x1280:d={duration}',
                '-filter_complex',
                f'[0:v][1:v]blend=all_mode=overlay:all_opacity=0.5,zoompan=z=\'min(zoom+0.0015,1.5)\':d={int(duration*30)}:s=720x1280[v]',
                '-map', '[v]',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '23',
                '-t', str(duration),
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Animated fallback created: {output_path}")
                return output_path
            
            return None
                
        except Exception as e:
            logger.error(f"❌ Fallback failed: {e}")
            return None


if __name__ == "__main__":
    print("\n🧪 Testing AI Video Generator with YOUR APIs\n")
    
    generator = AIVideoGenerator()
    
    video_path = generator.generate_contextual_video(
        topic="AI productivity tools",
        narration="Discover AI automation to save 10 hours per week",
        duration=5.0,
        output_path="test_video.mp4"
    )
    
    if video_path:
        print(f"\n✅ SUCCESS! Video: {video_path}")
        print(f"   Size: {os.path.getsize(video_path) / 1024:.1f} KB")
    else:
        print("\n❌ Video generation failed")
