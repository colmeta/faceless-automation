#!/usr/bin/env python3
"""
🎵 MUSIC MANAGER - Add Background Music to Videos
Supports copyright-free music from YouTube Audio Library
"""

import os
import logging
import random
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class MusicManager:
    """Manage background music for videos"""
    
    def __init__(self, music_dir: str = "assets/music"):
        self.music_dir = Path(music_dir)
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.music_files = self._scan_music_library()
    
    def _scan_music_library(self) -> list:
        """Scan music directory for available tracks"""
        if not self.music_dir.exists():
            logger.warning(f"⚠️ Music directory not found: {self.music_dir}")
            return []
        
        music_files = list(self.music_dir.glob("*.mp3"))
        logger.info(f"🎵 Found {len(music_files)} music tracks")
        return music_files
    
    def get_random_track(self) -> Optional[str]:
        """Get a random music track"""
        if not self.music_files:
            logger.warning("⚠️ No music files available")
            return None
        
        track = random.choice(self.music_files)
        logger.info(f"🎵 Selected track: {track.name}")
        return str(track)
    
    def get_track_by_mood(self, mood: str = "upbeat") -> Optional[str]:
        """Get music track based on mood (future enhancement)"""
        # For now, just return random track
        # Future: categorize tracks by mood tags
        return self.get_random_track()
    
    def mix_audio_with_music(
        self,
        voice_audio_path: str,
        output_path: str,
        music_volume: float = 0.25,
        music_track: Optional[str] = None
    ) -> str:
        """
        Mix voice audio with background music
        
        Args:
            voice_audio_path: Path to voice audio file
            output_path: Where to save mixed audio
            music_volume: Music volume (0.0-1.0), recommended 0.2-0.3
            music_track: Specific track to use, or None for random
        
        Returns:
            Path to mixed audio file
        """
        try:
            from moviepy import AudioFileClip, CompositeAudioClip
            
            # Load voice audio
            voice = AudioFileClip(voice_audio_path)
            voice_duration = voice.duration
            
            # Get music track
            if not music_track:
                music_track = self.get_random_track()
            
            if not music_track or not os.path.exists(music_track):
                logger.warning("⚠️ No music track available, using voice only")
                return voice_audio_path
            
            # Load and prepare music
            logger.info(f"🎵 Mixing audio with background music...")
            music = AudioFileClip(music_track)
            
            # Loop or trim music to match voice duration
            if music.duration < voice_duration:
                # Loop music
                import math
                loops_needed = math.ceil(voice_duration / music.duration)
                from moviepy import concatenate_audioclips
                music = concatenate_audioclips([music] * loops_needed)
            
            # Trim to exact duration
            music = music.subclipped(0, voice_duration)
            
            # Reduce music volume
            music = music.with_volume_scaled(music_volume)
            
            # Composite audio (voice + music)
            final_audio = CompositeAudioClip([voice, music])
            
            # Export
            final_audio.write_audiofile(output_path, fps=44100, logger=None)
            
            logger.info(f"✅ Audio mixed successfully: {output_path}")
            
            # Cleanup
            voice.close()
            music.close()
            final_audio.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Audio mixing failed: {e}")
            logger.info("⚠️ Falling back to voice only")
            return voice_audio_path
    
    def download_youtube_audio_library_samples(self):
        """
        Helper to download copyright-free music from YouTube Audio Library
        
        NOTE: This requires manual download. Visit:
        https://studio.youtube.com/channel/UC.../music
        
        Recommended tracks:
        1. "Inspiring" - Upbeat, motivational
        2. "Energy" - Fast-paced, exciting
        3. "Chill" - Calm, background
        4. "Trendy" - Modern, viral vibes
        
        Download and place in assets/music/ folder
        """
        logger.info("=" * 60)
        logger.info("📥 YOUTUBE AUDIO LIBRARY SETUP")
        logger.info("=" * 60)
        logger.info("\n1. Go to: https://studio.youtube.com/channel/YOUR_CHANNEL/music")
        logger.info("2. Filter by: Genre (Ambient, Electronic, Hip Hop)")
        logger.info("3. Download 5-10 tracks (MP3)")
        logger.info(f"4. Save to: {self.music_dir.absolute()}")
        logger.info("\n✅ After downloading, restart your automation\n")
        logger.info("=" * 60)


if __name__ == "__main__":
    # Test the music manager
    logging.basicConfig(level=logging.INFO)
    
    manager = MusicManager()
    
    if not manager.music_files:
        print("\n🚨 No music files found!")
        manager.download_youtube_audio_library_samples()
    else:
        print(f"\n✅ Music library ready: {len(manager.music_files)} tracks")
        track = manager.get_random_track()
        print(f"🎵 Random track: {track}")
