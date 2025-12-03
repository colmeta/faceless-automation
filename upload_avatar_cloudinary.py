#!/usr/bin/env python3
"""
Upload local avatar image to Cloudinary and return public URL
"""
import os
import sys
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

def upload_avatar_to_cloudinary(local_path: str) -> str:
    """
    Uploads local avatar image to Cloudinary and returns public URL
    """
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        print(f"📤 Uploading {local_path} to Cloudinary...")
        
        # Upload with specific folder and public_id
        result = cloudinary.uploader.upload(
            local_path,
            folder="avatars",
            public_id="user_avatar",
            overwrite=True,
            resource_type="image"
        )
        
        url = result['secure_url']
        print(f"✅ Avatar uploaded: {url}")
        return url
        
    except Exception as e:
        print(f"❌ Cloudinary upload failed: {e}")
        return None

if __name__ == "__main__":
    # Test upload
    avatar_path = "ghgh.jpg"
    if os.path.exists(avatar_path):
        url = upload_avatar_to_cloudinary(avatar_path)
        if url:
            print(f"\n🎉 Success! Use this URL for D-ID:")
            print(f"   {url}")
    else:
        print(f"❌ {avatar_path} not found!")
