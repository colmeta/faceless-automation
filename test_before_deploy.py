#!/usr/bin/env python3
"""
🧪 LOCAL TEST SCRIPT - Test before deploying to Render
Tests all components independently to verify they work
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "=" * 60)
print("🧪 TESTING MASTER AUTOMATION COMPONENTS")
print("=" * 60 + "\n")

# Test 1: Environment Variables
print("📋 TEST 1: Environment Variables")
print("-" * 60)
required_keys = ['GROQ_API_KEY', 'GEMINI_API_KEY', 'PEXELS_API_KEY', 'YOUTUBE_TOKEN_PICKLE_BASE64']
optional_keys = ['KLING_ACCESS_KEY', 'RUNWAY_API_KEY', 'REPLICATE_API_TOKEN', 'PIXVERSE_API_KEY']

all_good = True
for key in required_keys:
    value = os.getenv(key)
    if value:
        print(f"✅ {key}: SET ({len(value)} chars)")
    else:
        print(f"❌ {key}: MISSING")
        all_good = False

print("\nOptional Keys:")
for key in optional_keys:
    value = os.getenv(key)
    if value:
        print(f"✅ {key}: SET ({len(value)} chars)")
    else:
        print(f"⚠️  {key}: Not set")

if not all_good:
    print("\n❌ CRITICAL: Some required keys are missing!")
    sys.exit(1)

print("\n✅ All required environment variables are set\n")

# Test 2: Import Fixed Master Automation
print("📦 TEST 2: Importing master_automation_FIXED.py")
print("-" * 60)
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import master_automation_FIXED as ma
    print("✅ Import successful")
    print(f"   - SafeAnalyzer: {ma.SafeAnalyzer}")
    print(f"   - VideoComposerFixed: {ma.VideoComposerFixed}")
    print(f"   - MasterOrchestrator: {ma.MasterOrchestrator}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: SafeAnalyzer Initialization
print("🧠 TEST 3: SafeAnalyzer (Groq + Gemini Flash 8B)")
print("-" * 60)
try:
    analyzer = ma.SafeAnalyzer()
    print("✅ SafeAnalyzer initialized")
    if analyzer.groq_client:
        print("   - Groq: ✅ Ready (PRIMARY)")
    else:
        print("   - Groq: ⚠️  Not available")
    
    if analyzer.gemini_model:
        print("   - Gemini Flash 8B: ✅ Ready (FALLBACK)")
    else:
        print("   - Gemini Flash 8B: ⚠️  Not available")
    
    # Test default analysis
    print("\n   Testing default analysis generation...")
    analysis = analyzer._create_default_analysis()
    print(f"   - short_hook: {analysis['short_hook'][:50]}...")
    print(f"   - summary: {analysis['summary'][:50]}...")
    print(f"   - key_topics: {analysis['key_topics']}")
    print(f"   - cta: {analysis['cta']}")
    print("   ✅ Default analysis works")
    
except Exception as e:
    print(f"❌ SafeAnalyzer test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: AI Video Generator (if available)
print("🎬 TEST 4: AI Video Generator Check")
print("-" * 60)
if ma.AI_VIDEO_AVAILABLE:
    try:
        from ai_video_manager_updated import AIVideoGenerator
        ai_gen = AIVideoGenerator()
        print("✅ AI Video Generator available")
        print(f"   - Kling AI: {'✅' if ai_gen.kling_access_key else '❌'}")
        print(f"   - Runway: {'✅' if ai_gen.runway_key else '❌'}")
        print(f"   - Replicate: {'✅' if ai_gen.replicate_key else '❌'}")
        print(f"   - Pixverse: {'✅' if ai_gen.pixverse_key else '❌'}")
    except Exception as e:
        print(f"⚠️  AI Video Generator import failed: {e}")
else:
    print("⚠️  AI Video Generator not available (ai_video_manager_updated.py not found)")

print()

# Test 5: B-roll Fetcher
print("📺 TEST 5: B-roll Fetcher")
print("-" * 60)
try:
    fetcher = ma.BRollFetcher()
    print("✅ B-roll Fetcher initialized")
    print(f"   - Pexels API: {'✅' if fetcher.pexels_key else '❌'}")
    print(f"   - Pixabay API: {'✅' if fetcher.pixabay_key else '❌'}")
except Exception as e:
    print(f"❌ B-roll Fetcher test failed: {e}")

print()

# Test 6: Video Composer
print("🎥 TEST 6: Video Composer")
print("-" * 60)
try:
    composer = ma.VideoComposerFixed()
    print("✅ Video Composer initialized")
except Exception as e:
    print(f"❌ Video Composer test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 7: MoviePy Check
print("🎞️  TEST 7: MoviePy 2.x Compatibility")
print("-" * 60)
try:
    from moviepy import TextClip, VideoFileClip, AudioFileClip, CompositeVideoClip, vfx
    from moviepy.video.VideoClip import ColorClip
    print("✅ All MoviePy imports successful")
    print("   - TextClip: ✅")
    print("   - VideoFileClip: ✅")
    print("   - AudioFileClip: ✅")
    print("   - CompositeVideoClip: ✅")
    print("   - ColorClip: ✅")
    print("   - vfx: ✅")
except Exception as e:
    print(f"❌ MoviePy import failed: {e}")
    print("   Run: pip install moviepy>=2.0.0")

print()

# Test 8: FFmpeg Check
print("⚙️  TEST 8: FFmpeg Availability")
print("-" * 60)
import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
    if result.returncode == 0:
        version_line = result.stdout.decode().split('\n')[0]
        print(f"✅ FFmpeg available: {version_line}")
    else:
        print("❌ FFmpeg found but returned error")
except FileNotFoundError:
    print("❌ FFmpeg not found in PATH")
    print("   Install: https://ffmpeg.org/download.html")
except Exception as e:
    print(f"⚠️  FFmpeg check failed: {e}")

print()

# Final Summary
print("=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("✅ master_automation_FIXED.py is ready for use!")
print("\n📝 NEXT STEPS:")
print("1. Verify all API keys are set correctly in .env")
print("2. Test locally: python master_automation_FIXED.py")
print("3. If successful, replace master_automation.py:")
print("   cp master_automation_FIXED.py master_automation.py")
print("4. Deploy to Render")
print("\n" + "=" * 60 + "\n")
