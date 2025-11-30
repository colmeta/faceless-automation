#!/usr/bin/env python3
"""
👑 MASTER AUTOMATION - FIXED FOR MOVIEPY 2.X & RENDER 512MB
✅ MoviePy 2.x compatibility (all with_* methods)
✅ URL-encoded API requests
✅ Graceful fallbacks (assets folder → ColorClip)
✅ Memory optimized for Render free tier
"""

import os
import sys
import json
import logging
import asyncio
import requests
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_automation.log'),
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
            from youtube_transcript_api import YouTubeTranscriptApi
            
            logger.info(f"🔍 Fetching transcript for {video_id}...")
            
            # ✅ FIXED: Direct static method call (this is the correct way)
            try:
                captions = YouTubeTranscriptApi.get_transcript(video_id)
                full_text = " ".join([item['text'] for item in captions])
                logger.info(f"✅ Transcript retrieved: {len(full_text)} chars")
                return full_text
                
            except Exception as e:
                logger.warning(f"⚠️ English transcript failed, trying any language...")
                
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
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
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
        """Create default analysis when all else fails"""
        return {
            'short_hook': 'This AI Strategy Changed Everything',
            'summary': 'Discover the power of AI automation. Transform your workflow with cutting-edge tools. Stop wasting time on manual tasks. Let AI handle the heavy lifting while you focus on what matters. Join thousands who are already using this game-changing technology.',
            'key_topics': 'AI, automation, productivity, technology, innovation',
            'cta': 'Start your free trial today',
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
        
        # Try Pexels first (most reliable)
        if self.pexels_key:
            try:
                query_encoded = urllib.parse.quote(query)
                url = f"https://api.pexels.com/videos/search?query={query_encoded}&per_page={count}&orientation=portrait"
                headers = {"Authorization": self.pexels_key}
                
                logger.info(f"🔍 Pexels API: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('videos'):
                        logger.info(f"✅ Pexels found {len(data['videos'])} videos")
                        
                        for i, video in enumerate(data['videos']):
                            if i >= count: break
                            
                            try:
                                video_files = video['video_files']
                                # Prefer HD, fallback to any available
                                hd_file = next((f for f in video_files if f.get('quality') == 'hd'), video_files[0])
                                video_url = hd_file['link']
                                
                                output_path = os.path.join(output_dir, f"broll_pexels_{i}.mp4")
                                
                                # Download with streaming to save memory
                                video_response = requests.get(video_url, timeout=30, stream=True)
                                video_response.raise_for_status()
                                
                                with open(output_path, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                
                                # Verify file was downloaded
                                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                                    clips_paths.append(output_path)
                                    logger.info(f"✅ Pexels clip {i+1}/{count} downloaded ({os.path.getsize(output_path)} bytes)")
                                else:
                                    logger.warning(f"⚠️ Downloaded file is too small or missing")
                                    
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to download clip {i}: {e}")
                                continue
                            
                        if len(clips_paths) >= count:
                            logger.info(f"🎉 Successfully fetched {len(clips_paths)} clips from Pexels")
                            return clips_paths
                    else:
                        logger.warning(f"⚠️ Pexels returned no videos for query: {query}")
                else:
                    logger.error(f"❌ Pexels API error: {response.status_code} - {response.text[:200]}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Pexels fetch failed: {e}")

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
    
    def generate_voice_and_video(self, script: dict, output_path: str) -> str:
        """Generate voice and create video - FULLY FIXED"""
        try:
            from moviepy import (
                ColorClip, TextClip, CompositeVideoClip, 
                AudioFileClip, concatenate_videoclips, VideoFileClip, ImageClip, vfx
            )
            
            logger.info("🎬 Starting video creation...")
            
            # STEP 1: Generate voice
            narration = script.get('narration', '')
            if not narration:
                narration = f"{script['hook']}. {script.get('cta', 'Try it now')}."
            
            voice_path = "temp/voice.mp3"
            os.makedirs("temp", exist_ok=True)
            
            logger.info(f"🔊 Generating voice: '{narration[:50]}...'")
            
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
            
            # STEP 2: Get audio duration
            audio = AudioFileClip(voice_path)
            actual_duration = audio.duration
            
            logger.info(f"⏱️ Audio duration: {actual_duration:.2f} seconds")
            
            # STEP 3: Create background (FIXED FALLBACK CHAIN)
            background = None
            
            # Try 1: Dynamic B-roll
            topic = script.get('topic', 'technology')
            broll_dir = "temp/broll_seq"
            os.makedirs(broll_dir, exist_ok=True)
            
            num_clips = max(3, int(actual_duration / 4))
            
            logger.info(f"🎞️ Fetching {num_clips} clips for: {topic}")
            fetched_clips = self.broll_fetcher.fetch_broll_sequence(topic, num_clips, broll_dir)
            
            if fetched_clips:
                logger.info(f"✅ Using {len(fetched_clips)} dynamic clips")
                clip_objs = []
                
                total_dur = 0
                target_clip_dur = actual_duration / len(fetched_clips)
                
                for i, clip_path in enumerate(fetched_clips):
                    try:
                        clip = VideoFileClip(clip_path)
                        
                        # ✅ FIXED: MoviePy 2.x syntax
                        clip = clip.resized(height=1920)
                        if clip.w < 1080:
                            clip = clip.resized(width=1080)
                        
                        # ✅ FIXED: with_effects instead of fx
                        clip = clip.with_effects([
                            vfx.Crop(x1=int(clip.w/2 - 540), width=1080, height=1920)
                        ])
                        
                        if i == len(fetched_clips) - 1:
                            dur = max(0, actual_duration - total_dur)
                        else:
                            dur = target_clip_dur
                        
                        if clip.duration < dur:
                            clip = clip.with_effects([vfx.Loop(duration=dur)])
                        else:
                            clip = clip.subclipped(0, dur)
                            
                        clip_objs.append(clip)
                        total_dur += dur
                    except Exception as e:
                        logger.warning(f"⚠️ Clip {i} failed: {e}")
                
                if clip_objs:
                    background = concatenate_videoclips(clip_objs, method="compose")
            
            # Try 2: Assets folder video
            if background is None:
                local_bg = "assets/background.mp4"
                if os.path.exists(local_bg):
                    logger.info(f"📂 Using assets/background.mp4")
                    video_clip = VideoFileClip(local_bg)
                    
                    if video_clip.duration < actual_duration:
                        video_clip = video_clip.with_effects([vfx.Loop(duration=actual_duration)])
                    else:
                        video_clip = video_clip.subclipped(0, actual_duration)
                    
                    background = video_clip.resized(height=1920)
                    if background.w < 1080:
                        background = background.resized(width=1080)
                    
                    background = background.with_effects([
                        vfx.Crop(x1=int(background.w/2 - 540), width=1080, height=1920)
                    ])
            
            # Try 3: Assets folder image
            if background is None:
                local_img = "assets/background.jpg"
                if os.path.exists(local_img):
                    logger.info(f"📂 Using assets/background.jpg")
                    img = ImageClip(local_img)
                    
                    background = img.resized(height=1920)
                    if background.w < 1080:
                        background = background.resized(width=1080)
                    
                    background = background.with_effects([
                        vfx.Crop(x_center=background.w/2, y_center=background.h/2, width=1080, height=1920)
                    ])
                    
                    # ✅ FIXED: with_duration, with_position
                    background = background.with_duration(actual_duration)
                    background = background.with_position(('center', 'center'))
            
            # Try 4: ColorClip fallback (never crashes)
            if background is None:
                logger.warning("⚠️ Using ColorClip fallback")
                background = ColorClip(
                    size=(1080, 1920),
                    color=(20, 20, 60),
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
            
            final_video = CompositeVideoClip(clips, size=(1080, 1920))
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
                threads=2,
                logger=None  # Removed verbose parameter (MoviePy 2.x)
            )
            
            logger.info(f"✅ Video created: {output_path} ({actual_duration:.2f}s)")
            
            # Cleanup
            audio.close()
            background.close()
            final_video.close()
            
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
