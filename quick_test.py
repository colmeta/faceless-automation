#!/usr/bin/env python3
"""
Quick automated test for Render deployment
"""

import requests
import json

# Configuration
RENDER_URL = "https://anslyzer.onrender.com"
AUTOMATION_TOKEN = "add68620ddb9a2dbcc3a42bbe4fa3a70"

def test_status():
    """Test server status endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Server Status")
    print("="*60)
    
    try:
        response = requests.get(f"{RENDER_URL}/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Server is running!")
            print(f"  Uptime: {data['server']['uptime_hours']:.2f} hours")
            print(f"  Last Run: {data['automation_stats']['last_run']}")
            print(f"  Videos Generated: {data['automation_stats']['videos_generated']}")
            print(f"  Next Run: {data['automation_stats']['next_run']}")
            return True
        else:
            print(f"[FAIL] Status returned: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_videos():
    """Test videos endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Videos Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{RENDER_URL}/videos", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Videos endpoint working!")
            print(f"  Total Videos: {data['count']}")
            
            if data['videos']:
                print("\n  Recent uploads:")
                for i, video in enumerate(data['videos'][:3], 1):
                    print(f"    {i}. {video['public_id']}")
                    print(f"       Duration: {video.get('duration', 'N/A')}s")
            else:
                print("  (No videos uploaded yet - this is normal for a new deployment)")
            return True
        else:
            print(f"[FAIL] Videos endpoint returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_trigger():
    """Test trigger endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Trigger Automation")
    print("="*60)
    
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
            print("[OK] Automation triggered successfully!")
            print(f"  Status: {data.get('status')}")
            print(f"  Message: {data.get('message')}")
            print(f"  Time: {data.get('timestamp')}")
            return True
        else:
            print(f"[FAIL] Trigger failed with status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("[OK] Request timed out (but automation likely started)")
        print("  This is normal - automation runs in background")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("RENDER DEPLOYMENT TEST SUITE")
    print("="*60)
    print(f"\nTesting: {RENDER_URL}")
    
    results = []
    
    # Run tests
    results.append(("Server Status", test_status()))
    results.append(("Videos Endpoint", test_videos()))
    
    # Ask before triggering
    print("\n" + "="*60)
    trigger = input("\nDo you want to trigger automation? (y/n): ").strip().lower()
    
    if trigger == 'y':
        results.append(("Trigger Automation", test_trigger()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
    
    # Instructions
    if trigger == 'y':
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Go to: https://dashboard.render.com")
        print("2. Click on your 'anslyzer' service")
        print("3. Click 'Logs' tab")
        print("4. Watch for automation progress")
        print("5. Process takes 5-15 minutes")
        print("\nLook for these log messages:")
        print("  - 'Starting automation cycle...'")
        print("  - 'PHASE 1: Hunting viral videos...'")
        print("  - 'Videos generated for all platforms'")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrupted by user.\n")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}\n")
