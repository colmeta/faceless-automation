#!/usr/bin/env python3
"""
🔐 ONE-CLICK YOUTUBE OAUTH SETUP
Run this ONCE to get your YouTube token for Render
"""

import os
import pickle
import json
import base64
from pathlib import Path

def main():
    print("\n" + "="*70)
    print("🔐 YOUTUBE OAUTH SETUP - ONE-TIME AUTHORIZATION")
    print("="*70 + "\n")
    
    # Step 1: Check for client_secret.json
    if not os.path.exists('client_secret.json'):
        print("❌ ERROR: client_secret.json not found!")
        print("\nYou need to:")
        print("1. Go to: https://console.cloud.google.com")
        print("2. Create OAuth 2.0 credentials (Desktop app)")
        print("3. Download JSON and save as client_secret.json")
        return
    
    print("✅ Found client_secret.json")
    
    # Step 2: Read and convert client_secret to base64
    print("\n📋 Step 1: Converting client_secret.json...")
    with open('client_secret.json', 'r') as f:
        client_secret_data = f.read()
    
    client_secret_b64 = base64.b64encode(client_secret_data.encode()).decode()
    
    print("✅ Converted to base64")
    
    # Step 3: Check if token already exists
    if os.path.exists('token.pickle'):
        print("\n✅ Found existing token.pickle")
        response = input("Do you want to re-authorize? (y/n): ").strip().lower()
        if response != 'y':
            print("\nUsing existing token...")
        else:
            os.remove('token.pickle')
            print("\n🗑️ Deleted old token, will create new one...")
    
    # Step 4: Run OAuth flow if needed
    if not os.path.exists('token.pickle'):
        print("\n🔐 Step 2: Starting OAuth authorization...")
        print("👉 Your browser will open in a moment...")
        print("👉 Sign in and click 'Allow'\n")
        
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            
            SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json',
                SCOPES
            )
            
            credentials = flow.run_local_server(
                port=8080,
                prompt='consent',
                success_message='✅ Authorization successful! You can close this window and return to the terminal.'
            )
            
            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)
            
            print("\n✅ Authorization successful!")
            print("✅ Token saved to token.pickle")
            
        except Exception as e:
            print(f"\n❌ Authorization failed: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure port 8080 is not blocked")
            print("2. Try running as Administrator")
            print("3. Check if browser opened correctly")
            return
    
    # Step 5: Convert token to base64
    print("\n📋 Step 3: Converting token to base64...")
    with open('token.pickle', 'rb') as token:
        token_bytes = token.read()
    
    token_b64 = base64.b64encode(token_bytes).decode()
    
    print("✅ Converted to base64")
    
    # Step 6: Save to files
    print("\n💾 Step 4: Saving to files...")
    
    with open('RENDER_ENV_VARIABLES.txt', 'w') as f:
        f.write("="*70 + "\n")
        f.write("COPY THESE TO RENDER ENVIRONMENT VARIABLES\n")
        f.write("="*70 + "\n\n")
        
        f.write("Variable 1:\n")
        f.write("-"*70 + "\n")
        f.write("Name: YOUTUBE_CLIENT_SECRET_JSON\n")
        f.write("Value:\n")
        f.write(client_secret_data + "\n\n")
        
        f.write("="*70 + "\n\n")
        
        f.write("Variable 2:\n")
        f.write("-"*70 + "\n")
        f.write("Name: YOUTUBE_TOKEN_PICKLE_BASE64\n")
        f.write("Value:\n")
        f.write(token_b64 + "\n\n")
        
        f.write("="*70 + "\n")
    
    print("✅ Saved to RENDER_ENV_VARIABLES.txt")
    
    # Step 7: Print instructions
    print("\n" + "="*70)
    print("🎉 SUCCESS! EVERYTHING IS READY!")
    print("="*70)
    
    print("\n📋 NEXT STEPS:\n")
    print("1. Open the file: RENDER_ENV_VARIABLES.txt")
    print("   (It just opened automatically - check Notepad)")
    print("")
    print("2. Copy Variable 1 (client secret)")
    print("   - Go to Render → Environment")
    print("   - Add: YOUTUBE_CLIENT_SECRET_JSON")
    print("   - Paste the value (entire JSON line)")
    print("")
    print("3. Copy Variable 2 (token)")
    print("   - Add: YOUTUBE_TOKEN_PICKLE_BASE64")
    print("   - Paste the value (long base64 string)")
    print("")
    print("4. Click 'Save' on Render")
    print("   - Render will redeploy automatically")
    print("   - Takes 3-5 minutes")
    print("")
    print("5. Test it:")
    print("   python trigger_automation.py")
    print("")
    print("="*70)
    
    print("\n📝 Quick Copy Reference:")
    print("-"*70)
    print("\nVariable 1 Name:")
    print("YOUTUBE_CLIENT_SECRET_JSON")
    print("\nVariable 1 Value (first 100 chars):")
    print(client_secret_data[:100] + "...")
    print("\n" + "-"*70)
    print("\nVariable 2 Name:")
    print("YOUTUBE_TOKEN_PICKLE_BASE64")
    print("\nVariable 2 Value (first 100 chars):")
    print(token_b64[:100] + "...")
    print("\n" + "="*70)
    
    # Open the file automatically
    try:
        os.startfile('RENDER_ENV_VARIABLES.txt')
    except:
        print("\n💡 TIP: Open RENDER_ENV_VARIABLES.txt to see full values")
    
    print("\n✅ Setup complete! Follow the steps above to finish. 🚀\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted. Run again to complete.\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this error for help.\n")
