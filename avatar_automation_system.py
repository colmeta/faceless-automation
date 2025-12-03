import os
import requests
import time
import json
import random
import logging
from typing import Optional, Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KeyManager:
    """
    Manages rotation of API keys to maximize free tier usage.
    """
    def __init__(self, key_env_var_prefix: str):
        self.prefix = key_env_var_prefix
        self.keys = self._load_keys()
        self.current_index = 0

    def _load_keys(self) -> List[str]:
        """Loads all keys matching the prefix (e.g., DID_KEY_1, DID_KEY_2)."""
        keys = []
        # Check for single key
        if os.getenv(f"{self.prefix}_KEY"):
            keys.append(os.getenv(f"{self.prefix}_KEY"))
        
        # Check for numbered keys
        i = 1
        while True:
            key = os.getenv(f"{self.prefix}_KEY_{i}")
            if not key:
                break
            keys.append(key)
            i += 1
        
        if not keys:
            logger.warning(f"No keys found for prefix {self.prefix}")
        else:
            logger.info(f"Loaded {len(keys)} keys for {self.prefix}")
        
        return keys

    def get_current_key(self) -> Optional[str]:
        if not self.keys:
            return None
        return self.keys[self.current_index]

    def rotate_key(self) -> Optional[str]:
        """Switches to the next available key."""
        if not self.keys:
            return None
        
        prev_index = self.current_index
        self.current_index = (self.current_index + 1) % len(self.keys)
        logger.info(f"Rotating key for {self.prefix}: {prev_index} -> {self.current_index}")
        return self.keys[self.current_index]

class AvatarGenerator:
    """
    Unified interface for generating AI Avatar videos from multiple providers.
    """
    def __init__(self):
        self.did_keys = KeyManager("DID")
        self.hedra_keys = KeyManager("HEDRA")
        # Add other providers here

    def generate_video(self, script: str, avatar_url: str, provider: str = "auto") -> Dict[str, Any]:
        """
        Generates a video using the specified or best available provider.
        Returns a dictionary with 'video_url' and 'metadata'.
        """
        logger.info(f"🎬 Requesting avatar video. Provider: {provider}, Script length: {len(script)}")

        if provider == "auto" or provider == "d-id":
            result = self._generate_with_did(script, avatar_url)
            if result:
                return result
            if provider == "d-id":
                logger.error("D-ID generation failed and no fallback requested.")
                return None

        # Fallback to Hedra (Placeholder for implementation)
        # if provider == "auto" or provider == "hedra":
        #     result = self._generate_with_hedra(script, avatar_url)
        #     if result:
        #         return result

        logger.error("❌ All avatar providers failed.")
        return None

    def _generate_with_did(self, script: str, source_url: str) -> Optional[Dict[str, Any]]:
        """
        Generates video using D-ID API.
        """
        max_retries = len(self.did_keys.keys) if self.did_keys.keys else 1
        
        for attempt in range(max_retries):
            api_key = self.did_keys.get_current_key()
            if not api_key:
                logger.error("No D-ID API keys available.")
                return None

            headers = {
                "Authorization": f"Basic {api_key}",
                "Content-Type": "application/json"
            }

            # 1. Create Talk
            create_url = "https://api.d-id.com/talks"
            payload = {
                "script": {
                    "type": "text",
                    "input": script,
                    "provider": {
                        "type": "microsoft",
                        "voice_id": "en-US-GuyNeural" # Default, can be parameterized
                    }
                },
                "source_url": source_url,
                "config": {
                    "fluent": True,
                    "pad_audio": "0.0"
                }
            }

            try:
                logger.info(f"Attempting D-ID generation with key index {self.did_keys.current_index}...")
                response = requests.post(create_url, json=payload, headers=headers)
                
                if response.status_code == 201:
                    talk_id = response.json().get("id")
                    logger.info(f"✅ D-ID Talk created: {talk_id}")
                    return self._wait_for_did_completion(talk_id, headers)
                
                elif response.status_code == 402 or response.status_code == 403: # Payment Required / Forbidden
                    logger.warning(f"⚠️ D-ID Key exhausted or invalid (Status {response.status_code}). Rotating...")
                    self.did_keys.rotate_key()
                    continue
                
                else:
                    logger.error(f"❌ D-ID Error: {response.text}")
                    # Don't rotate on generic errors, might be bad request
                    return None

            except Exception as e:
                logger.error(f"❌ D-ID Exception: {str(e)}")
                return None
        
        return None

    def _wait_for_did_completion(self, talk_id: str, headers: Dict) -> Optional[Dict[str, Any]]:
        """Polls D-ID API for video completion."""
        url = f"https://api.d-id.com/talks/{talk_id}"
        
        for _ in range(30): # Wait up to 60 seconds (2s interval)
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    
                    if status == "done":
                        video_url = data.get("result_url")
                        logger.info(f"✅ Video ready: {video_url}")
                        return {
                            "video_url": video_url,
                            "provider": "d-id",
                            "duration": data.get("duration")
                        }
                    elif status == "error":
                        logger.error("❌ D-ID processing error.")
                        return None
                    
                    logger.info(f"⏳ Processing... ({status})")
                    time.sleep(2)
                else:
                    logger.error(f"❌ Polling error: {response.status_code}")
                    return None
            except Exception as e:
                logger.error(f"❌ Polling exception: {str(e)}")
                return None
        
        logger.error("❌ Timeout waiting for D-ID video.")
        return None

if __name__ == "__main__":
    # Quick test
    print("Testing Avatar Automation System...")
    # Mock environment for testing
    # os.environ["DID_KEY"] = "test_key"
    # gen = AvatarGenerator()
    # print(f"Loaded keys: {gen.did_keys.keys}")
