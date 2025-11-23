#!/usr/bin/env python3
"""
🎬 PROFESSIONAL AI VIDEO GENERATOR - FULL AUTOMATION
Generates actual videos using FFmpeg + AI voices + subtitles + B-roll
"""

import os
import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ImageClip, ColorClip
)
from moviepy.video.fx import resize, fadein, fadeout
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from gtts import gTTS
import whisper
from yt_dlp import YoutubeDL

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
class VideoGenConfig:
    # Directories
    OUTPUT_DIR = Path("generated_videos")
    TEMP_DIR = Path("temp")
    ASSETS_DIR = Path("assets")
    FONTS_DIR = ASSETS_DIR / "fonts"
    
    # Video specs for YouTube Shorts
    WIDTH = 1080
    HEIGHT = 1920
    FPS = 30
    DURATION = 60  # Max 60 seconds
    
    # AI Voice APIs (Choose one or rotate)
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    PLAY_HT_API_KEY = os.getenv('PLAY_HT_API_KEY')
    
    # B-roll sources
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
    PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')
    
    # Stable Diffusion (Optional)
    STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
    
    @classmethod
    def init_dirs(cls):
        """Create necessary directories"""
        for dir_path in [cls.OUTPUT_DIR, cls.TEMP_DIR, cls.ASSETS_DIR, cls.FONTS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

# ==================== VIDEO DOWNLOADER ====================
class VideoDownloader:
    """Download source videos from YouTube"""
    
    @staticmethod
    def download_video(url: str, output_path: str, timestamps: tuple = None) -> str:
        """Download video and optionally trim to timestamps"""
        try:
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best',
                'outtmpl': output_path,
                'quiet': True
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Trim if timestamps provided
            if timestamps:
                start, end = timestamps
                trimmed = output_path.replace('.mp4', '_trimmed.mp4')
                VideoDownloader.trim_video(output_path, trimmed, start, end)
                return trimmed
            
            return output_path
        
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None
    
    @staticmethod
    def trim_video(input_path: str, output_path: str, start: int, end: int):
        """Trim video using FFmpeg"""
        cmd = [
            'ffmpeg', '-i', input_path,
            '-ss', str(start), '-to', str(end),
            '-c', 'copy', output_path, '-y'
        ]
        subprocess.run(cmd, check=True, capture_output=True)

# ==================== AI VOICE GENERATOR ====================
class AIVoiceGenerator:
    """Generate professional AI voiceovers"""
    
    def __init__(self):
        self.elevenlabs_key = VideoGenConfig.ELEVENLABS_API_KEY
    
    def generate_elevenlabs(self, text: str, output_path: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> str:
        """Generate voice using ElevenLabs (most professional)"""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": self.elevenlabs_key,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"✅ Voice generated: {output_path}")
                return output_path
            else:
                raise Exception(f"ElevenLabs API error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"ElevenLabs failed: {e}, falling back to gTTS")
            return self.generate_gtts(text, output_path)
    
    def generate_gtts(self, text: str, output_path: str) -> str:
        """Fallback: Generate voice using Google TTS (free)"""
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        logger.info(f"✅ gTTS voice generated: {output_path}")
        return output_path
    
    def generate_voice(self, text: str, output_path: str) -> str:
        """Main method - tries best option first"""
        if self.elevenlabs_key:
            return self.generate_elevenlabs(text, output_path)
        else:
            return self.generate_gtts(text, output_path)

# ==================== SUBTITLE GENERATOR ====================
class SubtitleGenerator:
    """Generate animated captions using Whisper"""
    
    def __init__(self):
        self.model = whisper.load_model("base")
    
    def transcribe_audio(self, audio_path: str) -> List[Dict]:
        """Transcribe audio to get word-level timestamps"""
        result = self.model.transcribe(audio_path, word_timestamps=True)
        
        words = []
        for segment in result['segments']:
            for word in segment.get('words', []):
                words.append({
                    'text': word['word'],
                    'start': word['start'],
                    'end': word['end']
                })
        
        return words
    
    def create_caption_clips(self, words: List[Dict], video_size: tuple) -> List[TextClip]:
        """Create animated caption clips (TikTok style)"""
        clips = []
        
        for word_data in words:
            txt = TextClip(
                word_data['text'].upper(),
                fontsize=80,
                color='white',
                stroke_color='black',
                stroke_width=3,
                font='Arial-Bold',
                method='caption',
                size=(video_size[0] - 100, None)
            ).set_position(('center', 'center')).set_start(word_data['start']).set_end(word_data['end'])
            
            # Add pop-in effect
            txt = txt.fx(fadein, 0.1).fx(fadeout, 0.1)
            clips.append(txt)
        
        return clips

# ==================== B-ROLL FETCHER ====================
class BRollFetcher:
    """Fetch stock footage and AI-generated images"""
    
    def __init__(self):
        self.pexels_key = VideoGenConfig.PEXELS_API_KEY
        self.stability_key = VideoGenConfig.STABILITY_API_KEY
    
    def fetch_pexels_video(self, query: str, output_path: str) -> Optional[str]:
        """Download stock video from Pexels"""
        try:
            url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
            headers = {"Authorization": self.pexels_key}
            
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if data['videos']:
                video_url = data['videos'][0]['video_files'][0]['link']
                video_data = requests.get(video_url)
                
                with open(output_path, 'wb') as f:
                    f.write(video_data.content)
                
                logger.info(f"✅ B-roll downloaded: {output_path}")
                return output_path
        
        except Exception as e:
            logger.error(f"Pexels fetch failed: {e}")
        
        return None
    
    def generate_ai_image(self, prompt: str, output_path: str) -> Optional[str]:
        """Generate image using Stable Diffusion"""
        if not self.stability_key:
            return None
        
        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Content-Type": "application/json"
            }
            data = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1920,
                "width": 1080,
                "samples": 1,
                "steps": 30
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                image_data = response.json()['artifacts'][0]['base64']
                import base64
                
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(image_data))
                
                logger.info(f"✅ AI image generated: {output_path}")
                return output_path
        
        except Exception as e:
            logger.error(f"Stable Diffusion failed: {e}")
        
        return None

# ==================== VIDEO COMPOSER ====================
class VideoComposer:
    """Compose final video with all elements"""
    
    def __init__(self):
        self.voice_gen = AIVoiceGenerator()
        self.sub_gen = SubtitleGenerator()
        self.broll = BRollFetcher()
    
    def create_short(self, script: Dict, output_path: str) -> str:
        """Create complete YouTube Short"""
        try:
            logger.info("🎬 Starting video creation...")
            
            # Step 1: Generate voiceover
            voice_path = VideoGenConfig.TEMP_DIR / "voice.mp3"
            self.voice_gen.generate_voice(script['narration'], str(voice_path))
            
            # Step 2: Get video duration from audio
            audio = AudioFileClip(str(voice_path))
            duration = min(audio.duration, VideoGenConfig.DURATION)
            
            # Step 3: Create background
            if script.get('source_video'):
                # Option A: Use trimmed source video
                bg_video = VideoFileClip(script['source_video'])
                bg_video = bg_video.subclip(0, min(duration, bg_video.duration))
            else:
                # Option B: Fetch B-roll or generate AI background
                broll_path = VideoGenConfig.TEMP_DIR / "broll.mp4"
                fetched = self.broll.fetch_pexels_video(script['topic'], str(broll_path))
                
                if fetched:
                    bg_video = VideoFileClip(fetched).subclip(0, duration)
                else:
                    # Fallback: Solid color with zoom effect
                    bg_video = ColorClip(
                        size=(VideoGenConfig.WIDTH, VideoGenConfig.HEIGHT),
                        color=(20, 20, 40),
                        duration=duration
                    )
            
            # Resize and crop to vertical format
            bg_video = bg_video.fx(resize, height=VideoGenConfig.HEIGHT)
            bg_video = bg_video.crop(
                x_center=bg_video.w/2,
                width=VideoGenConfig.WIDTH,
                height=VideoGenConfig.HEIGHT
            )
            
            # Step 4: Generate captions
            words = self.sub_gen.transcribe_audio(str(voice_path))
            caption_clips = self.sub_gen.create_caption_clips(
                words,
                (VideoGenConfig.WIDTH, VideoGenConfig.HEIGHT)
            )
            
            # Step 5: Add hook text at start
            hook_clip = TextClip(
                script['hook'].upper(),
                fontsize=100,
                color='yellow',
                stroke_color='black',
                stroke_width=5,
                font='Arial-Bold',
                method='caption',
                size=(VideoGenConfig.WIDTH - 100, None)
            ).set_position(('center', 200)).set_duration(3).fx(fadein, 0.5)
            
            # Step 6: Add CTA at end
            cta_clip = TextClip(
                script['cta'].upper(),
                fontsize=80,
                color='white',
                bg_color='red',
                font='Arial-Bold',
                method='caption',
                size=(VideoGenConfig.WIDTH - 100, None)
            ).set_position(('center', 'bottom')).set_start(duration - 3).set_duration(3)
            
            # Step 7: Composite everything
            final_video = CompositeVideoClip(
                [bg_video, hook_clip, cta_clip] + caption_clips,
                size=(VideoGenConfig.WIDTH, VideoGenConfig.HEIGHT)
            )
            
            # Step 8: Add audio
            final_video = final_video.set_audio(audio)
            
            # Step 9: Export with optimal settings
            final_video.write_videofile(
                output_path,
                fps=VideoGenConfig.FPS,
                codec='libx264',
                audio_codec='aac',
                bitrate='8000k',
                preset='medium',
                threads=4
            )
            
            logger.info(f"✅ Video created: {output_path}")
            
            # Cleanup
            audio.close()
            bg_video.close()
            final_video.close()
            
            return output_path
        
        except Exception as e:
            logger.error(f"❌ Video creation failed: {e}")
            raise

# ==================== AFFILIATE OPTIMIZER ====================
class AffiliateOptimizer:
    """Optimize affiliate performance using A/B testing"""
    
    def __init__(self):
        self.performance_db = {}
    
    def track_conversion(self, video_id: str, affiliate_tool: str, clicks: int, conversions: int):
        """Track affiliate performance"""
        key = f"{video_id}_{affiliate_tool}"
        self.performance_db[key] = {
            'clicks': clicks,
            'conversions': conversions,
            'ctr': conversions / clicks if clicks > 0 else 0
        }
    
    def get_best_performers(self, top_n: int = 5) -> List[Dict]:
        """Get top performing affiliate tools"""
        sorted_tools = sorted(
            self.performance_db.items(),
            key=lambda x: x[1]['ctr'],
            reverse=True
        )
        return sorted_tools[:top_n]
    
    def optimize_cta_placement(self, script: Dict) -> Dict:
        """A/B test different CTA placements"""
        variants = [
            {'placement': 'start', 'timing': 2},
            {'placement': 'middle', 'timing': script.get('duration', 30) / 2},
            {'placement': 'end', 'timing': script.get('duration', 30) - 3}
        ]
        
        # Return random variant for testing
        import random
        chosen = random.choice(variants)
        script['cta_config'] = chosen
        return script

# ==================== BATCH PROCESSOR ====================
class BatchVideoProcessor:
    """Process multiple videos in parallel"""
    
    def __init__(self, max_workers: int = 3):
        self.composer = VideoComposer()
        self.optimizer = AffiliateOptimizer()
        self.max_workers = max_workers
    
    def process_batch(self, scripts: List[Dict]):
        """Process multiple video scripts"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self.composer.create_short,
                    script,
                    str(VideoGenConfig.OUTPUT_DIR / f"short_{i}.mp4")
                ): script for i, script in enumerate(scripts)
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"✅ Batch item completed: {result}")
                except Exception as e:
                    logger.error(f"❌ Batch item failed: {e}")
        
        return results

# ==================== MAIN PIPELINE ====================
class VideoGenerationPipeline:
    """Complete video generation pipeline"""
    
    def __init__(self):
        VideoGenConfig.init_dirs()
        self.composer = VideoComposer()
        self.batch_processor = BatchVideoProcessor()
    
    def generate_single_video(self, script: Dict, output_filename: str = None) -> str:
        """Generate a single video"""
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"short_{timestamp}.mp4"
        
        output_path = VideoGenConfig.OUTPUT_DIR / output_filename
        return self.composer.create_short(script, str(output_path))
    
    def generate_from_analysis(self, analysis: Dict, source_video_url: str = None) -> str:
        """Generate video from LLM analysis"""
        
        # Download source if provided
        source_path = None
        if source_video_url:
            source_path = VideoGenConfig.TEMP_DIR / "source.mp4"
            timestamps = analysis.get('best_clips', '0:00-0:60').split('-')
            start = self._parse_timestamp(timestamps[0])
            end = self._parse_timestamp(timestamps[1])
            
            downloader = VideoDownloader()
            source_path = downloader.download_video(
                source_video_url,
                str(source_path),
                (start, end)
            )
        
        # Build script
        script = {
            'narration': f"{analysis['short_hook']}. {analysis['summary'][:200]}. {analysis['cta']}",
            'hook': analysis['short_hook'],
            'cta': analysis['cta'],
            'topic': analysis['key_topics'].split(',')[0],
            'source_video': source_path
        }
        
        return self.generate_single_video(script)
    
    def _parse_timestamp(self, ts: str) -> int:
        """Convert timestamp string to seconds"""
        parts = ts.strip().split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0

# ==================== USAGE EXAMPLE ====================
def main():
    """Example usage"""
    
    # Initialize pipeline
    pipeline = VideoGenerationPipeline()
    
    # Example 1: Generate from script
    script = {
        'narration': "This AI tool will change everything. CustomGPT lets you build custom chatbots in minutes. No coding required. Try it now with the link in bio.",
        'hook': "This AI Tool is Insane",
        'cta': "Link in Bio - Try Free",
        'topic': "AI technology",
        'source_video': None  # Will fetch B-roll
    }
    
    video_path = pipeline.generate_single_video(script)
    print(f"✅ Video generated: {video_path}")
    
    # Example 2: Generate from analysis + source video
    analysis = {
        'short_hook': "ChatGPT's New Feature is Wild",
        'summary': "OpenAI just released a game-changing update that lets you create custom GPTs",
        'key_topics': "ChatGPT, AI, Custom GPTs",
        'cta': "Try ChatGPT Plus Today",
        'best_clips': "2:30-3:00"
    }
    
    video_path = pipeline.generate_from_analysis(
        analysis,
        source_video_url="https://www.youtube.com/watch?v=example"
    )
    print(f"✅ Video generated: {video_path}")

if __name__ == "__main__":
    main()
# Aliases for compatibility
FacelessAutomationPipeline = VideoGenerationPipeline
FreeConfig = VideoGenConfig
