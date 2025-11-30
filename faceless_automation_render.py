#!/usr/bin/env python3
"""
🎬 RENDER-OPTIMIZED VIDEO GENERATOR
Lightweight version for Render free instance (512MB RAM)
- No Whisper (uses simple captions)
- No complex fonts (system fonts only)
- Memory optimized
- Cloudinary integration for storage
"""

            logger.info(f"✅ Video created: {output_path}")
            
            # Cleanup
            audio.close()
            bg_video.close()
            final_video.close()
            
            # Force garbage collection
            gc.collect()
            
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
