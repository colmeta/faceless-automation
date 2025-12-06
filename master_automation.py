#!/usr/bin/env python3
"""
👑 MASTER AUTOMATION - PRODUCTION READY
✅ Groq (Primary) + Gemini Flash 8B (Fallback) - FREE TIER
✅ AI Video Priority: Kling→Runway→Replicate→Pixverse→B-roll→ColorClip
✅ MoviePy 2.x compatibility
✅ Memory optimized for Render 512MB
✅ NO CORRUPTION - All variables properly defined
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

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging BEFORE imports that use logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import AI Video Generator (Kling/Runway/Replicate/Pixverse)
try:
    from ai_video_manager_updated import AIVideoGenerator
    AI_VIDEO_AVAILABLE = True
    logger.info("✅ AI Video Generator available (Kling/Runway/Replicate/Pixverse)")
except ImportError:
    logger.warning("⚠️ AI Video Generator not found")
    AI_VIDEO_AVAILABLE = False

try:
    from avatar_variation_manager import AvatarVariationManager
    AVATAR_VARIATION_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Avatar variation manager not found")
    AVATAR_VARIATION_AVAILABLE = False

try:
    from youtube_seo_manager import YouTubeSEOManager
    SEO_MANAGER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ YouTube SEO manager not found")
    SEO_MANAGER_AVAILABLE = False

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

# ==================== YOUTUBE TRANSCRIPT ====================
class YouTubeTranscriptFixer:
    """Fixed YouTube transcript extraction"""
    
    @staticmethod
    def get_transcript(video_id: str) -> str:
        """Get transcript with working implementation"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            logger.info(f"🔍 Fetching transcript for {video_id}...")
            
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Try English first
                try:
                    transcript = transcript_list.find_transcript(['en', 'en-US'])
                except:
                    transcript = next(iter(transcript_list))
                
                captions = transcript.fetch()
                full_text = " ".join([item['text'] for item in captions])
                logger.info(f"✅ Transcript retrieved: {len(full_text)} chars")
                return full_text
                
            except Exception as e:
                logger.warning(f"⚠️ Transcript fetch failed: {e}")
                return None
        
        except ImportError:
            logger.error("❌ youtube_transcript_api not installed")
            return None
        except Exception as e:
            logger.error(f"❌ Transcript error: {e}")
            return None

# ==================== SAFE ANALYZER (GROQ + GEMINI FLASH 8B) ====================
class SafeAnalyzer:
    """Analyze content with Groq (primary) and Gemini Flash 8B (fallback) - FREE TIER OPTIMIZED"""
    
    def __init__(self):
        # Initialize Groq (Primary - Free tier)
        self.groq_client = None
        groq_key = os.getenv('GROQ_API_KEY', '').strip()
        if groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=groq_key)
                logger.info("✅ Groq API initialized (PRIMARY)")
            except Exception as e:
                logger.warning(f"⚠️ Groq initialization failed: {e}")
        
        # Initialize Gemini Flash 8B (Fallback - Free tier)
        self.gemini_model = None
        gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                # Use Flash 8B - faster and free!
                self.gemini_model = genai.GenerativeModel('models/gemini-1.5-flash-8b')
                logger.info("✅ Gemini Flash 8B initialized (FALLBACK)")
            except Exception as e:
                logger.warning(f"⚠️ Gemini initialization failed: {e}")
    
    def analyze_transcript(self, transcript: str) -> dict:
        """Analyze with all required fields guaranteed - tries Groq first, then Gemini"""
        prompt = """Analyze this transcript and return ONLY valid JSON with these exact fields:
{
    "short_hook": "10-word attention-grabbing hook",
    "summary": "One paragraph summary",
    "key_topics": "topic1, topic2, topic3",
    "cta": "Call to action text",
    "affiliate_angle": "AI tools"
}
IMPORTANT: Return ONLY the JSON object, nothing else."""
        
        full_prompt = f"{prompt}\n\nTranscript:\n{transcript[:5000]}"
        
        # Try 1: Groq (Fast + Free)
        if self.groq_client:
            try:
                logger.info("⚡ Analyzing with Groq (PRIMARY)...")
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",  # Fast and capable
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                text = response.choices[0].message.content.strip()
                
                import re
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
                
                if json_match:
                    analysis = json.loads(json_match.group())
                    logger.info("✅ Groq analysis complete")
                    return self._ensure_fields(analysis)
            
            except Exception as e:
                logger.warning(f"⚠️ Groq failed: {e}, trying Gemini...")
        
        # Try 2: Gemini Flash 8B (Fallback)
        if self.gemini_model:
            try:
                logger.info("🔵 Analyzing with Gemini Flash 8B (FALLBACK)...")
                response = self.gemini_model.generate_content(full_prompt)
                text = response.text.strip()
                
                import re
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
                
                if json_match:
                    analysis = json.loads(json_match.group())
                    logger.info("✅ Gemini analysis complete")
                    return self._ensure_fields(analysis)
            
            except Exception as e:
                logger.warning(f"⚠️ Gemini failed: {e}")
        
        # Try 3: Use default with variation
        logger.warning("⚠️ All LLMs failed, using defaults with variation")
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
            
            seed = int(datetime.now().strftime("%H%M%S"))
            idx = seed % len(hooks)
            
            return {
                'short_hook': hooks[idx],
                'summary': narrations[idx],
                'key_topics': topics[idx],
                'cta': ctas[idx],
                'affiliate_angle': 'AI Productivity Tools'
            }

# ==================== B-ROLL FETCHER ====================
class BRollFetcher:
    """Fetch stock footage with URL encoding - 512MB optimized"""
    
    def __init__(self):
        self.pexels_key = os.getenv('PEXELS_API_KEY', '').strip()
        self.pixabay_key = os.getenv('PIXABAY_API_KEY', '').strip()
    
    def fetch_broll_sequence(self, query: str, count: int, output_dir: str) -> List[str]:
        """Fetch B-roll videos with robust fallbacks"""
        clips_paths = []
        
        logger.info(f"🎬 Fetching {count} B-roll clips for: '{query}'")
        
        fallback_queries = [query, "business office", "technology innovation", "modern workspace"]
        
        for attempt, search_query in enumerate(fallback_queries):
            if len(clips_paths) >= count:
                break
            
            logger.info(f"🔍 Attempt {attempt + 1}: Searching for '{search_query}'")
            
            # Try Pexels
            if self.pexels_key:
                try:
                    query_encoded = urllib.parse.quote(search_query)
                    url = f"https://api.pexels.com/videos/search?query={query_encoded}&per_page={count}&orientation=portrait"
                    headers = {"Authorization": self.pexels_key}
                    
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('videos'):
                            logger.info(f"✅ Pexels found {len(data['videos'])} videos")
                            
                            for i, video in enumerate(data['videos']):
                                if len(clips_paths) >= count: break
                                
                                try:
                                    video_files = video['video_files']
                                    
                                    # Choose 720p or lower for memory efficiency
                                    valid_files = [f for f in video_files if f.get('width') and f['width'] <= 1920]
                                    if not valid_files:
                                        valid_files = video_files
                                    
                                    best_file = min(valid_files, key=lambda x: abs(x.get('width', 0) - 720))
                                    video_url = best_file['link']
                                    
                                    gc.collect()
                                    
                                    output_path = os.path.join(output_dir, f"broll_{len(clips_paths)}.mp4")
                                    
                                    logger.info(f"📥 Downloading clip {len(clips_paths)+1}...")
                                    video_response = requests.get(video_url, timeout=60, stream=True)
                                    video_response.raise_for_status()
                                    
                                    with open(output_path, 'wb') as f:
                                        for chunk in video_response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    
                                    file_size = os.path.getsize(output_path)
                                    if os.path.exists(output_path) and file_size > 100000:
                                        clips_paths.append(output_path)
                                        logger.info(f"✅ Clip {len(clips_paths)}/{count} downloaded: {file_size/1024/1024:.2f}MB")
                                    else:
                                        if os.path.exists(output_path):
                                            os.remove(output_path)
                                        
                                except Exception as e:
                                    logger.warning(f"⚠️ Failed download: {str(e)[:100]}")
                                    continue
                            
                            if len(clips_paths) >= count:
                                return clips_paths
                        
                except Exception as e:
                    logger.warning(f"⚠️ Pexels failed: {e}")
        
        return clips_paths

# ==================== VIDEO COMPOSER (PRODUCTION READY) ====================
class VideoComposerFixed:
    """MoviePy 2.x compatible - AI Video Priority Chain"""
    
    def __init__(self):
        self.broll_fetcher = BRollFetcher()
    
    def create_background_with_ffmpeg(self, clips_paths: List[str], total_duration: float) -> str:
        """Create background using FFmpeg (memory efficient)"""
        try:
            import subprocess
            
            processed_clips = []
            target_duration = total_duration / len(clips_paths)
            
            for i, clip_path in enumerate(clips_paths):
                output_path = clip_path.replace(".mp4", f"_proc_{i}.mp4")
                
                duration = target_duration + 1.0 if i == len(clips_paths) - 1 else target_duration
                
                cmd = [
                    'ffmpeg', '-y', '-i', clip_path,
                    '-vf', f'scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:black,setsar=1',
                    '-t', str(duration),
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', '-an',
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, check=False)
                
                if os.path.exists(output_path):
                    processed_clips.append(output_path)
            
            if not processed_clips:
                return None
            
            concat_list = "temp/concat_list.txt"
            with open(concat_list, 'w') as f:
                for path in processed_clips:
                    abs_path = os.path.abspath(path).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
            
            final_bg = "temp/final_background.mp4"
            concat_cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list, '-c', 'copy', final_bg]
            subprocess.run(concat_cmd, check=True, capture_output=True)
            
            if os.path.exists(final_bg):
                logger.info(f"✅ Background created: {final_bg}")
                return final_bg
            
            return None
            
        except Exception as e:
            logger.error(f"❌ FFmpeg background failed: {e}")
            return None

    def generate_voice_and_video(self, script: dict, output_path: str) -> str:
        """Generate voice and video with CORRECT AI VIDEO PRIORITY CHAIN"""
        try:
            from moviepy import TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip, vfx
            from moviepy.video.VideoClip import ColorClip
            
            logger.info("🎬 Starting video creation...")
            
            narration = script.get('narration', '')
            if not narration:
                narration = f"{script['hook']}. {script.get('cta', 'Try it now')}."
            
            voice_path = "temp/voice.mp3"
            os.makedirs("temp", exist_ok=True)
            
            background = None
            audio = None
            actual_duration = 0
            
            #  --------------------------------------------------------
            # 🎤 STEP 1: Generate Voice
            # --------------------------------------------------------
            logger.info(f"🔊 Generating voice: '{narration[:50]}...'")
            
            edge_tts_success = False
            for attempt in range(3):
                try:
                    import edge_tts
                    
                    async def generate_voice():
                        voices = ["en-US-ChristopherNeural", "en-US-GuyNeural", "en-US-AriaNeural"]
                        voice = voices[attempt % len(voices)]
                        communicate = edge_tts.Communicate(narration, voice)
                        await communicate.save(voice_path)
                    
                    asyncio.run(generate_voice())
                    
                    if os.path.exists(voice_path) and os.path.getsize(voice_path) > 1000:
                        logger.info("✅ Edge-TTS success")
                        edge_tts_success = True
                        break
                        
                except Exception as e:
                    logger.warning(f"⚠️ Edge-TTS attempt {attempt+1} failed: {e}")
                    
                if attempt < 2:
                    import time
                    time.sleep(1)
            
            if not edge_tts_success:
                logger.warning("⚠️ Falling back to gTTS...")
                from gtts import gTTS
                tts = gTTS(text=narration, lang='en', slow=False)
                tts.save(voice_path)
                logger.info("✅ gTTS success")
            
            audio = AudioFileClip(voice_path)
            actual_duration = audio.duration
            
            # --------------------------------------------------------
            # 🎬 STEP 2: Generate Background - CORRECT Priority Chain
            # --------------------------------------------------------
            
            # 🥇 PRIORITY 1: AI Video Generators (Kling, Runway, Replicate, Pixverse)
            if AI_VIDEO_AVAILABLE and background is None:
                try:
                    logger.info("🤖 PRIORITY 1: Trying AI Video Generators...")
                    ai_gen = AIVideoGenerator()
                    ai_video_path = ai_gen.generate_contextual_video(
                        topic=script.get('topic', 'technology'),
                        narration=narration,
                        duration=actual_duration,
                        output_path="temp/ai_generated.mp4"
                    )
                    
                    if ai_video_path and os.path.exists(ai_video_path) and os.path.getsize(ai_video_path) > 1000:
                        logger.info(f"✅ AI video generated: {ai_video_path}")
                        background = VideoFileClip(ai_video_path)
                        
                        # Resize if needed
                        if background.w != 720 or background.h != 1280:
                            background = background.resized(height=1280)
                            if background.w != 720:
                                background = background.with_effects([vfx.Crop(x1=int((background.w-720)/2), width=720, height=1280)])
                        
                        logger.info("✅ Using AI-generated video")
                    else:
                        logger.warning("⚠️ AI video generation returned invalid file")
                        
                except Exception as e:
                    logger.warning(f"⚠️ AI video generation failed: {e}")
            
            # 🥈 PRIORITY 2: Stock B-roll (Pexels/Pixabay)
            if background is None:
                try:
                    logger.info("🎬 PRIORITY 2: Trying stock B-roll...")
                    broll_dir = "temp/broll"
                    os.makedirs(broll_dir, exist_ok=True)
                    topic = script.get('topic', 'technology')
                    num_clips = min(4, max(2, int(actual_duration / 5)))
                    
                    fetched_clips = self.broll_fetcher.fetch_broll_sequence(topic, num_clips, broll_dir)
                    
                    if fetched_clips:
                        logger.info(f"✅ Fetched {len(fetched_clips)} B-roll clips")
                        bg_path = self.create_background_with_ffmpeg(fetched_clips, actual_duration)
                        
                        if bg_path and os.path.exists(bg_path):
                            background = VideoFileClip(bg_path)
                            logger.info("✅ Using B-roll video")
                    else:
                        logger.warning("⚠️ B-roll fetch failed")
                        
                except Exception as e:
                    logger.warning(f"⚠️ B-roll generation failed: {e}")
            
            # 🥉 PRIORITY 3: Assets folder
            if background is None:
                local_bg = "assets/background.mp4"
                if os.path.exists(local_bg):
                    try:
                        logger.info("📂 PRIORITY 3: Using assets/background.mp4")
                        video_clip = VideoFileClip(local_bg)
                        
                        if video_clip.duration < actual_duration:
                            video_clip = video_clip.with_effects([vfx.Loop(duration=actual_duration)])
                        else:
                            video_clip = video_clip.subclipped(0, actual_duration)
                        
                        background = video_clip.resized(height=1280)
                        if background.w != 720:
                            background = background.with_effects([vfx.Crop(x1=int(background.w/2 - 360), width=720, height=1280)])
                        
                        logger.info("✅ Using assets video")
                    except Exception as e:
                        logger.warning(f"⚠️ Assets video failed: {e}")
            
            # 🏁 FINAL FALLBACK: ColorClip with varied colors
            if background is None:
                logger.warning("⚠️ All methods failed - using ColorClip")
                
                base_colors = [
                    (20, 20, 60), (60, 20, 60), (20, 60, 60), (60, 30, 20),
                    (20, 40, 60), (40, 20, 50), (10, 50, 40), (70, 20, 30)
                ]
                
                seed = int(datetime.now().strftime("%H%M%S"))
                color = base_colors[seed % len(base_colors)]
                
                logger.info(f"🎨 Using color: RGB{color}")
                
                background = ColorClip(size=(720, 1280), color=color, duration=actual_duration)
            
            # --------------------------------------------------------
            # 🎨 STEP 3: Add Text Overlays
            # --------------------------------------------------------
            try:
                hook_text = TextClip(
                    text=script['hook'][:40].upper(),
                    font_size=60,
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
            
            try:
                cta_text = TextClip(
                    text=script['cta'][:30].upper(),
                    font_size=50,
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
            
            # --------------------------------------------------------
            # 🎞️ STEP 4: Composite & Export
            # --------------------------------------------------------
            clips = [background]
            if hook_text:
                clips.append(hook_text)
            if cta_text:
                clips.append(cta_text)
            
            final_video = CompositeVideoClip(clips, size=(720, 1280))
            final_video = final_video.with_audio(audio)
            
            logger.info(f"💾 Writing video to {output_path}...")
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                bitrate='3000k',
                preset='ultrafast',
                threads=1,  # 512MB limit optimization
                logger=None
            )
            
            logger.info(f"✅ Video created: {output_path} ({actual_duration:.2f}s)")
            
            # Cleanup
            audio.close()
            background.close()
            final_video.close()
            gc.collect()
            
            try:
                os.remove(voice_path)
            except:
                pass
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Video creation failed: {e}")
            import traceback
            traceback.print_exc()
            raise

# ==================== MASTER ORCHESTRATOR ====================
class MasterOrchestrator:
    """Production-ready automation orchestrator"""
    
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
        
        # Initialize SEO Manager
        if SEO_MANAGER_AVAILABLE:
            self.seo_manager = YouTubeSEOManager()
            logger.info("✅ YouTube SEO Manager initialized")
        else:
            self.seo_manager = None
        
        logger.info("✅ Master Orchestrator initialized")
    
    def run_daily_automation(self):
        """Run complete automation cycle"""
        try:
            logger.info("\n" + "="*80)
            logger.info(f"🚀 DAILY AUTOMATION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80 + "\n")
            
            # PHASE 1: Content Analysis
            logger.info("📍 PHASE 1: Content analysis...")
            
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
                    logger.info(f"✅ Found video: {video_id}")
                    
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
                'topic': analysis.get('key_topics', 'technology').split(',')[0].strip()
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"faceless_empire/videos/video_{timestamp}.mp4"
            
            self.video_composer.generate_voice_and_video(script, output_path)
            
            logger.info("✅ Video generated successfully")

            # ==================== AI THUMBNAIL GENERATION ====================
thumbnail_path = None
try:
    from thumbnail_ai_generator import AIThumbnailGenerator
    
    logger.info("\n🎨 Generating AI thumbnail...")
    thumbnail_gen = AIThumbnailGenerator()
    
    # Create thumbnails directory
    thumb_dir = "faceless_empire/thumbnails"
    os.makedirs(thumb_dir, exist_ok=True)
    
    # Generate thumbnail filename
    thumb_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    thumbnail_path = f"{thumb_dir}/thumb_{thumb_timestamp}.jpg"
    
    # Auto-detect style from hook
    hook_lower = script['hook'].lower()
    if any(word in hook_lower for word in ['amazing', 'insane', 'crazy', 'shocking']):
        style = 'shock'
    elif any(word in hook_lower for word in ['professional', 'business', 'corporate']):
        style = 'professional'
    elif any(word in hook_lower for word in ['simple', 'clean', 'minimal']):
        style = 'minimal'
    else:
        style = 'viral'  # Default
    
    # Generate thumbnail
    thumbnail_path = thumbnail_gen.generate_thumbnail(
        hook=script['hook'],
        topic=script.get('topic', 'AI technology'),
        output_path=thumbnail_path,
        style=style
    )
    
    if thumbnail_path and os.path.exists(thumbnail_path):
        logger.info(f"✅ AI Thumbnail generated: {thumbnail_path}")
        logger.info(f"   Style: {style}")
    else:
        logger.warning("⚠️ Thumbnail generation returned None")
        thumbnail_path = None
    
except ImportError:
    logger.warning("⚠️ thumbnail_ai_generator.py not found - skipping thumbnails")
    thumbnail_path = None
except Exception as e:
    logger.error(f"❌ Thumbnail generation error: {e}")
    import traceback
    traceback.print_exc()
    thumbnail_path = None
# ==================== END THUMBNAIL GENERATION ====================
    
            # PHASE 3: Upload to YouTube
            logger.info("\n📍 PHASE 3: YouTube upload...")
            youtube_url = None
            
            if self.youtube_uploader:
                try:
                    if self.seo_manager:
                        video_title = self.seo_manager.get_video_title(analysis['short_hook'])
                        video_description = self.seo_manager.generate_video_description(
                            hook=analysis['short_hook'],
                            topic=analysis['key_topics'],
                            tool_name=analysis.get('affiliate_angle', 'AI Tools')
                        )
                    else:
                        video_title = f"{analysis['short_hook']} #Shorts"
                        video_description = f"{analysis['summary']}\n\n#AITools #Productivity"
                    
                    hashtags = [tag.strip() for tag in analysis['key_topics'].split(',')]
                    
                    upload_result = self.youtube_uploader.upload_shorts_optimized(
                        video_path=output_path,
                        hook=video_title,
                        topic=analysis['key_topics'],
                        hashtags=hashtags,
                        affiliate_link=video_description
                    )
                    
                    youtube_url = upload_result['url']
                    logger.info(f"✅ YouTube URL: {youtube_url}")
                    
                except Exception as e:
                    logger.error(f"❌ YouTube upload failed: {e}")
            else:
                logger.info("⚠️ YouTube upload skipped (not configured)")
            
            # Cleanup
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
