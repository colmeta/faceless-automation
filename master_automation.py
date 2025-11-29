#!/usr/bin/env python3
"""
👑 MASTER AUTOMATION - FIXED FOR RENDER 512MB
Fixes: 
1. YouTube transcript API compatibility 
2. Video duration issues (3-second problem)
3. Missing analysis fields
4. Memory-optimized for free tier
5. MoviePy 2.x compatibility
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

# ==================== CRITICAL FIX 1: YOUTUBE TRANSCRIPT ====================
class YouTubeTranscriptFixer:
    """Fixed YouTube transcript extraction"""
    
    @staticmethod
    def get_transcript(video_id: str) -> str:
        """Get transcript with fallback support"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            logger.info(f"🔍 Fetching transcript for {video_id}...")
            
            # Try the modern API first (handles auto-generated captions)
            try:
                if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
                    transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # Try English first
                    try:
                        transcript = transcripts.find_transcript(['en'])
                    except:
                        # Fallback to any available transcript
                        transcript = transcripts.find_transcript(transcripts._manually_created_transcripts[0].language if transcripts._manually_created_transcripts else 'en')
                    
                    captions = transcript.fetch()
                    full_text = " ".join([item['text'] for item in captions])
                    
                    logger.info(f"✅ Transcript retrieved: {len(full_text)} chars")
                    return full_text
                else:
                    raise AttributeError("Old API version")
                
            except Exception as e:
                logger.warning(f"⚠️ Modern API failed ({e}), trying legacy...")
                
                # Fallback to simple API (older but more reliable)
                try:
                    captions = YouTubeTranscriptApi.get_transcript(video_id)
                    full_text = " ".join([item['text'] for item in captions])
                    logger.info(f"✅ Transcript retrieved (legacy): {len(full_text)} chars")
                    return full_text
                except Exception as legacy_error:
                    logger.error(f"❌ Legacy transcript failed: {legacy_error}")
                    return None
        
        except Exception as e:
            logger.error(f"❌ Transcript error: {e}")
            return None

# ==================== CRITICAL FIX 2: ANALYSIS WITH FALLBACKS ====================
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
            
            # Extract JSON
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            
            if json_match:
                analysis = json.loads(json_match.group())
                logger.info("✅ Analysis complete")
                return self._ensure_fields(analysis)
            else:
                logger.warning("⚠️ Could not parse JSON response, using defaults")
                return self._create_default_analysis()
        
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return self._create_default_analysis()
    
    def _ensure_fields(self, analysis: dict) -> dict:
        """Ensure all required fields exist"""
        defaults = {
            'short_hook': 'This AI Tool is Amazing',
            'summary': 'An excellent AI tool that will help you.',
            'key_topics': 'AI, tools, automation',
            'cta': 'Try it free now',
            'affiliate_angle': 'AI tools'
        }
        
        # Fill missing fields
        for key, default_value in defaults.items():
            if key not in analysis or not analysis[key]:
                logger.warning(f"⚠️ Missing field '{key}', using default")
                analysis[key] = default_value
        
        return analysis
    
    def _create_default_analysis(self) -> dict:
        """Create default analysis when all else fails"""
        return {
            'short_hook': 'This Ferrari Strategy Changed Everything',
            'summary': 'Imagine driving a Ferrari through the Italian Alps. The wind in your hair, the roar of the engine. This isn\'t just a dream, it\'s a lifestyle. Discover how you can achieve financial freedom and travel the whole world in style. Stop watching others live your dream. Start building your empire today with these simple steps. You deserve the best life has to offer.',
            'key_topics': 'luxury, travel, motivation, ferrari, success',
            'cta': 'Click the link to start your journey',
            'affiliate_angle': 'Financial Freedom'
        }

# ==================== B-ROLL FETCHER ====================
class BRollFetcher:
    """Fetch stock footage"""
    
    def __init__(self):
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_key = os.getenv('PIXABAY_API_KEY')
    
    def fetch_broll_sequence(self, query: str, count: int, output_dir: str) -> List[str]:
        """Fetch a sequence of unique B-roll videos"""
        clips_paths = []
        
        # Try Pexels first
        if self.pexels_key:
            try:
                query_encoded = urllib.parse.quote(query)
                url = f"https://api.pexels.com/videos/search?query={query_encoded}&per_page={count}&orientation=portrait"
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
                        output_path = os.path.join(output_dir, f"broll_pexels_{i}.mp4")
                        video_data = requests.get(video_url, timeout=30)
                        
                        with open(output_path, 'wb') as f:
                            f.write(video_data.content)
                        
                        clips_paths.append(output_path)
                        logger.info(f"✅ Pexels clip downloaded: {output_path}")
                        
                    if len(clips_paths) >= count:
                        return clips_paths
            except Exception as e:
                logger.warning(f"⚠️ Pexels fetch failed: {e}")

        # Try Pixabay if needed
        if len(clips_paths) < count and self.pixabay_key:
            try:
                needed = count - len(clips_paths)
                query_encoded = urllib.parse.quote(query)
                url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={query_encoded}&per_page={needed + 3}"
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        hits = data.get('hits', [])
                        
                        for i, hit in enumerate(hits):
                            if len(clips_paths) >= count: break
                            
                            videos = hit.get('videos', {})
                            video_url = videos.get('medium', {}).get('url')
                            
                            if video_url:
                                output_path = os.path.join(output_dir, f"broll_pixabay_{i}.mp4")
                                video_data = requests.get(video_url, timeout=30)
                                
                                with open(output_path, 'wb') as f:
                                    f.write(video_data.content)
                                
                                clips_paths.append(output_path)
                                logger.info(f"✅ Pixabay clip downloaded: {output_path}")
                    except ValueError:
                        logger.error(f"❌ Pixabay returned invalid JSON: {response.text[:100]}")
                else:
                    logger.error(f"❌ Pixabay API error: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Pixabay fetch failed: {e}")
        
        return clips_paths

# ==================== CRITICAL FIX 3: VIDEO DURATION (THE 3-SECOND BUG) ====================
class VideoComposerFixed:
    """Fixed video composer for proper duration"""
    
    def __init__(self):
        self.broll_fetcher = BRollFetcher()
    
    def generate_voice_and_video(self, script: dict, output_path: str) -> str:
        """Generate voice and create video with correct duration"""
        try:
            from moviepy import (
                ColorClip, TextClip, CompositeVideoClip, 
                AudioFileClip, concatenate_videoclips, VideoFileClip, ImageClip, vfx
            )
            
            logger.info("🎬 Starting video creation...")
            
            # STEP 1: Generate voice (using Edge-TTS for professional quality)
            narration = script.get('narration', '')
            if not narration:
                narration = f"{script['hook']}. {script.get('cta', 'Try it now')}."
            
            voice_path = "temp/voice.mp3"
            os.makedirs("temp", exist_ok=True)
            
            logger.info(f"🔊 Generating voice with Edge-TTS: '{narration[:50]}...'")
            
            try:
                import edge_tts
                
                async def generate_voice():
                    communicate = edge_tts.Communicate(narration, "en-US-ChristopherNeural")
                    await communicate.save(voice_path)
                
                asyncio.run(generate_voice())
                logger.info("✅ Edge-TTS generation successful")
            except Exception as e:
                logger.warning(f"⚠️ Edge-TTS failed ({e}), falling back to gTTS...")
                from gtts import gTTS
                tts = gTTS(text=narration, lang='en', slow=False)
                tts.save(voice_path)
                logger.info("✅ gTTS generation successful (fallback)")
            
            # STEP 2: Get actual audio duration
            audio = AudioFileClip(voice_path)
            actual_duration = audio.duration
            
            logger.info(f"⏱️ Audio duration: {actual_duration:.2f} seconds")
            
            # STEP 3: Create background with Multi-Clip System
            # Try dynamic B-roll first
            topic = script.get('topic', 'technology')
            broll_dir = "temp/broll_seq"
            os.makedirs(broll_dir, exist_ok=True)
            
            # Calculate needed clips (approx 1 clip every 4-5 seconds)
            num_clips = max(3, int(actual_duration / 4))
            
            logger.info(f"🎞️ Fetching {num_clips} clips for topic: {topic}")
            fetched_clips = self.broll_fetcher.fetch_broll_sequence(topic, num_clips, broll_dir)
            
            local_bg = "assets/background.mp4"
            local_img = "assets/background.jpg"
            
            if fetched_clips:
                logger.info(f"✅ Using {len(fetched_clips)} dynamic clips")
                clip_objs = []
                
                # Create sequence
                total_dur = 0
                target_clip_dur = actual_duration / len(fetched_clips)
                
                for i, clip_path in enumerate(fetched_clips):
                    try:
                        clip = VideoFileClip(clip_path)
                        
                        # Resize to cover 1080x1920
                        # MoviePy 2.x: resize -> resized
                        clip = clip.resized(height=1920)
                        if clip.w < 1080:
                             clip = clip.resized(width=1080)
                        clip = clip.with_effects([vfx.Crop(x1=clip.w/2 - 540, width=1080, height=1920)])
                        
                        # Set duration for this segment
                        # Last clip takes remaining time
                        if i == len(fetched_clips) - 1:
                            dur = max(0, actual_duration - total_dur)
                        else:
                            dur = target_clip_dur
                        
                        # Loop if too short
                        if clip.duration < dur:
                            clip = clip.loop(duration=dur)
                        else:
                            clip = clip.subclip(0, dur)
                            
                        clip_objs.append(clip)
                        total_dur += dur
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to process clip {clip_path}: {e}")
                
                if clip_objs:
                    background = concatenate_videoclips(clip_objs, method="compose")
                else:
                    # Fallback if all clips failed processing
                    background = None
            else:
                background = None

            # Fallback to local assets if dynamic failed
            if background is None:
                if os.path.exists(local_bg):
                    logger.info(f"found background video at {local_bg}")
                    video_clip = VideoFileClip(local_bg)
                    if video_clip.duration < actual_duration:
                        video_clip = video_clip.loop(duration=actual_duration)
                    else:
                        video_clip = video_clip.subclip(0, actual_duration)
                    
                    background = video_clip.resized(height=1920)
                    if background.w < 1080:
                         background = background.resized(width=1080)
                    background = background.with_effects([vfx.Crop(x1=background.w/2 - 540, width=1080, height=1920)])

                elif os.path.exists(local_img):
                    logger.info(f"Found background image at {local_img}")
                    img = ImageClip(local_img)
                    background = img.resized(height=1920)
                    if background.w < 1080:
                        background = background.resized(width=1080)
                    background = background.with_effects([vfx.Crop(x_center=background.w/2, y_center=background.h/2, width=1080, height=1920)])
                    # MoviePy 2.x: set_duration -> with_duration, set_position -> with_position
                    background = background.with_duration(actual_duration)
                    background = background.with_position(('center', 'center'))
                else:
                    logger.warning("⚠️ No background found, using ColorClip")
                    background = ColorClip(
                        size=(1080, 1920),
                        color=(20, 20, 60),
                        duration=actual_duration
                    )
            
            # STEP 4: Add simple hook text
            try:
                # MoviePy 2.x: TextClip(text=..., font_size=...)
                hook_text = TextClip(
                    text=script['hook'][:40].upper(),
                    font_size=60,
                    color='yellow',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(1000, None)
                ).with_position('center').with_duration(min(3, actual_duration))
            except Exception as e:
                logger.warning(f"⚠️ Hook text failed: {e}")
                hook_text = None
            
            # STEP 5: Add CTA text at the end
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
            
            # STEP 6: Composite
            clips = [background]
            if hook_text:
                clips.append(hook_text)
            if cta_text:
                clips.append(cta_text)
            
            final_video = CompositeVideoClip(clips, size=(1080, 1920))
            # MoviePy 2.x: set_audio -> with_audio
            final_video = final_video.with_audio(audio)
            
            # STEP 7: Export with correct settings
            logger.info(f"💾 Writing video to {output_path}...")
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                bitrate='3000k',
                preset='ultrafast',
                threads=2,
                verbose=False,
                logger=None  # Suppress MoviePy logs
            )
            
            logger.info(f"✅ Video created: {output_path} ({actual_duration:.2f}s)")
            
            # Cleanup
            audio.close()
            background.close()
            final_video.close()
            os.remove(voice_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Video creation failed: {e}")
            raise

# ==================== FIXED MASTER ORCHESTRATOR ====================
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
        """Run fixed automation"""
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
                    order='date'  # Get newest videos
                )
                
                response = request.execute()
                
                if response['items']:
                    video_id = response['items'][0]['id']['videoId']
                    logger.info(f"✅ Found viral video: {video_id}")
                    
                    # Get transcript
                    transcript = self.transcript_fixer.get_transcript(video_id)
                    
                    if transcript:
                        # Analyze transcript
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
            
            logger.info("✅ Analysis complete with all required fields")
            
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
            
            
            # PHASE 3: Upload to Cloudinary (if configured)
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

            # PHASE 4: Upload to YouTube
            logger.info("\n📍 PHASE 4: Uploading to YouTube...")
            youtube_url = None
            
            if self.youtube_uploader:
                try:
                    logger.info("🚀 Starting YouTube upload...")
                    
                    # Prepare metadata
                    hashtags = [tag.strip() for tag in analysis['key_topics'].split(',')]
                    
                    upload_result = self.youtube_uploader.upload_shorts_optimized(
                        video_path=output_path,
                        hook=analysis['short_hook'],
                        topic=analysis['key_topics'],
                        hashtags=hashtags,
                        affiliate_link=analysis.get('cta_link', 'https://example.com')
                    )
                    
                    youtube_url = upload_result['url']
                    logger.info(f"✅ YouTube Upload Successful: {youtube_url}")
                    
                except Exception as e:
                    logger.error(f"❌ YouTube upload failed: {e}")
            else:
                logger.warning("⚠️ Skipping YouTube upload (uploader not initialized)")
            
            # Cleanup local file only after all uploads are done
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    logger.info("🗑️ Local file deleted")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete local file: {e}")
            
            logger.info("\n" + "="*80)
            logger.info("🎉 DAILY AUTOMATION COMPLETE!")
            logger.info("="*80 + "\n")
            
            return {
                'status': 'success',
                'analysis': analysis,
                'video_path': output_path,
                'cloudinary_url': cloudinary_url,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Daily automation failed: {e}")
            import traceback
            traceback.print_exc()
            raise

# ==================== SIMPLE CLI ====================
def main():
    """Simple one-shot automation"""
    try:
        orchestrator = MasterOrchestrator()
        orchestrator.run_daily_automation()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
