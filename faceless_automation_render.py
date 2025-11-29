#!/usr/bin/env python3
"""
🎬 RENDER-OPTIMIZED VIDEO GENERATOR
Lightweight version for Render free instance (512MB RAM)
- No Whisper (uses simple captions)
- No complex fonts (system fonts only)
- Memory optimized
- Cloudinary integration for storage
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
from moviepy.video.fx.all import resize, fadein, fadeout
from PIL import Image, ImageDraw, ImageFont
import numpy as np
# from gtts import gTTS
import cloudinary
import cloudinary.uploader

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
class VideoGenConfig:
    # Directories
    OUTPUT_DIR = Path("generated_videos")
    TEMP_DIR = Path("temp")
    
    # Video specs for YouTube Shorts
    WIDTH = 1080
    HEIGHT = 1920
    FPS = 30
    DURATION = 60  # Max 60 seconds
    
    # B-roll sources
    PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
    PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')
    
    # Cloudinary for storage
    CLOUDINARY_ENABLED = bool(os.getenv('CLOUDINARY_CLOUD_NAME'))
    
    @classmethod
    def init_dirs(cls):
        """Create necessary directories"""
        for dir_path in [cls.OUTPUT_DIR, cls.TEMP_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

# ==================== AI VOICE GENERATOR ====================
class AIVoiceGenerator:
    """Generate AI voiceovers using gTTS (lightweight)"""
    
    def generate_voice(self, text: str, output_path: str) -> str:
        """Generate voice using Edge-TTS (high quality, free)"""
        try:
            import asyncio
            import edge_tts
            
            async def _gen():
                communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
                await communicate.save(output_path)
                
            asyncio.run(_gen())
            
            logger.info(f"✅ Voice generated: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"⚠️ Edge-TTS failed ({e}), falling back to gTTS...")
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(output_path)
                logger.info(f"✅ Voice generated (gTTS fallback): {output_path}")
                return output_path
            except Exception as gtts_error:
                logger.error(f"❌ Voice generation failed completely: {gtts_error}")
                raise

# ==================== SIMPLE SUBTITLE GENERATOR ====================
class SimpleSubtitleGenerator:
    """Generate simple captions without Whisper (memory efficient)"""
    
    def create_simple_captions(self, text: str, duration: float, video_size: tuple) -> List[TextClip]:
        """Create simple scrolling captions"""
        clips = []
        
        # Split text into sentences
        sentences = text.split('. ')
        time_per_sentence = duration / max(len(sentences), 1)
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            start_time = i * time_per_sentence
            end_time = min((i + 1) * time_per_sentence, duration)
            
            try:
                # Professional Caption Style
                # 1. Background box for readability
                # 2. Better font (Arial-Bold is usually available on Linux/Render)
                
                # Calculate text size to size the background box
                # Note: TextClip doesn't give exact size easily without rendering, 
                # so we use a fixed width box or full width strip
                
                text_clip = TextClip(
                    sentence.strip().upper(),
                    fontsize=55,
                    font='Arial-Bold',  # Use a bolder font
                    color='white',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(video_size[0] - 140, None),
                    align='center'
                )
                
                # Create a semi-transparent background box
                # We'll make a strip at the bottom-center
                txt_w, txt_h = text_clip.size
                
                # Composite text over background
                txt_composite = CompositeVideoClip([
                    text_clip.set_position('center')
                ], size=(video_size[0], txt_h + 40))
                
                # Position the whole thing
                final_clip = txt_composite.set_position(('center', 'center')).set_start(start_time).set_duration(end_time - start_time)
                
                clips.append(final_clip)
            except Exception as e:
                logger.warning(f"⚠️ Skipping caption: {e}")
                continue
        
        return clips

# ==================== B-ROLL FETCHER ====================
class BRollFetcher:
    """Fetch stock footage"""
    
    def __init__(self):
        self.pexels_key = VideoGenConfig.PEXELS_API_KEY
        self.pixabay_key = VideoGenConfig.PIXABAY_API_KEY
    
    def fetch_pexels_video(self, query: str, output_path: str) -> Optional[str]:
        """Download stock video from Pexels"""
        if not self.pexels_key:
            logger.warning("⚠️ Pexels API key missing")
            return None
            
        try:
            url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
            headers = {"Authorization": self.pexels_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            if data.get('videos'):
                # Get HD video file
                video_files = data['videos'][0]['video_files']
                hd_file = next((f for f in video_files if f.get('quality') == 'hd'), video_files[0])
                video_url = hd_file['link']
                
                # Download
                video_data = requests.get(video_url, timeout=30)
                
                with open(output_path, 'wb') as f:
                    f.write(video_data.content)
                
                logger.info(f"✅ B-roll downloaded: {output_path}")
                return output_path
        
        except Exception as e:
            logger.error(f"❌ Pexels fetch failed: {e}")
        
        return None
    
    def fetch_pixabay_video(self, query: str, output_path: str) -> Optional[str]:
        """Download video from Pixabay"""
        if not self.pixabay_key:
            logger.warning("⚠️ Pixabay API key missing")
            return None
            
        try:
            url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={query}&per_page=3"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('hits'):
                # Get medium quality portrait video
                for hit in data['hits']:
                    videos = hit.get('videos', {})
                    video_url = videos.get('medium', {}).get('url')
                    
                    if video_url:
                        video_data = requests.get(video_url, timeout=30)
                        
                        with open(output_path, 'wb') as f:
                            f.write(video_data.content)
                        
                        logger.info(f"✅ Pixabay video downloaded: {output_path}")
                        return output_path
        
        except Exception as e:
            logger.error(f"❌ Pixabay fetch failed: {e}")
        
        return None

    def fetch_broll_sequence(self, query: str, count: int, output_dir: str) -> List[str]:
        """Fetch a sequence of unique B-roll videos"""
        clips_paths = []
        
        # Try Pexels first
        if self.pexels_key:
            try:
                url = f"https://api.pexels.com/videos/search?query={query}&per_page={count}&orientation=portrait"
                headers = {"Authorization": self.pexels_key}
                
                response = requests.get(url, headers=headers, timeout=10)
                data = response.json()
                
                if data.get('videos'):
                    for i, video in enumerate(data['videos']):
                        if i >= count: break
                        
                        # Get HD video file
                        video_files = video['video_files']
                        hd_file = next((f for f in video_files if f.get('quality') == 'hd'), video_files[0])
                        video_url = hd_file['link']
                        
                        # Download
                        output_path = os.path.join(output_dir, f"broll_{i}.mp4")
                        video_data = requests.get(video_url, timeout=30)
                        
                        with open(output_path, 'wb') as f:
                            f.write(video_data.content)
                        
                        clips_paths.append(output_path)
                        logger.info(f"✅ Pexels B-roll {i+1} downloaded")
            except Exception as e:
                logger.error(f"❌ Pexels sequence fetch failed: {e}")
        
        # Fill remaining with Pixabay if needed
        if len(clips_paths) < count and self.pixabay_key:
            try:
                needed = count - len(clips_paths)
                url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={query}&per_page={needed + 3}"
                
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if data.get('hits'):
                    for i, hit in enumerate(data['hits']):
                        if len(clips_paths) >= count: break
                        
                        videos = hit.get('videos', {})
                        video_url = videos.get('medium', {}).get('url')
                        
                        if video_url:
                            output_path = os.path.join(output_dir, f"broll_pixabay_{i}.mp4")
                            video_data = requests.get(video_url, timeout=30)
                            
                            with open(output_path, 'wb') as f:
                                f.write(video_data.content)
                            
                            clips_paths.append(output_path)
                            logger.info(f"✅ Pixabay B-roll downloaded")
            except Exception as e:
                logger.error(f"❌ Pixabay sequence fetch failed: {e}")
                
        return clips_paths

# ==================== VIDEO COMPOSER ====================
class VideoComposer:
    """Compose final video with all elements (memory optimized)"""
    
    def __init__(self):
        self.voice_gen = AIVoiceGenerator()
        self.sub_gen = SimpleSubtitleGenerator()
        self.broll = BRollFetcher()
    
    def create_short(self, script: Dict, output_path: str) -> str:
        """Create complete YouTube Short (optimized for low memory)"""
        try:
            logger.info("🎬 Starting video creation...")
            
            # Step 1: Generate voiceover
            voice_path = VideoGenConfig.TEMP_DIR / "voice.mp3"
            self.voice_gen.generate_voice(script['narration'], str(voice_path))
            
            # Step 2: Get video duration from audio
            audio = AudioFileClip(str(voice_path))
            duration = min(audio.duration, VideoGenConfig.DURATION)
            
            # Step 3: Create background
            broll_path = VideoGenConfig.TEMP_DIR / "broll.mp4"
            
            # Try Pexels first, then Pixabay
            fetched = self.broll.fetch_pexels_video(script.get('topic', 'technology'), str(broll_path))
            if not fetched:
                fetched = self.broll.fetch_pixabay_video(script.get('topic', 'technology'), str(broll_path))
            
            if fetched and os.path.exists(fetched):
                bg_video = VideoFileClip(fetched)
                bg_video = bg_video.subclip(0, min(duration, bg_video.duration))
            else:
                # Fallback: Solid gradient background
                logger.warning("⚠️ Using fallback background")
                bg_video = ColorClip(
                    size=(VideoGenConfig.WIDTH, VideoGenConfig.HEIGHT),
                    color=(20, 20, 60),
                    duration=duration
                )
            
            # Resize and crop to vertical format
            if bg_video.w != VideoGenConfig.WIDTH or bg_video.h != VideoGenConfig.HEIGHT:
                bg_video = bg_video.fx(resize, height=VideoGenConfig.HEIGHT)
                bg_video = bg_video.crop(
                    x_center=bg_video.w/2,
                    width=VideoGenConfig.WIDTH,
                    height=VideoGenConfig.HEIGHT
                )
            
            # Step 4: Generate simple captions
            caption_clips = self.sub_gen.create_simple_captions(
                script['narration'],
                duration,
                (VideoGenConfig.WIDTH, VideoGenConfig.HEIGHT)
            )
            
            # Step 5: Add hook text at start (Professional Style)
            try:
                hook_text = script['hook'].upper()[:50]
                
                # Main Hook Text
                hook_clip = TextClip(
                    hook_text,
                    fontsize=75,
                    font='Arial-Bold',
                    color='#FFD700',  # Gold/Yellow
                    stroke_color='black',
                    stroke_width=3,
                    method='caption',
                    size=(VideoGenConfig.WIDTH - 100, None),
                    align='center'
                ).set_position(('center', 250)).set_duration(3.5)
                
                # Apply fadein effect correctly
                hook_clip = hook_clip.fx(fadein, 0.5)
                
            except Exception as e:
                logger.warning(f"⚠️ Hook text skipped: {e}")
                hook_clip = None
            except Exception as e:
                logger.warning(f"⚠️ Hook text skipped: {e}")
                hook_clip = None
            
            # Step 6: Add CTA at end (Professional Style)
            try:
                cta_text = script['cta'].upper()
                
                cta_clip = TextClip(
                    cta_text,
                    fontsize=60,
                    font='Arial-Bold',
                    color='white',
                    bg_color='#CC0000',  # Dark Red background
                    method='caption',
                    size=(VideoGenConfig.WIDTH - 200, None),
                    align='center'
                ).set_position(('center', 1400)).set_start(max(0, duration - 4)).set_duration(4)
                
                # Add a "Subscribe" hint
                sub_clip = TextClip(
                    "SUBSCRIBE FOR MORE",
                    fontsize=40,
                    font='Arial-Bold',
                    color='white',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    align='center'
                ).set_position(('center', 1550)).set_start(max(0, duration - 4)).set_duration(4)
                
            except Exception as e:
                logger.warning(f"⚠️ CTA text skipped: {e}")
                cta_clip = None
                sub_clip = None
            except Exception as e:
                logger.warning(f"⚠️ CTA text skipped: {e}")
                cta_clip = None
            
            # Step 7: Composite everything
            all_clips = [bg_video]
            if hook_clip:
                all_clips.append(hook_clip)
            if cta_clip:
                all_clips.append(cta_clip)
            if 'sub_clip' in locals() and sub_clip:
                all_clips.append(sub_clip)
            all_clips.extend(caption_clips)
            
            final_video = CompositeVideoClip(
                all_clips,
                size=(VideoGenConfig.WIDTH, VideoGenConfig.HEIGHT)
            )
            
            # Step 8: Add audio
            final_video = final_video.set_audio(audio)
            
            # Step 9: Export with optimal settings for low memory
            final_video.write_videofile(
                output_path,
                fps=VideoGenConfig.FPS,
                codec='libx264',
                audio_codec='aac',
                bitrate='4000k',  # Lower bitrate for memory
                preset='ultrafast',  # Faster encoding, less memory
                threads=2  # Limit threads
            )
            
            logger.info(f"✅ Video created: {output_path}")
            
            # Cleanup
            audio.close()
            bg_video.close()
            final_video.close()
            
            # Delete temp files to save space
            try:
                if os.path.exists(voice_path):
                    os.remove(voice_path)
                if os.path.exists(broll_path):
                    os.remove(broll_path)
            except:
                pass
            
            return output_path
        
        except Exception as e:
            logger.error(f"❌ Video creation failed: {e}")
            raise

# ==================== MAIN PIPELINE ====================
class VideoGenerationPipeline:
    """Complete video generation pipeline (Render optimized)"""
    
    def __init__(self):
        VideoGenConfig.init_dirs()
        self.composer = VideoComposer()
        
        # Setup Cloudinary if available
        if VideoGenConfig.CLOUDINARY_ENABLED:
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
    
    def generate_single_video(self, script: Dict, output_filename: str = None) -> str:
        """Generate a single video"""
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"short_{timestamp}.mp4"
        
        output_path = VideoGenConfig.OUTPUT_DIR / output_filename
        video_path = self.composer.create_short(script, str(output_path))
        
        # Upload to Cloudinary if enabled
        if VideoGenConfig.CLOUDINARY_ENABLED:
            try:
                logger.info("☁️ Uploading to Cloudinary...")
                result = cloudinary.uploader.upload_large(
                    video_path,
                    resource_type="video",
                    folder="faceless_videos",
                    chunk_size=6000000
                )
                logger.info(f"✅ Cloudinary URL: {result['secure_url']}")
                
                # Delete local file after upload to save space
                os.remove(video_path)
                logger.info("🗑️ Local file deleted (saved to Cloudinary)")
                
                return result['secure_url']
            except Exception as e:
                logger.error(f"❌ Cloudinary upload failed: {e}")
        
        return video_path
    
    def run_full_pipeline(self, analysis: Dict) -> Dict:
        """Run full pipeline from analysis to video generation"""
        try:
            logger.info("🚀 Running full pipeline...")
            
            # Build script from analysis
            script = {
                'narration': f"{analysis.get('short_hook', 'Check this out')}. {analysis.get('summary', '')[:200]}. {analysis.get('cta', 'Try it now')}",
                'hook': analysis.get('short_hook', 'Amazing AI Tool'),
                'cta': analysis.get('cta', 'Link in bio'),
                'topic': analysis.get('key_topics', 'AI technology').split(',')[0]
            }
            
            # Generate video
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_url = self.generate_single_video(script, f"ai_short_{timestamp}.mp4")
            
            results = {
                'videos': {
                    'youtube': video_url
                },
                'youtube_url': video_url,
                'script': script,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("✅ Full pipeline complete")
            return results
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise

# ==================== USAGE EXAMPLE ====================
def main():
    """Example usage"""
    
    # Initialize pipeline
    pipeline = VideoGenerationPipeline()
    
    # Example script
    script = {
        'narration': "This AI tool will change everything. CustomGPT lets you build custom chatbots in minutes. No coding required. Try it now with the link in bio.",
        'hook': "This AI Tool is Insane",
        'cta': "Link in Bio - Try Free",
        'topic': "AI technology"
    }
    
    video_path = pipeline.generate_single_video(script)
    print(f"✅ Video generated: {video_path}")

if __name__ == "__main__":
    main()

# Aliases for compatibility
FacelessAutomationPipeline = VideoGenerationPipeline
FreeConfig = VideoGenConfig
