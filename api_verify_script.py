#!/usr/bin/env python3
"""
🔍 COMPLETE API VERIFICATION SCRIPT
Tests all APIs and provides detailed diagnostic information
Run this BEFORE deploying to catch issues early
"""

import os
import sys
import requests
import urllib.parse
import pickle
import base64
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"   {text}")

class APITester:
    def __init__(self):
        self.results = {}
        self.critical_failures = []
        self.warnings = []
    
    def test_pexels(self):
        """Test Pexels API"""
        print_header("TEST 1: Pexels API")
        
        api_key = os.getenv('PEXELS_API_KEY', '').strip()
        
        if not api_key:
            print_error("PEXELS_API_KEY not found in environment")
            self.critical_failures.append("Pexels API key missing")
            self.results['pexels'] = False
            return False
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-5:]}")
        
        try:
            query = urllib.parse.quote("technology")
            url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
            headers = {"Authorization": api_key}
            
            print_info(f"Testing: {url[:60]}...")
            response = requests.get(url, headers=headers, timeout=10)
            
            print_info(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total_results', 0)
                videos = data.get('videos', [])
                
                if videos:
                    print_success(f"Pexels API working! Found {total} total videos")
                    print_info(f"Sample video URL: {videos[0]['video_files'][0]['link'][:50]}...")
                    self.results['pexels'] = True
                    return True
                else:
                    print_warning("Pexels returned no videos")
                    self.warnings.append("Pexels: No videos in response")
                    self.results['pexels'] = False
                    return False
            
            elif response.status_code == 401:
                print_error("Pexels API: Unauthorized (401)")
                print_error("Your API key is invalid or expired")
                print_info("Get a new key at: https://www.pexels.com/api/")
                self.critical_failures.append("Pexels: Invalid API key")
                self.results['pexels'] = False
                return False
            
            else:
                print_error(f"Pexels API error: {response.status_code}")
                print_info(f"Response: {response.text[:200]}")
                self.critical_failures.append(f"Pexels: HTTP {response.status_code}")
                self.results['pexels'] = False
                return False
                
        except Exception as e:
            print_error(f"Pexels test failed: {e}")
            self.critical_failures.append(f"Pexels: {str(e)}")
            self.results['pexels'] = False
            return False
    
    def test_pixabay(self):
        """Test Pixabay API"""
        print_header("TEST 2: Pixabay API")
        
        api_key = os.getenv('PIXABAY_API_KEY', '').strip()
        
        if not api_key:
            print_error("PIXABAY_API_KEY not found in environment")
            self.warnings.append("Pixabay API key missing (optional)")
            self.results['pixabay'] = False
            return False
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-5:]}")
        
        try:
            query = urllib.parse.quote("technology")
            url = f"https://pixabay.com/api/videos/?key={api_key}&q={query}&per_page=1"
            
            print_info(f"Testing: {url[:80]}...")
            response = requests.get(url, timeout=10)
            
            print_info(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                hits = data.get('hits', [])
                
                if hits:
                    print_success(f"Pixabay API working! Found {total} total videos")
                    print_info(f"Sample video: {hits[0]['videos']['medium']['url'][:50]}...")
                    self.results['pixabay'] = True
                    return True
                else:
                    print_warning("Pixabay returned no videos")
                    self.warnings.append("Pixabay: No videos in response")
                    self.results['pixabay'] = False
                    return False
            
            elif response.status_code == 400:
                print_error("Pixabay API: Bad Request (400)")
                print_info(f"Response: {response.text[:200]}")
                self.critical_failures.append("Pixabay: Bad request")
                self.results['pixabay'] = False
                return False
            
            else:
                print_error(f"Pixabay API error: {response.status_code}")
                print_info(f"Response: {response.text[:200]}")
                self.critical_failures.append(f"Pixabay: HTTP {response.status_code}")
                self.results['pixabay'] = False
                return False
                
        except Exception as e:
            print_error(f"Pixabay test failed: {e}")
            self.warnings.append(f"Pixabay: {str(e)}")
            self.results['pixabay'] = False
            return False
    
    def test_youtube_api(self):
        """Test YouTube Data API"""
        print_header("TEST 3: YouTube Data API")
        
        api_key = os.getenv('YOUTUBE_API_KEY', '').strip()
        
        if not api_key:
            print_error("YOUTUBE_API_KEY not found in environment")
            self.critical_failures.append("YouTube API key missing")
            self.results['youtube_api'] = False
            return False
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-5:]}")
        
        try:
            from googleapiclient.discovery import build
            
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            request = youtube.search().list(
                q='AI tools',
                part='snippet',
                type='video',
                maxResults=1
            )
            
            response = request.execute()
            
            if response.get('items'):
                video_id = response['items'][0]['id']['videoId']
                title = response['items'][0]['snippet']['title']
                
                print_success(f"YouTube Data API working!")
                print_info(f"Sample video: {title[:50]}...")
                print_info(f"Video ID: {video_id}")
                self.results['youtube_api'] = True
                return True
            else:
                print_warning("YouTube API returned no results")
                self.warnings.append("YouTube API: No search results")
                self.results['youtube_api'] = False
                return False
                
        except Exception as e:
            print_error(f"YouTube API test failed: {e}")
            self.critical_failures.append(f"YouTube API: {str(e)}")
            self.results['youtube_api'] = False
            return False
    
    def test_youtube_transcript(self):
        """Test YouTube Transcript API"""
        print_header("TEST 4: YouTube Transcript API")
        
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            # Test with a known public video with captions
            test_video_id = "dQw4w9WgXcQ"
            
            print_info(f"Testing with video: {test_video_id}")
            
            try:
                captions = YouTubeTranscriptApi.get_transcript(test_video_id)
                
                if captions:
                    print_success(f"YouTube Transcript API working!")
                    print_info(f"Got {len(captions)} caption segments")
                    print_info(f"Sample: {captions[0]['text'][:50]}...")
                    self.results['youtube_transcript'] = True
                    return True
                else:
                    print_warning("No captions found")
                    self.warnings.append("YouTube Transcript: No captions")
                    self.results['youtube_transcript'] = False
                    return False
                    
            except Exception as e:
                print_warning(f"Direct method failed: {e}")
                print_info("Trying list_transcripts method...")
                
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(test_video_id)
                    transcript = transcript_list.find_transcript(['en'])
                    captions = transcript.fetch()
                    
                    print_success(f"YouTube Transcript API working! (list method)")
                    print_info(f"Got {len(captions)} caption segments")
                    self.results['youtube_transcript'] = True
                    return True
                except Exception as e2:
                    print_error(f"Both methods failed: {e2}")
                    self.warnings.append("YouTube Transcript: Both methods failed")
                    self.results['youtube_transcript'] = False
                    return False
                    
        except Exception as e:
            print_error(f"YouTube Transcript test failed: {e}")
            self.warnings.append(f"YouTube Transcript: {str(e)}")
            self.results['youtube_transcript'] = False
            return False
    
    def test_gemini(self):
        """Test Gemini API"""
        print_header("TEST 5: Gemini API")
        
        api_key = os.getenv('GEMINI_API_KEY', '').strip()
        
        if not api_key:
            print_error("GEMINI_API_KEY not found in environment")
            self.critical_failures.append("Gemini API key missing")
            self.results['gemini'] = False
            return False
        
        print_info(f"API Key: {api_key[:10]}...{api_key[-5:]}")
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            print_info("Sending test prompt...")
            response = model.generate_content("Reply with: 'Gemini API is working'")
            text = response.text.strip()
            
            if text:
                print_success(f"Gemini API working!")
                print_info(f"Response: {text[:100]}...")
                self.results['gemini'] = True
                return True
            else:
                print_error("Gemini returned empty response")
                self.critical_failures.append("Gemini: Empty response")
                self.results['gemini'] = False
                return False
                
        except Exception as e:
            print_error(f"Gemini test failed: {e}")
            self.critical_failures.append(f"Gemini: {str(e)}")
            self.results['gemini'] = False
            return False
    
    def test_cloudinary(self):
    """Test Cloudinary"""
    print_header("TEST 6: Cloudinary")
    
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', '').strip()
    api_key = os.getenv('CLOUDINARY_API_KEY', '').strip()
    api_secret = os.getenv('CLOUDINARY_API_SECRET', '').strip()
    
    if not all([cloud_name, api_key, api_secret]):
        print_error("Cloudinary credentials incomplete")
        print_info(f"Cloud Name: {'✅' if cloud_name else '❌'}")
        print_info(f"API Key: {'✅' if api_key else '❌'}")
        print_info(f"API Secret: {'✅' if api_secret else '❌'}")
        self.critical_failures.append("Cloudinary: Incomplete credentials")
        self.results['cloudinary'] = False
        return False
    
    print_info(f"Cloud Name: {cloud_name}")
    print_info(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        import cloudinary
        import cloudinary.uploader  # ← ADD THIS LINE
        
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Create test file
        test_file = "test_upload.txt"
        with open(test_file, 'w') as f:
            f.write(f"Test upload at {datetime.now()}")
        
        print_info("Uploading test file...")
        result = cloudinary.uploader.upload(
            test_file,
            resource_type="raw",
            folder="faceless_test"
        )
        
        # Cleanup
        os.remove(test_file)
        
        print_success(f"Cloudinary working!")
        print_info(f"Test URL: {result['secure_url'][:60]}...")
        self.results['cloudinary'] = True
        return True
        
    except Exception as e:
        print_error(f"Cloudinary test failed: {e}")
        self.critical_failures.append(f"Cloudinary: {str(e)}")
        self.results['cloudinary'] = False
        return False
    
    def test_youtube_token(self):
        """Test YouTube Upload Token"""
        print_header("TEST 7: YouTube Upload Token")
        
        token_b64 = os.getenv('YOUTUBE_TOKEN_PICKLE_BASE64', '').strip()
        
        if not token_b64:
            # Try local file
            if os.path.exists('youtube_token_base64.txt'):
                print_info("Loading from youtube_token_base64.txt...")
                with open('youtube_token_base64.txt', 'r') as f:
                    token_b64 = f.read().strip()
            else:
                print_error("YOUTUBE_TOKEN_PICKLE_BASE64 not found")
                print_warning("YouTube upload will be disabled")
                self.warnings.append("YouTube token missing (uploads disabled)")
                self.results['youtube_token'] = False
                return False
        
        print_info(f"Token length: {len(token_b64)} characters")
        
        try:
            # Clean and fix padding
            token_b64 = token_b64.replace(' ', '').replace('\n', '').replace('\r', '')
            
            missing_padding = len(token_b64) % 4
            if missing_padding:
                token_b64 += '=' * (4 - missing_padding)
                print_info(f"Added {4 - missing_padding} padding characters")
            
            # Try to decode
            token_bytes = base64.b64decode(token_b64)
            print_info(f"Decoded {len(token_bytes)} bytes")
            
            # Try to unpickle
            credentials = pickle.loads(token_bytes)
            
            print_success("YouTube token valid!")
            print_info(f"Token type: {type(credentials).__name__}")
            
            if hasattr(credentials, 'token'):
                print_info(f"Access token: {credentials.token[:20]}...")
            if hasattr(credentials, 'refresh_token'):
                print_info(f"Refresh token: {'Present' if credentials.refresh_token else 'Missing'}")
            
            self.results['youtube_token'] = True
            return True
            
        except Exception as e:
            print_error(f"YouTube token test failed: {e}")
            print_warning("YouTube upload will be disabled")
            self.warnings.append(f"YouTube token: {str(e)}")
            self.results['youtube_token'] = False
            return False
    
    def test_edge_tts(self):
        """Test Edge-TTS (Optional)"""
        print_header("TEST 8: Edge-TTS (Optional)")
        
        try:
            import edge_tts
            import asyncio
            
            async def test_voice():
                voices = await edge_tts.list_voices()
                return len(voices) > 0
            
            result = asyncio.run(test_voice())
            
            if result:
                print_success("Edge-TTS available!")
                print_info("Will use high-quality Edge-TTS voice")
                self.results['edge_tts'] = True
                return True
            else:
                print_warning("Edge-TTS available but no voices found")
                print_info("Will fallback to gTTS")
                self.warnings.append("Edge-TTS: No voices")
                self.results['edge_tts'] = False
                return False
                
        except Exception as e:
            print_warning(f"Edge-TTS not available: {e}")
            print_info("Will use gTTS fallback (still works fine)")
            self.results['edge_tts'] = False
            return False
    
    def test_gtts(self):
        """Test gTTS (Fallback)"""
        print_header("TEST 9: gTTS (Fallback Voice)")
        
        try:
            from gtts import gTTS
            
            test_file = "test_voice.mp3"
            tts = gTTS(text="Test", lang='en')
            tts.save(test_file)
            
            if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
                os.remove(test_file)
                print_success("gTTS working!")
                self.results['gtts'] = True
                return True
            else:
                print_error("gTTS file creation failed")
                self.critical_failures.append("gTTS: File creation failed")
                self.results['gtts'] = False
                return False
                
        except Exception as e:
            print_error(f"gTTS test failed: {e}")
            self.critical_failures.append(f"gTTS: {str(e)}")
            self.results['gtts'] = False
            return False
    
    def generate_report(self):
        """Generate final report"""
        print_header("📊 FINAL REPORT")
        
        # Count results
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        
        # Display results by category
        print(f"\n{BLUE}Core Services (CRITICAL):{RESET}")
        critical = ['gemini', 'youtube_api', 'gtts', 'cloudinary']
        for service in critical:
            if service in self.results:
                status = f"{GREEN}✅ PASS{RESET}" if self.results[service] else f"{RED}❌ FAIL{RESET}"
                print(f"  {status} - {service.upper()}")
        
        print(f"\n{BLUE}B-Roll Sources:{RESET}")
        broll = ['pexels', 'pixabay']
        for service in broll:
            if service in self.results:
                status = f"{GREEN}✅ PASS{RESET}" if self.results[service] else f"{YELLOW}⚠️  FAIL{RESET}"
                print(f"  {status} - {service.upper()}")
        
        print(f"\n{BLUE}Optional Features:{RESET}")
        optional = ['youtube_token', 'youtube_transcript', 'edge_tts']
        for service in optional:
            if service in self.results:
                status = f"{GREEN}✅ PASS{RESET}" if self.results[service] else f"{YELLOW}⚠️  SKIP{RESET}"
                print(f"  {status} - {service.upper()}")
        
        # Summary
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}SUMMARY: {passed}/{total} tests passed{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        
        # Critical failures
        if self.critical_failures:
            print(f"\n{RED}🚨 CRITICAL FAILURES (Must fix before deployment):{RESET}")
            for failure in self.critical_failures:
                print(f"{RED}  ❌ {failure}{RESET}")
        
        # Warnings
        if self.warnings:
            print(f"\n{YELLOW}⚠️  WARNINGS (Optional, but recommended):{RESET}")
            for warning in self.warnings:
                print(f"{YELLOW}  ⚠️  {warning}{RESET}")
        
        # Recommendations
        print(f"\n{BLUE}💡 RECOMMENDATIONS:{RESET}")
        
        if not self.results.get('pexels') and not self.results.get('pixabay'):
            print(f"{YELLOW}  ⚠️  No B-roll sources available - videos will use ColorClip backgrounds{RESET}")
            print(f"     Fix Pexels API key for professional videos")
        
        if not self.results.get('youtube_token'):
            print(f"{YELLOW}  ⚠️  YouTube uploads disabled - videos will only go to Cloudinary{RESET}")
            print(f"     Run: python get_youtube_token.py to enable uploads")
        
        if not self.results.get('edge_tts'):
            print(f"  ℹ️  Using gTTS for voice (Edge-TTS would be higher quality)")
        
        # Final verdict
        critical_core = all([
            self.results.get('gemini', False),
            self.results.get('youtube_api', False),
            self.results.get('gtts', False),
            self.results.get('cloudinary', False)
        ])
        
        print(f"\n{BLUE}{'='*70}{RESET}")
        if critical_core:
            print(f"{GREEN}✅ SYSTEM READY - Core services operational!{RESET}")
            print(f"\n{GREEN}You can deploy and run automation now.{RESET}")
            if self.warnings:
                print(f"{YELLOW}(Some optional features have warnings - see above){RESET}")
        else:
            print(f"{RED}❌ NOT READY - Critical failures must be fixed first{RESET}")
            print(f"\n{RED}Fix the critical failures listed above before deploying.{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        
        return critical_core

def main():
    print_header("🔍 FACELESS AUTOMATION - API VERIFICATION SUITE")
    print(f"\n{BLUE}Testing all APIs and services...{RESET}")
    print(f"{BLUE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")
    
    tester = APITester()
    
    # Run all tests
    tester.test_gemini()
    tester.test_youtube_api()
    tester.test_youtube_transcript()
    tester.test_pexels()
    tester.test_pixabay()
    tester.test_cloudinary()
    tester.test_youtube_token()
    tester.test_edge_tts()
    tester.test_gtts()
    
    # Generate report
    ready = tester.generate_report()
    
    # Exit code
    return 0 if ready else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️  Tests interrupted by user{RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Test suite crashed: {e}{RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)