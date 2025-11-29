#!/usr/bin/env python3
"""
🎬 PROFESSIONAL VIDEO COMPOSER
Features:
- MoviePy 2.x Compatibility (vfx, with_*)
- Multi-clip B-roll system
- Dynamic background generation
- Pattern interrupts (every 4-8 seconds)
- Professional text animations
- Graceful fallback chain
"""

import os
import logging
import asyncio
from typing import Optional, List, Dict
from moviepy import (
    ColorClip, TextClip, CompositeVideoClip, 
    AudioFileClip, concatenate_videoclips, VideoFileClip, ImageClip, vfx
)

logger = logging.getLogger(__name__)

class BRollFetcher:
    """Fetch stock footage with robust error handling"""
    
    def __init__(self):
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_key = os.getenv('PIXABAY_API_KEY')
    
    def fetch_broll_sequence(self, query: str, count: int, output_dir: str) -> List[str]:
        """Fetch a sequence of unique B-roll videos"""
        import requests
        import urllib.parse
        
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

class VideoComposerProfessional:
    """Professional video composer for proper duration and effects"""
    
    def __init__(self):
        self.broll_fetcher = BRollFetcher()
    
    def generate_voice_and_video(self, script: dict, output_path: str) -> str:
        """Generate voice and create video with correct duration"""
        try:
            logger.info("🎬 Starting professional video creation...")
            
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
            
            # Calculate needed clips (approx 1 clip every 4-5 seconds for pattern interrupt)
            num_clips = max(3, int(actual_duration / 4))
            
            logger.info(f"🎞️ Fetching {num_clips} clips for topic: {topic}")
            fetched_clips = self.broll_fetcher.fetch_broll_sequence(topic, num_clips, broll_dir)
            
            local_bg = "assets/background.mp4"
            local_img = "assets/background.jpg"
            
            background = None
            
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
                        
                        # Center crop
                        clip = clip.with_effects([vfx.Crop(x1=clip.w/2 - 540, width=1080, height=1920)])
                        
                        # Set duration for this segment
                        # Last clip takes remaining time
                        if i == len(fetched_clips) - 1:
                            dur = max(0, actual_duration - total_dur)
                        else:
                            dur = target_clip_dur
                        
                        # Loop if too short
                        if clip.duration < dur:
                            clip = clip.with_effects([vfx.Loop(duration=dur)])
                        else:
                            clip = clip.subclip(0, dur)
                            
                        clip_objs.append(clip)
                        total_dur += dur
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to process clip {clip_path}: {e}")
                
                if clip_objs:
                    background = concatenate_videoclips(clip_objs, method="compose")
            
            # Fallback to local assets if dynamic failed
            if background is None:
                if os.path.exists(local_bg):
                    logger.info(f"found background video at {local_bg}")
                    video_clip = VideoFileClip(local_bg)
                    if video_clip.duration < actual_duration:
                        video_clip = video_clip.with_effects([vfx.Loop(duration=actual_duration)])
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
                
                # Add fade in effect
                hook_text = hook_text.with_effects([vfx.FadeIn(0.5)])
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
                
                # Add slide in effect (simulated with fadein for now as slide_in is complex)
                cta_text = cta_text.with_effects([vfx.FadeIn(0.5)])
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
