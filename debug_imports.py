
import os
import sys
import base64
import pickle
import traceback

def test_transcript_api():
    print("Testing YouTubeTranscriptApi...")
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print(f"Imported: {YouTubeTranscriptApi}")
        print(f"Dir: {dir(YouTubeTranscriptApi)}")
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            print("✅ get_transcript exists")
        else:
            print("❌ get_transcript MISSING")
            
        if hasattr(YouTubeTranscriptApi, 'list_transcripts'):
            print("✅ list_transcripts exists")
        else:
            print("❌ list_transcripts MISSING")
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()

def test_base64_token():
    print("\nTesting Base64 Token...")
    try:
        with open('youtube_token_base64.txt', 'r') as f:
            token_b64 = f.read().strip()
        
        print(f"Token length: {len(token_b64)}")
        
        # Try decoding
        try:
            token_bytes = base64.b64decode(token_b64)
            print("✅ Base64 decode successful")
            
            # Try unpickling
            creds = pickle.loads(token_bytes)
            print(f"✅ Unpickle successful: {creds}")
            
        except Exception as e:
            print(f"❌ Decode/Unpickle failed: {e}")
            # Try with padding fix
            missing_padding = len(token_b64) % 4
            if missing_padding:
                token_b64 += '=' * (4 - missing_padding)
                print(f"Added padding, new length: {len(token_b64)}")
                try:
                    token_bytes = base64.b64decode(token_b64)
                    print("✅ Base64 decode successful (with padding)")
                    creds = pickle.loads(token_bytes)
                    print(f"✅ Unpickle successful: {creds}")
                except Exception as e2:
                    print(f"❌ Still failed: {e2}")

    except Exception as e:
        print(f"❌ File read failed: {e}")

if __name__ == "__main__":
    test_transcript_api()
    test_base64_token()
