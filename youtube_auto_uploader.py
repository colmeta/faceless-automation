#!/usr/bin/env python3
"""
📤 YOUTUBE AUTO-UPLOADER - COMPLETE SOLUTION
Handles OAuth authentication and automatic video uploads
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import json

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
    
    def authenticate(self):
        """Handle OAuth authentication"""
        credentials = None
        
        # Load existing credentials
        if os.path.exists(self.TOKEN_FILE):
            logger.info("📋 Loading existing credentials...")
            with open(self.TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
        
        # Refresh or get new credentials
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                logger.info("🔄 Refreshing expired credentials...")
                credentials.refresh(Request())
            else:
                if not os.path.exists(self.CLIENT_SECRET_FILE):
                    raise FileNotFoundError(
                        f"❌ {self.CLIENT_SECRET_FILE} not found!\n\n"
                        "Get it from: https://console.cloud.google.com\n"
                        "1. Create OAuth 2.0 Client ID\n"
                        "2. Application type: Desktop app\n"
                        "3. Download JSON and rename to client_secret.json"
                    )
                
                logger.info("🔐 Starting OAuth flow...")
                logger.info("👉 Your browser will open for authorization")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRET_FILE,
                    self.SCOPES
                )
                credentials = flow.run_local_server(
                    port=8080,
                    prompt='consent',
                    success_message='✅ Authorization successful! You can close this window.'
                )
            
            # Save credentials
            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(credentials, token)
            logger.info("✅ Credentials saved")
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=credentials)
        logger.info("✅ YouTube service authenticated")
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list = None,
        category: str = "28",  # Science & Technology
        privacy: str = "public",  # public, private, or unlisted
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
                'title': title[:100],  # Max 100 chars
                'description': description[:5000],  # Max 5000 chars
                'tags': tags[:500] if tags else [],  # Max 500 tags
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
            chunksize=1024*1024,  # 1MB chunks
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
                    if progress > last_progress + 10:  # Log every 10%
                        logger.info(f"   Upload progress: {progress}%")
                        last_progress = progress
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ Upload complete!")
            logger.info(f"   Video ID: {video_id}")
            logger.info(f"   URL: {video_url}")
            
            # Save upload record
            self._save_upload_record(video_id, title, video_url)
            
            return {
                'success': True,
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'uploaded_at': datetime.now().isoformat()
            }
        
        except HttpError as e:
            logger.error(f"❌ Upload failed: {e}")
            
            error_reason = e.error_details[0]['reason'] if e.error_details else 'Unknown'
            
            # Common errors
            if 'quotaExceeded' in str(e):
                logger.error("📊 YouTube API quota exceeded (10,000 points/day)")
                logger.error("   Wait until midnight PST for reset")
            elif 'uploadLimitExceeded' in str(e):
                logger.error("⏰ Upload limit exceeded (50 uploads/day)")
            
            raise
    
    def _save_upload_record(self, video_id: str, title: str, url: str):
        """Save upload record for tracking"""
        record_file = 'upload_history.json'
        
        record = {
            'video_id': video_id,
            'title': title,
            'url': url,
            'uploaded_at': datetime.now().isoformat()
        }
        
        # Load existing records
        if os.path.exists(record_file):
            with open(record_file, 'r') as f:
                history = json.load(f)
        else:
            history = {'uploads': []}
        
        history['uploads'].append(record)
        
        # Save
        with open(record_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_upload_history(self) -> list:
        """Get upload history"""
        record_file = 'upload_history.json'
        
        if os.path.exists(record_file):
            with open(record_file, 'r') as f:
                history = json.load(f)
            return history['uploads']
        
        return []
    
    def upload_shorts_optimized(
        self,
        video_path: str,
        hook: str,
        topic: str,
        hashtags: list,
        affiliate_link: str = None
    ) -> Dict:
        """Upload with YouTube Shorts optimization"""
        
        # Build title (max 100 chars)
        title = f"{hook[:70]} #Shorts"
        
        # Build description (max 5000 chars)
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
            " ".join(hashtags[:30]),  # Add hashtags
            "",
            "---",
            "This video is created using AI automation for educational purposes.",
            "",
            "#AI #ArtificialIntelligence #Technology #Tutorial #Shorts"
        ])
        
        description = "\n".join(description_parts)
        
        # Extract hashtags as tags
        tags = [tag.replace('#', '') for tag in hashtags]
        tags.extend(['AI', 'Artificial Intelligence', 'Technology', 'Tutorial', 'Shorts'])
        
        return self.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            category="28",  # Science & Technology
            privacy="public"
        )


class SmartUploadScheduler:
    """Schedule uploads at optimal times"""
    
    OPTIMAL_TIMES_UTC = {
        'monday': ['14:00', '19:00'],
        'tuesday': ['14:00', '19:00', '22:00'],
        'wednesday': ['14:00', '19:00'],
        'thursday': ['14:00', '19:00', '22:00'],
        'friday': ['14:00', '19:00'],
        'saturday': ['16:00', '20:00'],
        'sunday': ['16:00', '20:00']
    }
    
    def __init__(self):
        self.uploader = YouTubeUploader()
    
    def should_upload_now(self) -> bool:
        """Check if current time is optimal"""
        from datetime import datetime
        
        now = datetime.utcnow()
        day = now.strftime('%A').lower()
        current_time = now.strftime('%H:%M')
        
        optimal_times = self.OPTIMAL_TIMES_UTC.get(day, [])
        
        # Check if within 30 minutes of optimal time
        for opt_time in optimal_times:
            opt_hour, opt_min = map(int, opt_time.split(':'))
            curr_hour, curr_min = map(int, current_time.split(':'))
            
            time_diff = abs((opt_hour * 60 + opt_min) - (curr_hour * 60 + curr_min))
            
            if time_diff <= 30:  # Within 30 minutes
                return True
        
        return False
    
    def upload_with_timing(self, video_path: str, metadata: Dict) -> Dict:
        """Upload only at optimal times"""
        if self.should_upload_now():
            logger.info("⏰ Optimal upload time - proceeding")
            return self.uploader.upload_shorts_optimized(
                video_path=video_path,
                **metadata
            )
        else:
            logger.info("⏰ Not optimal time - queuing for later")
            return {'success': False, 'reason': 'Not optimal time', 'queued': True}


# ==================== USAGE EXAMPLE ====================

def main():
    """Example usage"""
    
    # Initialize uploader
    uploader = YouTubeUploader()
    
    # Example 1: Simple upload
    result = uploader.upload_video(
        video_path='test_video.mp4',
        title='This AI Tool Changed Everything',
        description='Learn about this amazing AI tool. Link in description!',
        tags=['AI', 'Technology', 'Tutorial'],
        privacy='public'
    )
    
    print(f"✅ Uploaded: {result['url']}")
    
    # Example 2: Shorts-optimized upload
    result = uploader.upload_shorts_optimized(
        video_path='generated_videos/short_123.mp4',
        hook='This AI Tool Blew My Mind',
        topic='AI automation',
        hashtags=['#AI', '#Shorts', '#Technology', '#Tutorial'],
        affiliate_link='https://customgpt.ai/aff/YOUR_ID'
    )
    
    print(f"✅ Short uploaded: {result['url']}")
    
    # Example 3: Check upload history
    history = uploader.get_upload_history()
    print(f"\n📊 Upload History: {len(history)} videos")
    for upload in history[-5:]:
        print(f"   • {upload['title']}")
        print(f"     {upload['url']}")


if __name__ == "__main__":
    main()
