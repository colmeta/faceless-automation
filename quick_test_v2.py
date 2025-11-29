import os
import sys
import logging
from master_automation import VideoComposerFixed

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_video_generation():
    try:
        logger.info("🧪 Starting video generation test...")
        
        composer = VideoComposerFixed()
        
        script = {
            'hook': 'TEST HOOK',
            'narration': 'This is a test of the emergency broadcast system. This is only a test.',
            'cta': 'TEST CTA',
            'topic': 'technology'
        }
        
        output_path = "test_video.mp4"
        
        composer.generate_voice_and_video(script, output_path)
        
        if os.path.exists(output_path):
            logger.info(f"✅ Test passed! Video created at {output_path}")
            # Clean up
            os.remove(output_path)
        else:
            logger.error("❌ Test failed! Video not created.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_video_generation()
