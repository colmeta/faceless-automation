#!/usr/bin/env python3
"""
📤 YOUTUBE AUTO-UPLOADER - RENDER COMPATIBLE
Supports both local file and environment variable authentication
"""

import os
import pickle
import logging
import json
import base64
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeUploader:
    """Complete YouTube upload automation with OAuth"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    CLIENT_SECRET_FILE = 'client_secret.json'
    TOKEN_FILE = 'token.pickle'
    
    def __init__(self):
        self.youtube = None
        self.authenticate()
    
    def _get_client_config(self):
        """Get client config from file or environment variable"""
        
        # Try environment variable first (for Render)
        client_secret_env = os.getenv('YOUTUBE_CLIENT_SECRET_JSON')
        if client_secret_env:
            logger.info("📋 Using client secret from environment variable")
            try:
                return json.loads(client_secret_env)
            except:
                # Try base64 decode
                try:
                    decoded = base64.b64decode(client_secret_env)
                    return json.loads(decoded)
                except Exception as e:
                    logger.error(f"Failed to parse YOUTUBE_CLIENT_SECRET_JSON: {e}")
        
        # Fallback to file
        if os.path.exists(self.CLIENT_SECRET_FILE):
            logger.info("📋 Using client secret from file")
            with open(self.CLIENT_SECRET_FILE, 'r') as f:
                return json.load(f)
        
        raise FileNotFoundError(
            f"❌ No client secret found!\n"
        )
        
    def authenticate(self):
        """Authenticate with YouTube"""
        credentials = self._get_token_from_env()
        
        # Try file if env variable not available
        if not credentials and os.path.exists(self.TOKEN_FILE):
            logger.info("📋 Loading credentials from file...")
            with open(self.TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
        
        # Refresh or get new credentials
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                logger.info("🔄 Refreshing expired credentials...")
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    credentials = None
            
            if not credentials:
                # On Render, we CANNOT open a browser. Fail if no valid token.
                logger.error("❌ No valid credentials found and cannot open browser on server!")
                logger.error("Please check YOUTUBE_TOKEN_PICKLE_BASE64 environment variable.")
                raise ValueError("Authentication failed: No valid token and cannot perform OAuth on server")

        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=credentials)
        logger.info("✅ YouTube service authenticated")

    def _get_token_from_env(self):
        """Get token from environment variable with padding fix"""
        token_b64 = os.getenv('YOUTUBE_TOKEN_PICKLE_BASE64')
        
        # Fallback to local file if env var is missing or empty
        if not token_b64:
            if os.path.exists('youtube_token_base64.txt'):
                 try:
                     with open('youtube_token_base64.txt', 'r') as f:
                         token_b64 = f.read().strip()
                     logger.info("📋 Loaded token from youtube_token_base64.txt")
                 except Exception as e:
                     logger.error(f"❌ Failed to read token file: {e}")
                     return None
            else:
                return None
            
        try:
            # Fix base64 padding and clean string
            token_b64 = token_b64.strip()
            token_b64 = token_b64.replace(' ', '').replace('\n', '').replace('\r', '')
            
            missing_padding = len(token_b64) % 4
            if missing_padding:
                token_b64 += '=' * (4 - missing_padding)
            
            token_bytes = base64.b64decode(token_b64)
            return pickle.loads(token_bytes)
        except Exception as e:
            logger.error(f"❌ Failed to decode token from env: {e}")
            return None
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list = None,
        category: str = "28",  # Science & Technology
        privacy: str = "public",
        made_for_kids: bool = False
    ) -> Dict:
        """Upload video to YouTube"""
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        logger.info(f"📤 Uploading: {title}")
        logger.info(f"   File: {video_path}")
        logger.info(f"   Privacy: {privacy}")
        
        # Prepare request body
        body = {
            'snippet': {
                'title': title[:100],
                'description': description[:5000],
                'tags': tags[:500] if tags else [],
                'categoryId': category,
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': made_for_kids,
                'embeddable': True,
                'publicStatsViewable': True
            }
        }
        
        # Upload file
        media = MediaFileUpload(
            video_path,
            chunksize=1024*1024,
            resumable=True,
            mimetype='video/mp4'
        )
        
        try:
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            last_progress = 0
            
            while response is None:
                status, response = request.next_chunk()
                
                if status:
                    progress = int(status.progress() * 100)
                    if progress > last_progress + 10:
                        logger.info(f"   Upload progress: {progress}%")
                        last_progress = progress
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ Upload complete!")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: {video_url}")
            
            return {
                'success': True,
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'uploaded_at': datetime.now().isoformat()
            }
        
        except HttpError as e:
            logger.error(f"❌ Upload failed: {e}")
            raise
    
    def upload_shorts_optimized(
        self,
        video_path: str,
        hook: str,
        topic: str,
        hashtags: list,
        affiliate_link: str = None
    ) -> Dict:
        """Upload with YouTube Shorts optimization"""
        
        title = f"{hook[:70]} #Shorts"
        
        description_parts = [
            hook,
            "",
            "⚡ Quick AI Tutorial",
            ""
        ]
        
        if affiliate_link:
            description_parts.extend([
                f"🔗 Try it free: {affiliate_link}",
                ""
            ])
        
        description_parts.extend([
            "📱 Follow for daily AI tips",
            "",
            " ".join(hashtags[:30]),
            "",
            "---",
            "Created with AI automation for educational purposes.",
            "",
            "#AI #ArtificialIntelligence #Technology #Tutorial #Shorts"
        ])
        
        description = "\n".join(description_parts)
        
        tags = [tag.replace('#', '') for tag in hashtags]
        tags.extend(['AI', 'Artificial Intelligence', 'Technology', 'Tutorial', 'Shorts'])
        
        return self.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            category="28",
            privacy="public"
        )


if __name__ == "__main__":
    uploader = YouTubeUploader()
    print("✅ YouTube uploader ready!")
