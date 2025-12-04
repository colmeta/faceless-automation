"""
Avatar Variation Manager
Manages rotation of multiple avatar images for D-ID video generation
"""
import os
import random
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AvatarVariationManager:
    """Manages multiple avatar images for variety in video generation"""
    
    def __init__(self, avatar_dir: str = "avatars"):
        self.avatar_dir = avatar_dir
        self.avatars = self._load_avatars()
        self.current_index = 0
        self.selection_mode = "sequential"  # Options: sequential, random, time_based
        
        if self.avatars:
            logger.info(f"✅ Loaded {len(self.avatars)} avatar images")
        else:
            logger.warning(f"⚠️ No avatars found in {avatar_dir}")
    
    def _load_avatars(self) -> List[str]:
        """Load all avatar image files from directory"""
        if not os.path.exists(self.avatar_dir):
            logger.warning(f"Avatar directory {self.avatar_dir} not found")
            return []
        
        valid_extensions = ('.jpg', '.jpeg', '.png')
        avatars = []
        
        for file in sorted(os.listdir(self.avatar_dir)):
            if file.lower().endswith(valid_extensions):
                avatar_path = os.path.join(self.avatar_dir, file)
                avatars.append(avatar_path)
        
        return avatars
    
    def get_next_avatar(self) -> Optional[str]:
        """Get the next avatar based on selection mode"""
        if not self.avatars:
            logger.error("No avatars available")
            return None
        
        if self.selection_mode == "random":
            selected = random.choice(self.avatars)
        elif self.selection_mode == "time_based":
            # Use hour of day to select avatar (varies throughout day)
            hour_index = datetime.now().hour % len(self.avatars)
            selected = self.avatars[hour_index]
        else:  # sequential (default)
            selected = self.avatars[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.avatars)
        
        logger.info(f"📸 Selected avatar: {os.path.basename(selected)}")
        return selected
    
    def set_selection_mode(self, mode: str):
        """Set avatar selection mode: sequential, random, or time_based"""
        if mode in ["sequential", "random", "time_based"]:
            self.selection_mode = mode
            logger.info(f"Avatar selection mode set to: {mode}")
        else:
            logger.warning(f"Invalid mode: {mode}. Using 'sequential'")
    
    def get_avatar_count(self) -> int:
        """Return number of available avatars"""
        return len(self.avatars)
    
    def has_avatars(self) -> bool:
        """Check if any avatars are available"""
        return len(self.avatars) > 0

if __name__ == "__main__":
    # Test the avatar manager
    logging.basicConfig(level=logging.INFO)
    
    manager = AvatarVariationManager()
    print(f"\nFound {manager.get_avatar_count()} avatars")
    
    if manager.has_avatars():
        print("\nTesting sequential mode:")
        for i in range(min(3, manager.get_avatar_count())):
            avatar = manager.get_next_avatar()
            print(f"  {i+1}. {avatar}")
        
        print("\nTesting random mode:")
        manager.set_selection_mode("random")
        for i in range(3):
            avatar = manager.get_next_avatar()
            print(f"  {i+1}. {avatar}")
