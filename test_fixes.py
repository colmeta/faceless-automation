#!/usr/bin/env python3
"""
🧪 QUICK TEST - Test video generation with new fixes
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_video_generation():
    """Test the complete video generation pipeline"""
    print("="*80)
    print("🧪 TESTING VIDEO GENERATION WITH FIXES")
    print("="*80)
    
    try:
        from master_automation import MasterOrchestrator
        
        print("\n📦 Initializing Master Orchestrator...")
        orchestrator = MasterOrchestrator()
        
        print("\n🚀 Running automation cycle...")
        result = orchestrator.run_daily_automation()
        
        print("\n" + "="*80)
        print("✅ TEST PASSED!")
        print("="*80)
        print(f"\n📊 Result: {result}")
        
        if result.get('cloudinary_url'):
            print(f"\n🎥 Cloudinary URL: {result['cloudinary_url']}")
        
        if result.get('youtube_url'):
            print(f"\n📺 YouTube URL: {result['youtube_url']}")
            
        return True
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED!")
        print("="*80)
        print(f"\nError: {e}")
        
        import traceback
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    success = test_video_generation()
    sys.exit(0 if success else 1)
