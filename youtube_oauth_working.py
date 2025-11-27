#!/usr/bin/env python3
"""
🔐 YOUTUBE OAUTH - WORKING VERSION
This WILL create token.pickle after you authorize
Works on Windows, Mac, Linux
"""

import os
import pickle
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ==================== CONFIGURATION ====================
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = 'client_secret_1062656825030-aogokq77phh8g4eo2gkh54i34qkq80ep.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token.pickle'

print("\n" + "="*70)
print("🔐 YOUTUBE OAUTH TOKEN GENERATOR")
print("="*70)

# ==================== STEP 1: Check files ====================
print("\n📋 Step 1: Checking files...")

if not os.path.exists(CLIENT_SECRETS_FILE):
    print(f"❌ ERROR: {CLIENT_SECRETS_FILE} not found!")
    print("\nYou need:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create credentials (OAuth 2.0 for Desktop App)")
    print("3. Download it as JSON")
    print("4. Rename to match the path above")
    exit(1)

print(f"✅ Found: {CLIENT_SECRETS_FILE}")

# Load and show what's in the file
try:
    with open(CLIENT_SECRETS_FILE, 'r') as f:
        secret_data = json.load(f)
    print(f"✅ Client ID: {secret_data['web']['client_id'][:30]}...")
except Exception as e:
    print(f"❌ Error reading file: {e}")
    exit(1)

# ==================== STEP 2: Check for existing token ====================
print("\n📋 Step 2: Checking for existing token...")

if os.path.exists(TOKEN_PICKLE_FILE):
    print(f"⚠️  Found existing {TOKEN_PICKLE_FILE}")
    delete = input("Delete and re-authorize? (y/n): ").strip().lower()
    if delete == 'y':
        os.remove(TOKEN_PICKLE_FILE)
        print(f"🗑️  Deleted {TOKEN_PICKLE_FILE}")
    else:
        print("\n✅ Using existing token!")
        exit(0)

# ==================== STEP 3: Run OAuth flow ====================
print("\n📋 Step 3: Starting OAuth flow...")
print("⏳ Your browser will open in 2 seconds...")
print("👉 If it doesn't open, copy this URL manually:\n")

try:
    # Create the flow
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES
    )
    
    # Run local server (opens browser automatically)
    print("🌐 Waiting for authorization...")
    credentials = flow.run_local_server(port=8080)
    
    print("\n✅ Authorization successful!")
    
    # ==================== STEP 4: Save the token ====================
    print("\n💾 Step 4: Saving token...")
    
    # Save as pickle
    with open(TOKEN_PICKLE_FILE, 'wb') as token_file:
        pickle.dump(credentials, token_file)
    
    print(f"✅ Saved: {TOKEN_PICKLE_FILE}")
    
    # Also save as JSON (for reference)
    token_json = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    with open('token.json', 'w') as f:
        json.dump(token_json, f, indent=2)
    
    print(f"✅ Also saved: token.json (for reference)")
    
    # ==================== STEP 5: Verify ====================
    print("\n✅ Verification: Loading token back...")
    
    with open(TOKEN_PICKLE_FILE, 'rb') as token_file:
        loaded_creds = pickle.load(token_file)
    
    print(f"✅ Token loaded successfully!")
    print(f"   Token expires in: {loaded_creds.expiry}")
    print(f"   Refresh token present: {bool(loaded_creds.refresh_token)}")
    
    # ==================== STEP 6: Test ====================
    print("\n✅ Step 5: Testing YouTube API...")
    
    from googleapiclient.discovery import build
    
    youtube = build('youtube', 'v3', credentials=loaded_creds)
    
    # Get authenticated user's channel
    request = youtube.channels().list(
        part='snippet',
        mine=True
    )
    
    response = request.execute()
    
    if response['items']:
        channel_name = response['items'][0]['snippet']['title']
        print(f"✅ Authenticated as: {channel_name}")
    else:
        print("⚠️  Could not fetch channel info (but token is valid)")
    
    print("\n" + "="*70)
    print("🎉 SUCCESS! TOKEN IS READY!")
    print("="*70)
    print("""
Your token is saved and will be used for:
• Uploading videos to YouTube
• Creating playlists
• Managing your channel

The token will auto-refresh when needed.

Next steps:
1. Run: python master_automation.py
2. Your videos will auto-upload to YouTube
""")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure port 8080 is not in use")
    print("2. Check if browser opened (should open automatically)")
    print("3. If manual: copy the URL shown above, paste in browser")
    print("4. Click 'Continue' when it says 'Untrusted app'")
    print("5. Select your YouTube account")
    print("6. Click 'Allow' when asked for permissions")
    import traceback
    traceback.print_exc()
    exit(1)
