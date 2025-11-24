#!/usr/bin/env python3
"""
Simple script to trigger your Render automation
Usage: python trigger_automation.py
"""

import requests
import json
import time

# Configuration
RENDER_URL = "https://anslyzer.onrender.com"
AUTOMATION_TOKEN = "add68620ddb9a2dbcc3a42bbe4fa3a70"  # Your token

def trigger_automation():
    """Trigger the automation"""
    print("🚀 Triggering automation...")
    
    try:
        response = requests.post(
            f"{RENDER_URL}/trigger",
            headers={
                "Authorization": f"Bearer {AUTOMATION_TOKEN}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            print(f"   Time: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠️ Request timed out (but automation may have started)")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_status():
    """Check server status"""
    print("\n📊 Checking server status...")
    
    try:
        response = requests.get(f"{RENDER_URL}/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status:")
            print(f"   Uptime: {data['server']['uptime_hours']:.2f} hours")
            print(f"   Last Run: {data['automation_stats']['last_run']}")
            print(f"   Videos Generated: {data['automation_stats']['videos_generated']}")
            print(f"   Next Run: {data['automation_stats']['next_run']}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Status check error: {e}")

def check_videos():
    """Check uploaded videos"""
    print("\n📹 Checking videos...")
    
    try:
        response = requests.get(f"{RENDER_URL}/videos", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Videos: {data['count']} total")
            
            if data['videos']:
                print("\n   Recent uploads:")
                for video in data['videos'][:5]:
                    print(f"   • {video['public_id']}")
                    print(f"     Duration: {video.get('duration', 'N/A')}s")
                    print(f"     URL: {video['url'][:60]}...")
            else:
                print("   No videos uploaded yet")
        else:
            print(f"⚠️ Videos check returned: {response.status_code}")
            print(f"   (This is normal if no videos exist yet)")
            
    except Exception as e:
        print(f"❌ Videos check error: {e}")

def monitor_logs():
    """Instructions for monitoring logs"""
    print("\n" + "="*60)
    print("📋 MONITORING INSTRUCTIONS")
    print("="*60)
    print("\n1. Go to: https://dashboard.render.com")
    print("2. Click on your 'anslyzer' service")
    print("3. Click 'Logs' tab")
    print("4. Watch for these messages:")
    print("   • '🚀 Starting automation cycle...'")
    print("   • '📍 PHASE 1: Hunting viral videos...'")
    print("   • '✅ Videos generated for all platforms'")
    print("\n5. The process takes 5-15 minutes")
    print("\n" + "="*60)

def main():
    """Main menu"""
    print("\n" + "="*60)
    print("🎬 RENDER AUTOMATION CONTROLLER")
    print("="*60)
    
    print("\nOptions:")
    print("  1. Trigger Automation Now")
    print("  2. Check Status")
    print("  3. Check Videos")
    print("  4. Full Check (All)")
    print("  5. Monitor Instructions")
    print("  6. Exit")
    
    choice = input("\nSelect (1-6): ").strip()
    
    if choice == "1":
        trigger_automation()
        print("\n💡 TIP: Check Render logs to see progress")
        time.sleep(2)
        monitor_logs()
        
    elif choice == "2":
        check_status()
        
    elif choice == "3":
        check_videos()
        
    elif choice == "4":
        check_status()
        check_videos()
        
    elif choice == "5":
        monitor_logs()
        
    elif choice == "6":
        print("\n👋 Goodbye!\n")
        return
    else:
        print("\n❌ Invalid choice")
    
    # Ask to continue
    print("\n" + "="*60)
    again = input("Run another command? (y/n): ").strip().lower()
    if again == 'y':
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
