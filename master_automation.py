#!/usr/bin/env python3
"""
👑 MASTER AUTOMATION - FIXED FOR MOVIEPY 2.X & RENDER 512MB
✅ MoviePy 2.x compatibility (all with_* methods)
✅ URL-encoded API requests
✅ Graceful fallbacks (assets folder → ColorClip)
✅ Memory optimized for Render free tier
"""

import os
import gc
import sys
import json
import logging
import asyncio
import requests
import urllib.parse
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import io
try:
    from avatar_automation_system import AvatarGenerator
    AVATAR_SYSTEM_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Avatar system not found, skipping")
    AVATAR_SYSTEM_AVAILABLE = False

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import content templates for variation
try:
    from content_templates import (
        generate_unique_script,
        get_timestamp_based_script,
        get_random_color_scheme,
        get_timestamp_color_scheme
    )
    TEMPLATES_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ content_templates.py not found, using basic variation")
    TEMPLATES_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== YOUTUBE TRANSCRIPT ====================
class YouTubeTranscriptFixer:
    """Fixed YouTube transcript extraction"""
    
    @staticmethod
    def get_transcript(video_id: str) -> str:
        """Get transcript with fallback support"""
        try:
            # ✅ FIXED: Robust Import
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
            except ImportError:
                logger.error("❌ youtube_transcript_api not installed!")
                return None
            
            logger.info(f"🔍 Fetching transcript for {video_id}...")
            
            try:
                # Try to get English transcript directly
                # Note: Some versions might need instantiation, though it's usually static
                captions = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
                full_text = " ".join([item['text'] for item in captions])
                logger.info(f"✅ Transcript retrieved: {len(full_text)} chars")
                return full_text
                
            except Exception as e:
                logger.warning(f"⚠️ English transcript failed, trying list_transcripts: {e}")
                
                # Try to get any available transcript
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # Try to find English first
                    try:
                        transcript = transcript_list.find_transcript(['en'])
                    except:
                        # Get first available transcript
                        transcript = next(iter(transcript_list))
                        logger.info(f"Using transcript language: {transcript.language}")
                    
                    captions = transcript.fetch()
                    full_text = " ".join([item['text'] for item in captions])
                    logger.info(f"✅ Transcript retrieved: {len(full_text)} chars")
                    return full_text
                    
                except Exception as e2:
                    logger.error(f"❌ All transcript methods failed: {e2}")
                    return None
        
        except Exception as e:
            logger.error(f"❌ Transcript error: {e}")
            return None

# ==================== SAFE ANALYZER ====================
class SafeAnalyzer:
    """Analyze content with guaranteed output fields"""
    
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    def analyze_transcript(self, transcript: str) -> dict:
        """Analyze with all required fields guaranteed"""
        try:
            logger.info("🔵 Analyzing with Gemini...")
            
            prompt = """Analyze this transcript and return ONLY valid JSON with these exact fields:
{
    "short_hook": "10-word attention-grabbing hook",
    "summary": "One paragraph summary",
    "key_topics": "topic1, topic2, topic3",
    "cta": "Call to action text",
    "affiliate_angle": "AI tools"
}
IMPORTANT: Return ONLY the JSON object, nothing else."""
            
            response = self.model.generate_content(f"{prompt}\n\nTranscript:\n{transcript[:5000]}")
            text = response.text.strip()
            
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            
            if json_match:
                analysis = json.loads(json_match.group())
                logger.info("✅ Analysis complete")
                return self._ensure_fields(analysis)
            else:
                logger.warning("⚠️ Could not parse JSON, using defaults")
                return self._create_default_analysis()
        
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return self._create_default_analysis()
    
    def _ensure_fields(self, analysis: dict) -> dict:
        """Ensure all required fields exist"""
        defaults = {
            'short_hook': 'This AI Tool is Amazing',
            'summary': 'An excellent AI tool that will help you achieve more.',
            'key_topics': 'AI, tools, automation',
            'cta': 'Try it free now',
            'affiliate_angle': 'AI tools'
        }
        
        for key, default_value in defaults.items():
            if key not in analysis or not analysis[key]:
                logger.warning(f"⚠️ Missing field '{key}', using default")
                analysis[key] = default_value
        
        return analysis
    
    def _create_default_analysis(self) -> dict:
        """Create default analysis with VARIATION to avoid duplicate videos"""
        if TEMPLATES_AVAILABLE:
            # Use timestamp-based selection for reproducible variety
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script = get_timestamp_based_script(timestamp)
            
            return {
                'short_hook': script['hook'],
                'summary': script['narration'],
                'key_topics': script['topic']['keywords'],
                'cta': script['cta'],
                'affiliate_angle': script['topic']['focus']
            }
        else:
            # Basic variation using lists when templates not available
            hooks = [
                'This AI Strategy Changed Everything',
                'Stop Wasting Time on This',
                'The Tool Nobody Talks About',
                'This Mistake Costs You Hours',
                'The Hidden Productivity Hack'
            ]
            
            narrations = [
                'Discover the power of AI automation. Transform your workflow with cutting-edge tools. Stop wasting time on manual tasks.',
                'Most people waste hours on repetitive work. But there\'s a smarter way. This AI tool handles it automatically.',
                'What if you could save 10 hours this week? This innovation makes it possible. Join thousands already using it.',
                'Traditional methods are outdated. This game-changing platform revolutionizes how you work. Pure efficiency.',
                'You\'re doing productivity wrong. Everyone is. This automated solution fixes it instantly. Zero struggle.'
            ]
            
            topics = [
                'AI, automation, productivity',
                'technology, efficiency, tools',
                'innovation, workflow, business',
                'software, automation, growth',
                'productivity, time management, success'
            ]
            
            ctas = [
                'Start your free trial today',
                'Try it free now',
                'Get instant access',
                'Join thousands of users',
                'Transform your workflow'
            ]
            
            # Use timestamp to select from lists
            seed = int(datetime.now().strftime("%H%M%S"))
            idx = seed % len(hooks)
            
            return {
                'short_hook': hooks[idx],
                'summary': narrations[idx],
                'key_topics': topics[idx],
                'cta': ctas[idx],
                'affiliate_angle': 'AI Productivity Tools'
            }

# ==================== B-ROLL FETCHER (FIXED) ====================
class BRollFetcher:
    """Fetch stock footage with URL encoding"""
    
    def __init__(self):
        self.pexels_key = os.getenv('PEXELS_API_KEY', '').strip()
        self.pixabay_key = os.getenv('PIXABAY_API_KEY', '').strip()
    
    def fetch_broll_sequence(self, query: str, count: int, output_dir: str) -> List[str]:
        """Fetch a sequence of unique B-roll videos with robust fallbacks"""
        clips_paths = []
        
        logger.info(f"🎬 Fetching {count} B-roll clips for: '{query}'")
        
        # If primary query fails, try these fallback queries
        fallback_queries = [query, "business office", "technology innovation", "modern workspace", "digital technology"]
        
        for attempt, search_query in enumerate(fallback_queries):
            if len(clips_paths) >= count:
                break  # We have enough clips
            
            logger.info(f"🔍 Attempt {attempt + 1}/{len(fallback_queries)}: Searching for '{search_query}'")
            
            # Try Pexels first (most reliable)
            if self.pexels_key:
                try:
                    query_encoded = urllib.parse.quote(search_query)
                    url = f"https://api.pexels.com/videos/search?query={query_encoded}&per_page={count}&orientation=portrait"
                    headers = {"Authorization": self.pexels_key}
                    
                    logger.info(f"🔍 Pexels API: {url}")
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('videos'):
                            logger.info(f"✅ Pexels found {len(data['videos'])} videos for '{search_query}'")
                            
                            for i, video in enumerate(data['videos']):
                                if len(clips_paths) >= count: break
                                
                                try:
                                    video_files = video['video_files']
                                    
                                    # 🧠 SMART SELECTION: Avoid 4K to prevent OOM on Render
                                    # Filter for files <= 1080p (1920x1080)
                                    valid_files = [
                                        f for f in video_files 
                                        if f.get('width') and f.get('height') 
                                        and f['width'] <= 1920 and f['height'] <= 1920
                                    ]
                                    
                                    if not valid_files:
                                        # Fallback if no HD/SD found (rare)
                                        valid_files = video_files
                                    
                                    # Find best match: closest to 720p width (optimal for mobile)
                                    best_file = min(valid_files, key=lambda x: abs(x.get('width', 0) - 720))
                                    video_url = best_file['link']
                                    
                                    logger.info(f"🎥 Selected quality: {best_file.get('width')}x{best_file.get('height')} (avoiding 4K)")
                                    
                                    # Force GC before download
                                    gc.collect()
                                    
                                    output_path = os.path.join(output_dir, f"broll_pexels_{len(clips_paths)}.mp4")
                                    
                                    logger.info(f"📥 Downloading clip {len(clips_paths)+1}: {video_url[:60]}...")
                                    
                                    # ✅ INCREASED TIMEOUT: 60 seconds instead of 30
                                    video_response = requests.get(video_url, timeout=60, stream=True)
                                    video_response.raise_for_status()
                                    
                                    bytes_written = 0
                                    with open(output_path, 'wb') as f:
                                        for chunk in video_response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                            bytes_written += len(chunk)
                                    
                                    # Verify file was downloaded (must be > 100KB)
                                    file_size = os.path.getsize(output_path)
                                    if os.path.exists(output_path) and file_size > 100000:
                                        clips_paths.append(output_path)
                                        logger.info(f"✅ Pexels clip {len(clips_paths)}/{count} downloaded: {file_size / 1024 / 1024:.2f} MB")
                                    else:
                                        logger.warning(f"⚠️ Downloaded file is too small: {file_size} bytes (expected > 100KB)")
                                        if os.path.exists(output_path):
                                            os.remove(output_path)
                                        
                                except Exception as e:
                                    logger.warning(f"⚠️ Failed to download clip {i}: {str(e)[:100]}")
                                    continue
                                
                            if len(clips_paths) >= count:
                                logger.info(f"🎉 Successfully fetched {len(clips_paths)} clips from Pexels")
                                return clips_paths
                        else:
                            logger.warning(f"⚠️ Pexels returned no videos for query: {search_query}")
                    else:
                        logger.error(f"❌ Pexels API error: {response.status_code} - {response.text[:200]}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Pexels fetch failed for '{search_query}': {e}")

        # Try Pixabay if needed (with improved error handling)
        if len(clips_paths) < count and self.pixabay_key:
            try:
                needed = count - len(clips_paths)
                query_encoded = urllib.parse.quote(query)
                url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={query_encoded}&per_page={needed + 5}"
                
                logger.info(f"🔍 Pixabay API: {url[:100]}...")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get('hits', [])
                    
                    if hits:
                        logger.info(f"✅ Pixabay found {len(hits)} videos")
                        
                        for i, hit in enumerate(hits):
                            if len(clips_paths) >= count: break
                            
                            try:
                                videos = hit.get('videos', {})
                                # Try different quality levels
                                video_url = (videos.get('medium', {}).get('url') or 
                                           videos.get('small', {}).get('url') or
                                           videos.get('tiny', {}).get('url'))
                                
                                if video_url:
                                    output_path = os.path.join(output_dir, f"broll_pixabay_{i}.mp4")
                                    
                                    # Download with streaming
                                    video_response = requests.get(video_url, timeout=30, stream=True)
                                    video_response.raise_for_status()
                                    
                                    with open(output_path, 'wb') as f:
                                        for chunk in video_response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    
                                    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                                        clips_paths.append(output_path)
                                        logger.info(f"✅ Pixabay clip {len(clips_paths)}/{count} downloaded")
                                    else:
                                        logger.warning(f"⚠️ Downloaded file is too small")
                                        
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to download Pixabay clip {i}: {e}")
                                continue
                    else:
                        logger.warning(f"⚠️ Pixabay returned no videos for query: {query}")
                else:
                    logger.error(f"❌ Pixabay API error: {response.status_code}")
                    logger.error(f"Response: {response.text[:500]}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Pixabay fetch failed: {e}")
        
        # Fallback: Try Pexels trending/popular if we still don't have enough
        if len(clips_paths) < count and self.pexels_key:
            logger.info(f"🔄 Trying Pexels popular videos as fallback...")
            try:
                needed = count - len(clips_paths)
                url = f"https://api.pexels.com/videos/popular?per_page={needed}&orientation=portrait"
                headers = {"Authorization": self.pexels_key}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('videos'):
                        for i, video in enumerate(data['videos']):
                            if len(clips_paths) >= count: break
                            
                            try:
                                video_files = video['video_files']
                                hd_file = next((f for f in video_files if f.get('quality') == 'hd'), video_files[0])
                                video_url = hd_file['link']
                                
                                output_path = os.path.join(output_dir, f"broll_popular_{i}.mp4")
                                
                                video_response = requests.get(video_url, timeout=30, stream=True)
                                video_response.raise_for_status()
                                
                                with open(output_path, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                
                                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                                    clips_paths.append(output_path)
                                    logger.info(f"✅ Popular clip {len(clips_paths)}/{count} downloaded")
                                    
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to download popular clip: {e}")
                                continue
                                
            except Exception as e:
                logger.warning(f"⚠️ Pexels popular fetch failed: {e}")
        
        if clips_paths:
            logger.info(f"🎉 Total clips fetched: {len(clips_paths)}/{count}")
        else:
            logger.error(f"❌ Failed to fetch any B-roll clips!")
            
        return clips_paths

# ==================== VIDEO COMPOSER (MOVIEPY 2.X FIXED) ====================
class VideoComposerFixed:
    """MoviePy 2.x compatible video composer"""
    
    def __init__(self):
        self.broll_fetcher = BRollFetcher()
    
    def resize_with_ffmpeg(self, input_path: str, output_path: str, width: int, height: int) -> bool:
        """Resize video using FFmpeg CLI to save memory (MoviePy is too RAM heavy)"""
        try:
            import subprocess
            
            # Scale and crop to fill 720x1280 (9:16)
            # scale=-1:1280 sets height to 1280 and keeps aspect ratio
            # crop=720:1280 centers the crop
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-vf', f'scale=-1:{height},crop={width}:{height}:(iw-{width})/2:0,setsar=1',
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '28',
                '-an',  # Remove audio from B-roll
                output_path
            ]
            
            logger.info(f"🎞️ FFmpeg resizing: {input_path} -> {output_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True
            else:
                logger.warning(f"⚠️ FFmpeg failed: {result.stderr[:200]}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ FFmpeg error: {e}")
            return False

            return False

    def create_background_with_ffmpeg(self, clips_paths: List[str], total_duration: float) -> str:
        """
        Create background video using ONLY FFmpeg (Zero RAM usage in Python)
        1. Resize & Trim each clip
        2. Concat all clips
        3. Return path to single background video
        """
        try:
            import subprocess
            
            processed_clips = []
            target_duration = total_duration / len(clips_paths)
            
            # Step 1: Process each clip (Resize + Crop + Trim)
            for i, clip_path in enumerate(clips_paths):
                output_path = clip_path.replace(".mp4", f"_processed_{i}.mp4")
                
                # Calculate duration for this clip
                if i == len(clips_paths) - 1:
                    # Last clip takes remaining time to ensure exact match
                    # We add 0.5s buffer to be safe, MoviePy will trim final result
                    duration = target_duration + 1.0 
                else:
                    duration = target_duration
                
                # FFmpeg command: Resize -> Crop -> Trim
                # scale=-1:1280 (height 1280, keep aspect)
                # crop=720:1280 (center crop)
                # -t {duration} (trim length)
                cmd = [
                    'ffmpeg', '-y',
                    '-i', clip_path,
                    '-vf', f'scale=-1:1280,crop=720:1280:(iw-720)/2:0,setsar=1',
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-preset', 'ultrafast',
                    '-crf', '28',
                    '-an',
                    output_path
                ]
                
                logger.info(f"🎞️ Processing clip {i+1}/{len(clips_paths)} via FFmpeg...")
                subprocess.run(cmd, check=True, capture_output=True)
                
                if os.path.exists(output_path):
                    processed_clips.append(output_path)
            
            # Step 2: Create Concat List
            if not processed_clips:
                return None
                
            concat_list_path = "temp/concat_list.txt"
            with open(concat_list_path, 'w') as f:
                for path in processed_clips:
                    # FFmpeg requires absolute paths or safe relative paths
                    # We use absolute to be safe
                    abs_path = os.path.abspath(path).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
            
            # Step 3: Concatenate
            final_bg_path = "temp/final_background.mp4"
            concat_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list_path,
                '-c', 'copy',
                final_bg_path
            ]
            
            logger.info("🔗 Concatenating clips via FFmpeg...")
            subprocess.run(concat_cmd, check=True, capture_output=True)
            
            if os.path.exists(final_bg_path):
                logger.info(f"✅ Background created: {final_bg_path}")
                return final_bg_path
            
            return None
            
        except Exception as e:
            logger.error(f"❌ FFmpeg background creation failed: {e}")
            return None

    def generate_voice_and_video(self, script: dict, output_path: str) -> str:
        """Generate voice and create video - FULLY FIXED"""
        try:
            from moviepy import (
                TextClip, CompositeVideoClip, 
                AudioFileClip, concatenate_videoclips, VideoFileClip, ImageClip, vfx
            )
            from moviepy.video.VideoClip import ColorClip
            logger.info("🎬 Starting video creation...")
            
            # STEP 1: Generate Content (Avatar or Voice+B-roll)
            narration = script.get('narration', '')
            if not narration:
                narration = f"{script['hook']}. {script.get('cta', 'Try it now')}."
            
            voice_path = "temp/voice.mp3"
            os.makedirs("temp", exist_ok=True)
            
            background = None
            audio = None
            actual_duration = 0
            
            # ---------------------------------------------------------
            # 🤖 AVATAR GENERATION (Priority)
            # ---------------------------------------------------------
            if AVATAR_SYSTEM_AVAILABLE:
                try:
                    logger.info("🤖 Attempting Avatar Generation...")
                    avatar_gen = AvatarGenerator()
                    
                    # Use the raw GitHub URL for the avatar image
                    avatar_url = "https://raw.githubusercontent.com/colmeta/faceless-automation/main/ghgh.jpg"
                    
                    # Generate video
                    avatar_result = avatar_gen.generate_video(narration, avatar_url, provider="d-id")
                    
                    if avatar_result and avatar_result.get('video_url'):
                        video_url = avatar_result['video_url']
                        logger.info(f"✅ Avatar video generated: {video_url}")
                        
                        # Download the video
                        avatar_video_path = "temp/avatar_raw.mp4"
                        logger.info(f"⬇️ Downloading avatar video...")
                        response = requests.get(video_url, stream=True)
                        response.raise_for_status()
                        
                        with open(avatar_video_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                
                        if os.path.exists(avatar_video_path) and os.path.getsize(avatar_video_path) > 1000:
                            logger.info("✅ Avatar video downloaded successfully")
                            
                            # Load as background
                            background = VideoFileClip(avatar_video_path)
                            audio = background.audio
                            actual_duration = background.duration
                            
                            # Resize/Crop if needed (D-ID usually returns square or portrait)
                            # We want 720x1280 (9:16)
                            # If it's square, we might need to center it on a background or crop
                            # For now, let's just resize/crop to fill
                            if background.w != 720 or background.h != 1280:
                                logger.info(f"📐 Resizing avatar video from {background.w}x{background.h} to 720x1280")
                                # Simple resize to cover (might crop head) - better to fit width and center?
                                # Let's try to fit width=720, then center vertically
                                background = background.resized(width=720)
                                if background.h < 1280:
                                    # If too short, we need a background layer?
                                    # Or just resize height to 1280 (might stretch)
                                    # Or resize to fill height=1280 (might crop sides)
                                    background = background.resized(height=1280)
                                    background = background.with_effects([vfx.Crop(x1=int((background.w-720)/2), width=720, height=1280)])
                                else:
                                    # If too tall, crop center
                                    background = background.with_effects([vfx.Crop(y1=int((background.h-1280)/2), width=720, height=1280)])
                            
                except Exception as e:
                    logger.error(f"❌ Avatar generation failed: {e}")
                    background = None
                    audio = None

            # ---------------------------------------------------------
            # 🎤 FALLBACK: Voice Generation (if Avatar failed)
            # ---------------------------------------------------------
            if not audio:
                logger.info(f"🔊 Generating voice (Fallback): '{narration[:50]}...'")
                
                # Try Edge-TTS with retry logic
                edge_tts_success = False
                for attempt in range(3):
                    try:
                        import edge_tts
                        
                        async def generate_voice():
                            voices = ["en-US-ChristopherNeural", "en-US-GuyNeural", "en-US-AriaNeural"]
                            voice = voices[attempt % len(voices)]
                            
                            logger.info(f"🎤 Trying Edge-TTS with {voice} (attempt {attempt + 1}/3)")
                            communicate = edge_tts.Communicate(narration, voice)
                            await communicate.save(voice_path)
                        
                        # Run with timeout
                        asyncio.wait_for(asyncio.run(generate_voice()), timeout=30)
                        
                        if os.path.exists(voice_path) and os.path.getsize(voice_path) > 1000:
                            logger.info("✅ Edge-TTS generation successful")
                            edge_tts_success = True
                            break
                        else:
                            logger.warning(f"⚠️ Edge-TTS file too small or missing")
                            
                    except asyncio.TimeoutError:
                        logger.warning(f"⚠️ Edge-TTS timeout on attempt {attempt + 1}")
                    except Exception as e:
                        logger.warning(f"⚠️ Edge-TTS failed (attempt {attempt + 1}): {e}")
                        
                    if attempt < 2:
                        import time
                        time.sleep(1)  # Brief pause before retry
                
                # Fallback to gTTS if Edge-TTS failed
                if not edge_tts_success:
                    logger.warning(f"⚠️ Edge-TTS failed after 3 attempts, falling back to gTTS...")
                    from gtts import gTTS
                    tts = gTTS(text=narration, lang='en', slow=False)
                    tts.save(voice_path)
                    logger.info("✅ gTTS generation successful (fallback)")
                
                # Get audio duration
                audio = AudioFileClip(voice_path)
                actual_duration = audio.duration
            
            logger.info(f"⏱️ Audio duration: {actual_duration:.2f} seconds")
            
            # STEP 3: Create background (If not already created by Avatar)
            if background is None:
            
                # Try 1: Dynamic B-roll
                topic = script.get('topic', 'technology')
                broll_dir = "temp/broll_seq"
                os.makedirs(broll_dir, exist_ok=True)
            
                # 🧠 MEMORY OPTIMIZATION: Cap max clips to 6 for Render Free Tier
                # Previous logic (duration/4) could request 15+ clips for 60s video -> OOM
                num_clips = min(6, max(3, int(actual_duration / 5)))
            
                logger.info(f"🎞️ Fetching {num_clips} clips for: {topic}")
                fetched_clips = self.broll_fetcher.fetch_broll_sequence(topic, num_clips, broll_dir)
            
                if fetched_clips:
                    logger.info(f"✅ Using {len(fetched_clips)} dynamic clips")
                if fetched_clips:
                    logger.info(f"✅ Using {len(fetched_clips)} dynamic clips")
                
                    # 🚀 NUCLEAR OPTIMIZATION: Use FFmpeg for EVERYTHING
                    # This bypasses MoviePy's memory issues completely by doing all
                    # resizing, trimming, and concatenation in the CLI before Python loads anything.
                    bg_path = self.create_background_with_ffmpeg(fetched_clips, actual_duration)
                
                    if bg_path:
                        logger.info("✅ Loading optimized background video...")
                        background = VideoFileClip(bg_path)
                    else:
                        logger.warning("⚠️ FFmpeg background creation failed, falling back...")
                        # Fallback logic could go here, but we rely on ColorClip fallback later
            

            
                # Try 2: Assets folder video ONLY (no static images!)
                if background is None:
                    local_bg = "assets/background.mp4"
                    if os.path.exists(local_bg):
                        logger.info(f"📂 Using assets/background.mp4")
                        video_clip = VideoFileClip(local_bg)
                    
                        if video_clip.duration < actual_duration:
                            video_clip = video_clip.with_effects([vfx.Loop(duration=actual_duration)])
                        else:
                            video_clip = video_clip.subclipped(0, actual_duration)
                    
                        background = video_clip.resized(height=1280)
                        if background.w < 720:
                            background = background.resized(width=720)
                    
                        background = background.with_effects([
                            vfx.Crop(x1=int(background.w/2 - 360), width=720, height=1280)
                        ])
            
                # ⛔ REMOVED: Static image fallback - we want REAL videos only!
                # Assets folder images are now DISABLED to force dynamic content
            
                # Try 4: ColorClip with VARIED colors (ONLY if all B-roll attempts failed)
                if background is None:
                    logger.error("❌ ========================================")
                    logger.error("❌ CRITICAL: B-ROLL FETCH COMPLETELY FAILED")
                    logger.error(f"❌ Pexels API Key available: {bool(self.broll_fetcher.pexels_key)}")
                    logger.error(f"❌ Pixabay API Key available: {bool(self.broll_fetcher.pixabay_key)}")
                    logger.error(f"❌ Requested clips: {num_clips}")
                    logger.error(f"❌ Fetched clips: {len(fetched_clips) if fetched_clips else 0}")
                    logger.error("❌ Falling back to ColorClip (NOT IDEAL)")
                    logger.error("❌ ========================================")
                
                    logger.warning("⚠️ Using ColorClip with varied colors")
                
                    # Get varied color based on timestamp
                    base_colors = [
                        (20, 20, 60),   # Dark blue
                        (60, 20, 60),   # Purple  
                        (20, 60, 60),   # Teal
                        (60, 30, 20),   # Brown/Orange
                        (20, 40, 60),   # Medium blue
                        (40, 20, 50),   # Deep purple
                        (10, 50, 40),   # Dark green
                        (70, 20, 30),   # Dark red
                        (30, 30, 70),   # Bright blue
                        (50, 40, 10),   # Gold
                    ]
                
                    # Use timestamp to select color (different each run)
                    seed = int(datetime.now().strftime("%H%M%S"))
                    color = base_colors[seed % len(base_colors)]
                
                    logger.info(f"🎨 Using color scheme: RGB{color}")
                
                    background = ColorClip(
                        size=(720, 1280),
                        color=color,
                        duration=actual_duration
                    )
            
            # STEP 4: Add hook text (FIXED)
            try:
                hook_text = TextClip(
                    text=script['hook'][:40].upper(),
                    font_size=60,  # ✅ FIXED: font_size not fontsize
                    color='yellow',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(1000, None)
                ).with_position('center').with_duration(min(3, actual_duration))
                
                hook_text = hook_text.with_effects([vfx.FadeIn(0.5)])
            except Exception as e:
                logger.warning(f"⚠️ Hook text failed: {e}")
                hook_text = None
            
            # STEP 5: Add CTA text (FIXED)
            try:
                cta_text = TextClip(
                    text=script['cta'][:30].upper(),
                    font_size=50,  # ✅ FIXED
                    color='white',
                    bg_color='red',
                    method='caption',
                    size=(1000, None)
                ).with_position(('center', 'bottom')).with_start(
                    max(0, actual_duration - 2)
                ).with_duration(min(2, actual_duration))
            except Exception as e:
                logger.warning(f"⚠️ CTA text failed: {e}")
                cta_text = None
            
            # STEP 6: Composite
            clips = [background]
            if hook_text:
                clips.append(hook_text)
            if cta_text:
                clips.append(cta_text)
            
            final_video = CompositeVideoClip(clips, size=(720, 1280))
            final_video = final_video.with_audio(audio)  # ✅ FIXED
            
            # STEP 7: Export (memory optimized)
            logger.info(f"💾 Writing video to {output_path}...")
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                bitrate='3000k',
                preset='ultrafast',
                threads=1,  # Reduced to 1 for Render 512MB limit
                logger=None  # Removed verbose parameter (MoviePy 2.x)
            )
            
            logger.info(f"✅ Video created: {output_path} ({actual_duration:.2f}s)")
            
            # Cleanup
            audio.close()
            background.close()
            final_video.close()
            
            # Force garbage collection
            gc.collect()
            
            # Delete temp voice file
            try:
                os.remove(voice_path)
            except:
                pass
            
            # Delete B-roll clips to save space
            try:
                import shutil
                if os.path.exists(broll_dir):
                    shutil.rmtree(broll_dir)
                    logger.info("🗑️ B-roll clips deleted to save space")
            except Exception as e:
                logger.warning(f"⚠️ Failed to delete B-roll clips: {e}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Video creation failed: {e}")
            import traceback
            traceback.print_exc()
            raise

# ==================== MASTER ORCHESTRATOR ====================
class MasterOrchestrator:
    """Fixed master automation"""
    
    def __init__(self):
        Path("faceless_empire/videos").mkdir(parents=True, exist_ok=True)
        Path("temp").mkdir(exist_ok=True)
        
        self.transcript_fixer = YouTubeTranscriptFixer()
        self.analyzer = SafeAnalyzer()
        self.video_composer = VideoComposerFixed()
        
        # Initialize YouTube Uploader
        try:
            from youtube_auto_uploader import YouTubeUploader
            self.youtube_uploader = YouTubeUploader()
            logger.info("✅ YouTube Uploader initialized")
        except Exception as e:
            logger.warning(f"⚠️ YouTube Uploader not available: {e}")
            self.youtube_uploader = None
        
        # Initialize Avatar Generator
        if AVATAR_SYSTEM_AVAILABLE:
            self.avatar_generator = AvatarGenerator()
            logger.info("✅ Avatar Generator initialized")
        else:
            self.avatar_generator = None
        
        logger.info("✅ Master Orchestrator initialized")
    
    def run_daily_automation(self):
        """Run complete automation cycle"""
        try:
            logger.info("\n" + "="*80)
            logger.info(f"🚀 DAILY AUTOMATION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80 + "\n")
            
            # PHASE 1: Find video
            logger.info("📍 PHASE 1: Hunting viral videos...")
            
            try:
                from googleapiclient.discovery import build
                youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
                
                request = youtube.search().list(
                    q='Best AI tools 2025',
                    part='snippet',
                    type='video',
                    maxResults=5,
                    order='date'
                )
                
                response = request.execute()
                
                if response['items']:
                    video_id = response['items'][0]['id']['videoId']
                    logger.info(f"✅ Found viral video: {video_id}")
                    
                    transcript = self.transcript_fixer.get_transcript(video_id)
                    
                    if transcript:
                        analysis = self.analyzer.analyze_transcript(transcript)
                    else:
                        logger.warning("⚠️ No transcript, using defaults")
                        analysis = self.analyzer._create_default_analysis()
                else:
                    logger.warning("⚠️ No videos found, using defaults")
                    analysis = self.analyzer._create_default_analysis()
            
            except Exception as e:
                logger.error(f"❌ Video search failed: {e}")
                analysis = self.analyzer._create_default_analysis()
            
            logger.info("✅ Analysis complete")
            
            # PHASE 2: Generate video
            logger.info("\n📍 PHASE 2: Generating video...")
            
            script = {
                'hook': analysis['short_hook'],
                'narration': analysis['summary'],
                'cta': analysis['cta'],
                'topic': analysis.get('key_topics', 'technology').split(',')[0]
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"faceless_empire/videos/video_{timestamp}.mp4"
            
            video_generated = False
            
            # Try Avatar Generation First
            if self.avatar_generator:
                logger.info("🤖 Attempting AI Avatar generation...")
                # Use a default avatar URL or one from env
                avatar_url = os.getenv("AVATAR_IMAGE_URL", "https://img.freepik.com/free-photo/portrait-man-laughing_23-2148859448.jpg")
                
                avatar_result = self.avatar_generator.generate_video(
                    script=script['narration'],
                    avatar_url=avatar_url
                )
                
                if avatar_result and avatar_result.get('video_url'):
                    logger.info(f"✅ Avatar video generated: {avatar_result['video_url']}")
                    # Download the video to output_path
                    try:
                        v_response = requests.get(avatar_result['video_url'])
                        with open(output_path, 'wb') as f:
                            f.write(v_response.content)
                        video_generated = True
                    except Exception as e:
                        logger.error(f"❌ Failed to download avatar video: {e}")
            
            if not video_generated:
                logger.info("🎬 Falling back to Faceless Video generation...")
                self.video_composer.generate_voice_and_video(script, output_path)

            
            logger.info("✅ Video generated successfully")
            
            # PHASE 3: Upload to Cloudinary
            logger.info("\n📍 PHASE 3: Uploading to Cloudinary...")
            
            cloudinary_url = None
            if os.getenv('CLOUDINARY_CLOUD_NAME'):
                try:
                    import cloudinary
                    import cloudinary.uploader
                    
                    cloudinary.config(
                        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                        api_key=os.getenv('CLOUDINARY_API_KEY'),
                        api_secret=os.getenv('CLOUDINARY_API_SECRET')
                    )
                    
                    logger.info("☁️ Uploading to Cloudinary...")
                    result = cloudinary.uploader.upload_large(
                        output_path,
                        resource_type="video",
                        folder="faceless_videos",
                        chunk_size=6000000
                    )
                    
                    cloudinary_url = result['secure_url']
                    logger.info(f"✅ Cloudinary URL: {cloudinary_url}")
                    
                except Exception as e:
                    logger.error(f"⚠️ Cloudinary upload failed: {e}")
            
            # PHASE 4: Upload to YouTube (optional)
            logger.info("\n📍 PHASE 4: YouTube upload...")
            youtube_url = None
            
            if self.youtube_uploader:
                try:
                    hashtags = [tag.strip() for tag in analysis['key_topics'].split(',')]
                    
                    upload_result = self.youtube_uploader.upload_shorts_optimized(
                        video_path=output_path,
                        hook=analysis['short_hook'],
                        topic=analysis['key_topics'],
                        hashtags=hashtags,
                        affiliate_link='https://example.com'
                    )
                    
                    youtube_url = upload_result['url']
                    logger.info(f"✅ YouTube URL: {youtube_url}")
                    
                except Exception as e:
                    logger.error(f"❌ YouTube upload failed: {e}")
            else:
                logger.info("⚠️ YouTube upload skipped (not configured)")
            
            # Cleanup local file
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    logger.info("🗑️ Local file deleted")
                except:
                    pass
            
            logger.info("\n" + "="*80)
            logger.info("🎉 DAILY AUTOMATION COMPLETE!")
            logger.info("="*80 + "\n")
            
            return {
                'status': 'success',
                'analysis': analysis,
                'cloudinary_url': cloudinary_url,
                'youtube_url': youtube_url,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            import traceback
            traceback.print_exc()
            raise

# ==================== MAIN ====================
def main():
    """Entry point"""
    try:
        orchestrator = MasterOrchestrator()
        orchestrator.run_daily_automation()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
