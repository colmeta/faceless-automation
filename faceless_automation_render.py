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
                (VideoGenConfig.WIDTH, VideoGenConfig.HEIGHT),
                vfx
            )
            
            # Step 5: Add hook text at start (Professional Style)
            try:
                hook_text = script['hook'].upper()[:50]
                
                # Main Hook Text
                hook_clip = TextClip(
                    text=hook_text,
                    font_size=75,
                    font='Arial-Bold',
                    color='#FFD700',  # Gold/Yellow
                    stroke_color='black',
                    stroke_width=3,
                    method='caption',
                    size=(VideoGenConfig.WIDTH - 100, None),
                    align='center'
                ).with_position(('center', 250)).with_duration(3.5)
                
                # Apply fadein effect correctly
                hook_clip = hook_clip.with_effects([vfx.fadein(0.5)])
                
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
                    text=cta_text,
                    font_size=60,
                    font='Arial-Bold',
                    color='white',
                    bg_color='#CC0000',  # Dark Red background
                    method='caption',
                    size=(VideoGenConfig.WIDTH - 200, None),
                    align='center'
                ).with_position(('center', 1400)).with_start(max(0, duration - 4)).with_duration(4)
                
                # Add a "Subscribe" hint
                sub_clip = TextClip(
                    text="SUBSCRIBE FOR MORE",
                    font_size=40,
                    font='Arial-Bold',
                    color='white',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    align='center'
                ).with_position(('center', 1550)).with_start(max(0, duration - 4)).with_duration(4)
                
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
            final_video = final_video.with_audio(audio)
            
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
