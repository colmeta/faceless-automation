import sys
try:
    import youtube_transcript_api
    print(f"Module: {youtube_transcript_api}")
    print(f"Version: {getattr(youtube_transcript_api, '__version__', 'unknown')}")
    
    from youtube_transcript_api import YouTubeTranscriptApi
    print(f"Class: {YouTubeTranscriptApi}")
    print(f"Dir: {dir(YouTubeTranscriptApi)}")
    
    if hasattr(YouTubeTranscriptApi, 'get_transcript'):
        print("✅ get_transcript exists")
    else:
        print("❌ get_transcript MISSING")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
