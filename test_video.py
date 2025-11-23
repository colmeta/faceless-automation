#!/usr/bin/env python3
"""Quick test to generate one video"""

from complete_launch_system import ViralScriptGenerator
from gtts import gTTS
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
import os

# Generate script
script_gen = ViralScriptGenerator()
script = script_gen.generate_script()

print(f"✅ Script: {script['hook']}")

# Generate voice
tts = gTTS(text=script['full_script'], lang='en')
tts.save('test_voice.mp3')
print("✅ Voice generated")

# Create simple video
audio = AudioFileClip('test_voice.mp3')
duration = min(audio.duration, 60)

bg = ColorClip(size=(1080, 1920), color=(20, 20, 40), duration=duration)

txt = TextClip(
    script['hook'][:50],
    fontsize=70,
    color='white',
    size=(1000, None)
).set_position('center').set_duration(duration)

video = CompositeVideoClip([bg, txt], size=(1080, 1920))
video = video.set_audio(audio)

video.write_videofile(
    'test_video.mp4',
    fps=30,
    codec='libx264',
    audio_codec='aac'
)

print("✅ Video created: test_video.mp4")

# Upload to Cloudinary
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

result = cloudinary.uploader.upload(
    'test_video.mp4',
    resource_type='video',
    folder='faceless_videos/test'
)

print(f"✅ Uploaded to Cloudinary: {result['secure_url']}")
