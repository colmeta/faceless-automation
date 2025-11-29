from moviepy import ImageClip, ColorClip
import sys

print(f"MoviePy version: {sys.modules.get('moviepy', 'unknown')}")

try:
    # Create a dummy clip (ColorClip is easier as it doesn't need a file)
    clip = ColorClip(size=(100, 100), color=(255, 0, 0), duration=1)
    
    print("Checking attributes of ColorClip...")
    if hasattr(clip, 'resize'):
        print("✅ clip.resize exists")
    else:
        print("❌ clip.resize does NOT exist")

    if hasattr(clip, 'resized'):
        print("✅ clip.resized exists")
    else:
        print("❌ clip.resized does NOT exist")

except Exception as e:
    print(f"Error: {e}")
