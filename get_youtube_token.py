#!/usr/bin/env python3
"""
GET YOUTUBE TOKEN - Simple Script
This will authorize YouTube and give you the base64 token string
"""

import os
import pickle
import base64

def main():
    print("\n" + "="*70)
    print("YOUTUBE TOKEN GENERATOR")
    print("="*70 + "\n")
    
    # Check if token already exists
    if os.path.exists('token.pickle'):
        print("[OK] Found existing token.pickle")
        with open('token.pickle', 'rb') as token:
            token_bytes = token.read()
        
        token_b64 = base64.b64encode(token_bytes).decode()
        
        print("\n" + "="*70)
        print("YOUR YOUTUBE TOKEN BASE64 STRING:")
        print("="*70)
        print(token_b64)
        print("="*70)
        print(f"\nLength: {len(token_b64)} characters")
        
        # Save to file
        with open('youtube_token_base64.txt', 'w') as f:
            f.write(token_b64)
        
        print("\n[OK] Also saved to: youtube_token_base64.txt")
        print("\n[TIP] Copy this entire string to your YOUTUBE_TOKEN_PICKLE_BASE64 variable")
        return
    
    # If no token exists, run the OAuth flow
    print("[INFO] No token.pickle found. Starting OAuth flow...\n")
    
    # Check for client_secret
    client_secret_files = [f for f in os.listdir('.') if f.startswith('client_secret') and f.endswith('.json')]
    
    if not client_secret_files:
        print("[ERROR] No client_secret.json found!")
        print("\nYou need to:")
        print("1. Go to: https://console.cloud.google.com")
        print("2. Create OAuth 2.0 credentials (Desktop app)")
        print("3. Download JSON and save in this folder")
        return
    
    client_secret_file = client_secret_files[0]
    print(f"[OK] Found: {client_secret_file}\n")
    
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        
        print("[INFO] Opening browser for authorization...")
        print("  1. Sign in to your YouTube account")
        print("  2. Click 'Continue' or 'Allow'")
        print("  3. Wait for the success message\n")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_file,
            SCOPES
        )
        
        # Run the OAuth flow
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='Authorization successful! You can close this window and return to the terminal.',
            open_browser=True
        )
        
        # Save credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
        
        print("\n[OK] Authorization successful!")
        print("[OK] Token saved to token.pickle\n")
        
        # Convert to base64
        with open('token.pickle', 'rb') as token:
            token_bytes = token.read()
        
        token_b64 = base64.b64encode(token_bytes).decode()
        
        print("="*70)
        print("YOUR YOUTUBE TOKEN BASE64 STRING:")
        print("="*70)
        print(token_b64)
        print("="*70)
        print(f"\nLength: {len(token_b64)} characters")
        
        # Save to file
        with open('youtube_token_base64.txt', 'w') as f:
            f.write(token_b64)
        
        print("\n[OK] Also saved to: youtube_token_base64.txt")
        print("\n[TIP] Copy this entire string to your YOUTUBE_TOKEN_PICKLE_BASE64 variable")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nTroubleshooting:")
        print("1. Make sure port 8080 is available")
        print("2. Check your internet connection")
        print("3. Try running as Administrator")
        print("4. Make sure you clicked 'Allow' in the browser")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Interrupted. Run again to complete.\n")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}\n")
