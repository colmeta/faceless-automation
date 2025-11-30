#!/usr/bin/env python3
"""
🧪 QUICK TEST - VERIFY FIXED SYSTEM
Tests all critical components locally before deploying
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_moviepy_imports():
    """Test MoviePy 2.x imports"""
    print("\n" + "="*60)
    print("TEST 1: MoviePy 2.x Imports")
    print("="*60)
    
    try:
        from moviepy import (
            ColorClip, TextClip, CompositeVideoClip, 
            AudioFileClip, VideoFileClip, ImageClip, vfx
        )
        print("✅ All MoviePy imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_moviepy_syntax():
    """Test MoviePy 2.x syntax"""
    print("\n" + "="*60)
    print("TEST 2: MoviePy 2.x Syntax")
    print("="*60)
    
    try:
        from moviepy import ColorClip, vfx
        
        # Test with_duration
        clip = ColorClip(size=(100, 100), color=(255, 0, 0), duration=1)
        
        if hasattr(clip, 'with_duration'):
            print("✅ clip.with_duration exists")
        else:
            print("❌ clip.with_duration does NOT exist")
            return False
        
        # Test with_position
        if hasattr(clip, 'with_position'):
            print("✅ clip.with_position exists")
        else:
            print("❌ clip.with_position does NOT exist")
            return False
        
        # Test with_effects
        if hasattr(clip, 'with_effects'):
            print("✅ clip.with_effects exists")
        else:
            print("❌ clip.with_effects does NOT exist")
            return False
        
        print("✅ All MoviePy 2.x methods available")
        return True
        
    except Exception as e:
        print(f"❌ Syntax test failed: {e}")
        return False

def test_url_encoding():
    """Test URL encoding"""
    print("\n" + "="*60)
    print("TEST 3: URL Encoding")
    print("="*60)
    
    try:
        import urllib.parse
        
        test_query = "AI tools automation"
        encoded = urllib.parse.quote(test_query)
        
        print(f"Original: {test_query}")
        print(f"Encoded: {encoded}")
        
        if encoded == "AI%20tools%20automation":
            print("✅ URL encoding works correctly")
            return True
        else:
            print("❌ URL encoding produced unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ URL encoding failed: {e}")
        return False

def test_edge_tts():
    """Test Edge-TTS availability"""
    print("\n" + "="*60)
    print("TEST 4: Edge-TTS (Optional)")
    print("="*60)
    
    try:
        import edge_tts
        print("✅ Edge-TTS available")
        return True
    except ImportError:
        print("⚠️ Edge-TTS not installed (will use gTTS fallback)")
        return True  # Not a failure

def test_gtts():
    """Test gTTS availability"""
    print("\n" + "="*60)
    print("TEST 5: gTTS (Fallback)")
    print("="*60)
    
    try:
        from gtts import gTTS
        print("✅ gTTS available")
        return True
    except ImportError:
        print("❌ gTTS not installed (CRITICAL)")
        return False

def test_environment_variables():
    """Test critical environment variables"""
    print("\n" + "="*60)
    print("TEST 6: Environment Variables")
    print("="*60)
    
    required = ['YOUTUBE_API_KEY', 'GEMINI_API_KEY']
    optional = ['PEXELS_API_KEY', 'PIXABAY_API_KEY', 'CLOUDINARY_CLOUD_NAME']
    
    all_good = True
    
    for var in required:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is MISSING (CRITICAL)")
            all_good = False
    
    for var in optional:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️ {var} is missing (optional)")
    
    return all_good

def test_assets_folder():
    """Test assets folder availability"""
    print("\n" + "="*60)
    print("TEST 7: Assets Folder")
    print("="*60)
    
    if os.path.exists('assets'):
        print("✅ assets/ folder exists")
        
        if os.path.exists('assets/background.mp4'):
            print("✅ assets/background.mp4 exists")
        else:
            print("⚠️ assets/background.mp4 missing (will use image or ColorClip)")
        
        if os.path.exists('assets/background.jpg'):
            print("✅ assets/background.jpg exists")
        else:
            print("⚠️ assets/background.jpg missing (will use ColorClip)")
        
        return True
    else:
        print("⚠️ assets/ folder missing (will use ColorClip fallback)")
        return True  # Not a failure - ColorClip fallback exists

def test_video_generation():
    """Test minimal video generation"""
    print("\n" + "="*60)
    print("TEST 8: Video Generation (Quick)")
    print("="*60)
    
    try:
        from moviepy import ColorClip, AudioFileClip, CompositeVideoClip
        from gtts import gTTS
        import os
        
        print("🎬 Generating 2-second test video...")
        
        # Generate voice
        tts = gTTS(text="Test", lang='en')
        tts.save('test_voice.mp3')
        print("✅ Voice generated")
        
        # Create video
        audio = AudioFileClip('test_voice.mp3')
        duration = min(audio.duration, 2)
        
        bg = ColorClip(size=(1080, 1920), color=(20, 20, 60), duration=duration)
        
        final = CompositeVideoClip([bg], size=(1080, 1920))
        final = final.with_audio(audio)
        
        final.write_videofile(
            'test_video.mp4',
            fps=30,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        print("✅ Video created: test_video.mp4")
        
        # Cleanup
        audio.close()
        bg.close()
        final.close()
        os.remove('test_voice.mp3')
        os.remove('test_video.mp4')
        
        print("✅ Cleanup successful")
        return True
        
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TESTING FIXED SYSTEM")
    print("="*60)
    
    tests = [
        ("MoviePy Imports", test_moviepy_imports),
        ("MoviePy 2.x Syntax", test_moviepy_syntax),
        ("URL Encoding", test_url_encoding),
        ("Edge-TTS", test_edge_tts),
        ("gTTS Fallback", test_gtts),
        ("Environment Variables", test_environment_variables),
        ("Assets Folder", test_assets_folder),
        ("Video Generation", test_video_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - READY TO DEPLOY!")
        print("\nNext steps:")
        print("1. Commit changes: git add . && git commit -m 'Fixed system'")
        print("2. Push to GitHub: git push origin main")
        print("3. Wait for Render to deploy (3-5 minutes)")
        print("4. Trigger automation: python trigger_automation.py")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed - fix before deploying")
        print("\nFailed tests need to be resolved before deployment.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}\n")
        sys.exit(1)
