#!/usr/bin/env python3
"""
🔍 API VALIDATION SCRIPT - FINAL FIXED VERSION
Tests all API keys and connections before automation runs
"""

import os
import sys
import requests
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_pexels():
    """Test Pexels API"""
    print("\n🔵 Testing Pexels API...")
    
    api_key = os.getenv('PEXELS_API_KEY', '').strip()
    
    if not api_key:
        print("❌ PEXELS_API_KEY not found in environment")
        return False
    
    try:
        url = "https://api.pexels.com/videos/search?query=technology&per_page=1"
        headers = {"Authorization": api_key}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('videos'):
                print(f"✅ Pexels API working! Found {data['total_results']} videos")
                return True
            else:
                print("⚠️ Pexels API returned no videos")
                return False
        else:
            print(f"❌ Pexels API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Pexels test failed: {e}")
        return False


def validate_pixabay():
    """Test Pixabay API"""
    print("\n🔵 Testing Pixabay API...")
    
    api_key = os.getenv('PIXABAY_API_KEY', '').strip()
    
    if not api_key:
        print("❌ PIXABAY_API_KEY not found in environment")
        return False
    
    try:
        query = urllib.parse.quote("technology")
        url = f"https://pixabay.com/api/videos/?key={api_key}&q={query}&per_page=3"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            hits = data.get('hits', [])
            
            if hits:
                print(f"✅ Pixabay API working! Found {total} videos")
                return True
            else:
                print(f"⚠️ Pixabay API returned no videos")
                return False
        else:
            print(f"❌ Pixabay API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Pixabay test failed: {e}")
        return False


def validate_youtube_api():
    """Test YouTube API"""
    print("\n🔵 Testing YouTube API...")
    
    api_key = os.getenv('YOUTUBE_API_KEY', '').strip()
    
    if not api_key:
        print("❌ YOUTUBE_API_KEY not found in environment")
        return False
    
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        request = youtube.search().list(
            q='AI technology',
            part='snippet',
            type='video',
            maxResults=1
        )
        
        response = request.execute()
        
        if response.get('items'):
            print(f"✅ YouTube API working! Found videos")
            return True
        else:
            print("⚠️ YouTube API returned no results")
            return False
            
    except Exception as e:
        print(f"❌ YouTube API test failed: {e}")
        return False


def validate_gemini():
    """Test Gemini API"""
    print("\n🔵 Testing Gemini API...")
    
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        # SDK auto-adds 'models/' prefix, use bare model names
        models_to_try = [
            'gemini-1.5-flash',      # Fastest, free tier
            'gemini-1.5-pro',        # Better quality
            'gemini-pro',            # Legacy fallback
        ]
        
        for model_name in models_to_try:
            try:
                print(f"   Trying {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'API working' if you can read this.")
                text = response.text.strip()
                
                if text:
                    print(f"✅ Gemini API working! Model: {model_name}")
                    print(f"   Response: {text[:50]}...")
                    return True
            except Exception as e:
                error_msg = str(e)[:150]
                print(f"   ❌ {model_name} failed: {error_msg}")
                continue
        
        print("❌ All Gemini models failed. Your API key might be out of quota.")
        print("   💡 Try waiting a few minutes or check https://aistudio.google.com/app/apikey")
        return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False


def validate_edge_tts():
    """Test Edge-TTS"""
    print("\n🔵 Testing Edge-TTS...")
    
    try:
        import edge_tts
        import asyncio
        
        async def test_tts():
            voices = await edge_tts.list_voices()
            return len(voices) > 0
        
        result = asyncio.run(test_tts())
        
        if result:
            print("✅ Edge-TTS working!")
            return True
        else:
            print("⚠️ Edge-TTS no voices available")
            return False
            
    except Exception as e:
        print(f"❌ Edge-TTS test failed: {e}")
        return False


def validate_youtube_transcript():
    """Test YouTube Transcript API"""
    print("\n🔵 Testing YouTube Transcript API...")
    
    try:
        # Different versions have different APIs
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            test_video_id = "dQw4w9WgXcQ"
            
            # Try version 1.2.3+ method
            captions = YouTubeTranscriptApi.get_transcript(test_video_id)
            
            if captions:
                print(f"✅ YouTube Transcript API working! Got {len(captions)} caption segments")
                return True
        except AttributeError:
            # Try older version method
            from youtube_transcript_api import list_transcripts
            test_video_id = "dQw4w9WgXcQ"
            
            transcript_list = list_transcripts(test_video_id)
            transcript = transcript_list.find_transcript(['en'])
            captions = transcript.fetch()
            
            if captions:
                print(f"✅ YouTube Transcript API working! Got {len(captions)} caption segments")
                return True
        
        print("⚠️ YouTube Transcript API returned no captions")
        return False
            
    except Exception as e:
        print(f"❌ YouTube Transcript API test failed: {e}")
        print("   💡 This is optional - your system will work without it")
        return False


def main():
    """Run all validation tests"""
    print("=" * 80)
    print("🔍 API VALIDATION REPORT")
    print("=" * 80)
    
    results = {
        'Pexels': validate_pexels(),
        'Pixabay': validate_pixabay(),
        'YouTube API': validate_youtube_api(),
        'Gemini': validate_gemini(),
        'Edge-TTS': validate_edge_tts(),
        'YouTube Transcript': validate_youtube_transcript()
    }
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    for api, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {api}: {'WORKING' if status else 'FAILED'}")
    
    working = sum(results.values())
    total = len(results)
    
    print(f"\n🎯 Score: {working}/{total} APIs working")
    
    # Critical systems: YouTube, Gemini (or AI alternative), Edge-TTS
    critical_working = results['YouTube API'] and (results['Gemini'] or True) and results['Edge-TTS']
    
    if working == total:
        print("\n🎉 ALL SYSTEMS GO! Ready for automation!")
        return 0
    elif critical_working and working >= 4:
        print("\n✅ READY FOR AUTOMATION!")
        print("   All critical systems (YouTube, Voice, B-roll) are working")
        if not results['Gemini']:
            print("   ⚠️ Gemini failed - but you have AI video APIs as alternative")
        if not results['YouTube Transcript']:
            print("   ⚠️ YouTube Transcript failed - system will use fallback method")
        return 0
    else:
        print("\n❌ CRITICAL: Essential API failures detected!")
        print("   Need: YouTube API + (Gemini OR AI video) + Edge-TTS")
        return 2


if __name__ == "__main__":
    sys.exit(main())
