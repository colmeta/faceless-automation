import os
import sys
import io
import time
from avatar_automation_system import AvatarGenerator

# Set API Key explicitly for testing
os.environ['DID_KEY'] = "bnN1YnVnYWNvbGxpbkBnbWFpbC5jb20:M21ye8rOIk5vlxy2Dko70"

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_did_integration():
    print("Starting D-ID API Integration Test...")
    
    # Initialize Generator
    try:
        gen = AvatarGenerator()
        print("AvatarGenerator initialized.")
    except Exception as e:
        print(f"Failed to initialize AvatarGenerator: {e}")
        return

    # Check for API Key
    key = gen.did_keys.get_current_key()
    if not key:
        print("No D-ID API Key found in environment variables.")
        print("Please ensure DID_KEY is set in your .env file or environment.")
        return
    print(f"Found API Key: {key[:5]}...{key[-5:]}")

    # Test Parameters
    # Note: D-ID requires a publicly accessible URL for the source image.
    # We will use a sample image for the API test.
    # To use 'ghgh.jpg', it must be hosted online (e.g., S3, Cloudinary, or a public server).
    sample_image_url = "https://img.freepik.com/free-photo/portrait-white-man-isolated_53876-40306.jpg" 
    script = "Hello! This is a test of the D-ID API integration. If you can see this video, the system is working correctly."
    
    print(f"Using source image: {sample_image_url}")
    print(f"Using script: '{script}'")

    # Generate Video
    print("Sending request to D-ID...")
    result = gen.generate_video(script, sample_image_url, provider="d-id")

    if result:
        print("\nSUCCESS! Video generated successfully.")
        print(f"Video URL: {result['video_url']}")
        print(f"Duration: {result.get('duration')}s")
    else:
        print("\nFAILURE. Video generation failed.")
        print("Check the logs for more details.")

if __name__ == "__main__":
    test_did_integration()
