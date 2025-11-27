#!/usr/bin/env python3
"""
👑 MASTER AUTOMATION - FIXED FOR RENDER 512MB
Fixes: 
1. YouTube transcript API compatibility 
2. Video duration issues (3-second problem)
3. Missing analysis fields
4. Memory-optimized for free tier
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from pathlib import Path
from youtube_auto_uploader import YouTubeUploader

# Setup logging
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
                
            except Exception as e:
                logger.warning(f"⚠️ Modern API failed ({e}), trying legacy...")
                
                # Fallback to simple API (older but more reliable)
                try:
                    captions = YouTubeTranscriptApi.get_transcript(video_id)
                    full_text = " ".join([item['text'] for item in captions])
                    logger.info(f"✅ Transcript retrieved (legacy): {len(full_text)} chars")
                    return full_text
                except:
                    logger.error("❌ Both transcript methods failed")
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
            'short_hook': 'This Free AI Tool Blew My Mind',
            'summary': 'Discover how this AI tool can automate your workflow and save hours every week.',
            'key_topics': 'AI, automation, productivity',
            'cta': 'Get started free today',
            'affiliate_angle': 'AI tools'
        }

# ==================== CRITICAL FIX 3: VIDEO DURATION (THE 3-SECOND BUG) ====================
class VideoComposerFixed:
    """Fixed video composer for proper duration"""
    
    def __init__(self):
        from gtts import gTTS
        self.gTTS = gTTS
    
    def generate_voice_and_video(self, script: dict, output_path: str) -> str:
        """Generate voice and create video with correct duration"""
        try:
            from moviepy.editor import (
                ColorClip, TextClip, CompositeVideoClip, 
                AudioFileClip, concatenate_videoclips
            )
            import os
            
            logger.info("🎬 Starting video creation...")
            
            # STEP 1: Generate voice
            narration = script.get('narration', '')
            if not narration:
                narration = f"{script['hook']}. {script.get('cta', 'Try it now')}."
            
            voice_path = "temp/voice.mp3"
            os.makedirs("temp", exist_ok=True)
            
            logger.info(f"🔊 Generating voice: '{narration[:50]}...'")
            tts = self.gTTS(text=narration, lang='en', slow=False)
            tts.save(voice_path)
            
            # STEP 2: Get actual audio duration
            audio = AudioFileClip(voice_path)
            actual_duration = audio.duration
            
            logger.info(f"⏱️ Audio duration: {actual_duration:.2f} seconds")
            
            # STEP 3: Create background that matches audio duration
            # This is the KEY FIX - video duration must match audio duration
            background = ColorClip(
                size=(1080, 1920),
                color=(20, 20, 60),
                duration=actual_duration  # Use actual audio duration!
            )
            
            # STEP 4: Add simple hook text
            try:
                hook_text = TextClip(
                    script['hook'][:40].upper(),
                    fontsize=60,
                    color='yellow',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(1000, None)
                ).set_position('center').set_duration(min(3, actual_duration))
            except Exception as e:
                logger.warning(f"⚠️ Hook text failed: {e}")
                hook_text = None
            
            # STEP 5: Add CTA text at the end
            try:
                cta_text = TextClip(
                    script['cta'][:30].upper(),
                    fontsize=50,
                    color='white',
                    bg_color='red',
                    method='caption',
                    size=(1000, None)
                ).set_position(('center', 'bottom')).set_start(
                    max(0, actual_duration - 2)
                ).set_duration(min(2, actual_duration))
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
            final_video = final_video.set_audio(audio)
            
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
                    q='AI tools tutorial -crypto',
                    part='snippet',
                    type='video',
                    maxResults=5,
                    order='viewCount'
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
                'cta': analysis['cta']
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
        result = orchestrator.run_daily_automation()
        
        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print(f"Video: {result['video_path']}")
        if result['cloudinary_url']:
            print(f"URL: {result['cloudinary_url']}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
