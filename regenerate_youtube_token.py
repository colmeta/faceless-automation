#!/usr/bin/env python3
"""
🔑 YouTube Token Regenerator
Regenerates the YOUTUBE_TOKEN_PICKLE_BASE64 for Render
"""

import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

print("\n" + "="*60)
print("🔑 YOUTUBE TOKEN REGENERATOR")
print("="*60 + "\n")

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Check for client_secret.json
if not os.path.exists('client_secret.json'):
    print("❌ ERROR: client_secret.json not found!")
    print("\n📝 You need to:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Select your project (or create one)")
    print("3. Enable YouTube Data API v3")
    print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client ID'")
    print("5. Application type: 'Desktop app'")
    print("6. Download the JSON file and save as 'client_secret.json'")
    exit(1)

print("✅ Found client_secret.json")
print("\n🔄 Starting OAuth flow...")
print("📌 A browser window will open for authentication")
print("   If it doesn't open automatically, copy the URL from the terminal\n")

try:
    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', 
        SCOPES
    )
    
    # This will open a browser for authentication
    creds = flow.run_local_server(port=8080)
    
    print("\n✅ Authentication successful!")
    
    # Save to pickle file
    with open('youtube_token.pickle', 'wb') as f:
        pickle.dump(creds, f)
    
    print("✅ Saved to youtube_token.pickle")
    
    # Convert to base64
    with open('youtube_token.pickle', 'rb') as f:
        pickle_data = f.read()
    
    base64_token = base64.b64encode(pickle_data).decode('utf-8')
    
    # Save to text file for easy copying
    with open('YOUTUBE_TOKEN_BASE64.txt', 'w') as f:
        f.write(base64_token)
    
    print("✅ Base64 token saved to YOUTUBE_TOKEN_BASE64.txt")
    
    print("\n" + "="*60)
    print("🎉 TOKEN GENERATED SUCCESSFULLY!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("1. Open YOUTUBE_TOKEN_BASE64.txt")
    print("2. Copy the entire content (it's one long line)")
    print("3. Go to Render Dashboard → anslyzer → Environment")
    print("4. Find YOUTUBE_TOKEN_PICKLE_BASE64")
    print("5. Replace the old value with the new token")
    print("6. Click 'Save Changes'")
    print("7. Render will auto-redeploy with the new token")
    print("\n✅ Done! Your YouTube uploads will work again.")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n💡 TROUBLESHOOTING:")
    print("- Make sure client_secret.json is valid")
    print("- Check that YouTube Data API v3 is enabled")
    print("- Ensure your Google account has access to the YouTube channel")
    exit(1)
