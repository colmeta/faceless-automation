from moviepy import TextClip, ColorClip, AudioFileClip
import sys

print(f"MoviePy version: {sys.modules.get('moviepy', 'unknown')}")

# 1. Check set_audio vs with_audio
try:
    clip = ColorClip(size=(100, 100), color=(255, 0, 0), duration=1)
    if hasattr(clip, 'with_audio'):
        print("✅ clip.with_audio exists")
    else:
        print("❌ clip.with_audio does NOT exist")
        
    if hasattr(clip, 'set_audio'):
        print("⚠️ clip.set_audio exists (Legacy?)")
    else:
        print("ℹ️ clip.set_audio does NOT exist")

    # Check other set_ vs with_ methods
    for method in ['position', 'duration', 'start', 'end']:
        has_set = hasattr(clip, f'set_{method}')
        has_with = hasattr(clip, f'with_{method}')
        print(f"Method '{method}': set_={has_set}, with_={has_with}")

except Exception as e:
    print(f"Error checking clip methods: {e}")

# 2. Check TextClip arguments
print("\nChecking TextClip signature...")
try:
    # Try creating TextClip with new potential arguments
    # Hypothesis: fontsize -> font_size, color might be different
    try:
        txt = TextClip(text="Hello", font_size=50, color='white')
        print("✅ TextClip(text='...', font_size=50, color='white') worked")
    except Exception as e:
        print(f"❌ TextClip(font_size) failed: {e}")

    try:
        txt = TextClip("Hello", fontsize=50, color='white')
        print("✅ TextClip(fontsize=50) worked")
    except Exception as e:
        print(f"❌ TextClip(fontsize) failed: {e}")

    # Inspect init if possible
    import inspect
    sig = inspect.signature(TextClip.__init__)
    print(f"TextClip.__init__ signature: {sig}")

except Exception as e:
    print(f"Error checking TextClip: {e}")
