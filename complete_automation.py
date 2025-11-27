#!/usr/bin/env python3
"""
🚀 COMPLETE FACELESS AUTOMATION - PRODUCTION READY
End-to-end: Find video → Analyze → Generate → Upload → Track
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faceless_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import all components
from complete_launch_system import (
    ViralScriptGenerator,
    HashtagStrategy,
    AnalyticsTracker
)

# Import based on environment
if os.getenv('RENDER'):
    from faceless_automation_render import VideoGenerationPipeline
    logger.info("📦 Using Render-optimized pipeline")
else:
    from faceless_automation import VideoGenerationPipeline
    logger.info("📦 Using full-featured pipeline")


class CompleteAutomation:
    """Complete end-to-end automation system"""
    
    def __init__(self):
        logger.info("🚀 Initializing Complete Automation System")
        
        # Initialize components
        self.script_gen = ViralScriptGenerator()
        self.hashtag_engine = HashtagStrategy()
        self.video_pipeline = VideoGenerationPipeline()
        self.analytics = AnalyticsTracker()
        
        # YouTube uploader (optional - only if OAuth configured)
        self.youtube_uploader = None
        if os.path.exists('token.pickle'):
            try:
                from youtube_uploader import YouTubeUploader
                self.youtube_uploader = YouTubeUploader()
                logger.info("✅ YouTube uploader initialized")
            except Exception as e:
                logger.warning(f"⚠️ YouTube uploader not available: {e}")
        
        # Create directories
        Path("faceless_empire/videos").mkdir(parents=True, exist_ok=True)
        Path("faceless_empire/reports").mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Initialization complete")
    
    def run_full_cycle(self, upload_to_youtube: bool = False) -> Dict:
        """Run complete automation cycle"""
        
        logger.info("\n" + "="*80)
        logger.info(f"🎬 STARTING FULL AUTOMATION CYCLE - {datetime.now()}")
        logger.info("="*80 + "\n")
        
        try:
            # PHASE 1: GENERATE SCRIPT
            logger.info("📝 PHASE 1: Generating viral script...")
            script = self.script_gen.generate_script()
            
            logger.info(f"   Hook: {script['hook']}")
            logger.info(f"   Tool: {script['tool']}")
            logger.info(f"   Affiliate: {script['affiliate_link']}")
            
            # PHASE 2: GENERATE VIDEO
            logger.info("\n🎬 PHASE 2: Generating video...")
            
            video_script = {
                'narration': script['full_script'],
                'hook': script['hook'],
                'cta': script['cta'],
                'topic': script['use_case']
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"ai_short_{timestamp}.mp4"
            
            video_result = self.video_pipeline.generate_single_video(
                video_script,
                video_filename
            )
            
            if isinstance(video_result, str) and video_result.startswith('http'):
                logger.info(f"✅ Video uploaded to Cloudinary: {video_result}")
                video_path = video_result
                is_cloudinary = True
            else:
                logger.info(f"✅ Video generated: {video_result}")
                video_path = video_result
                is_cloudinary = False
            
            # PHASE 3: GENERATE METADATA
            logger.info("\n📊 PHASE 3: Generating metadata...")
            
            hashtags = self.hashtag_engine.generate_hashtags('youtube', script['tool'])
            description = self._build_description(script, hashtags)
            
            logger.info(f"   Title: {script['hook'][:60]}")
            logger.info(f"   Hashtags: {' '.join(hashtags[:5])}")
            
            # PHASE 4: UPLOAD TO YOUTUBE (Optional)
            youtube_url = None
            
            if upload_to_youtube and self.youtube_uploader and not is_cloudinary:
                logger.info("\n📤 PHASE 4: Uploading to YouTube...")
                
                try:
                    upload_result = self.youtube_uploader.upload_shorts_optimized(
                        video_path=video_path,
                        hook=script['hook'],
                        topic=script['use_case'],
                        hashtags=hashtags,
                        affiliate_link=script['affiliate_link']
                    )
                    
                    if upload_result['success']:
                        youtube_url = upload_result['url']
                        logger.info(f"✅ YouTube URL: {youtube_url}")
                    
                except Exception as e:
                    logger.error(f"❌ YouTube upload failed: {e}")
            else:
                logger.info("\n📤 PHASE 4: Skipped (YouTube upload not configured)")
            
            # PHASE 5: TRACK ANALYTICS
            logger.info("\n📊 PHASE 5: Updating analytics...")
            
            video_data = {
                'title': script['hook'],
                'tool': script['tool'],
                'hook_type': 'shock',  # Could be determined from script
                'video_path': video_path,
                'youtube_url': youtube_url,
                'cloudinary_url': video_path if is_cloudinary else None,
                'affiliate_link': script['affiliate_link'],
                'hashtags': hashtags,
                'description': description,
                'created_at': datetime.now().isoformat()
            }
            
            self.analytics.track_video(video_data)
            
            # PHASE 6: GENERATE REPORT
            logger.info("\n📋 PHASE 6: Generating report...")
            
            report = self._generate_report(script, video_data, youtube_url)
            
            # Save report
            report_file = f"faceless_empire/reports/cycle_{timestamp}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✅ Report saved: {report_file}")
            
            # Print summary
            self._print_summary(report)
            
            logger.info("\n" + "="*80)
            logger.info("🎉 AUTOMATION CYCLE COMPLETE!")
            logger.info("="*80 + "\n")
            
            return report
        
        except Exception as e:
            logger.error(f"❌ Automation cycle failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _build_description(self, script: Dict, hashtags: List[str]) -> str:
        """Build YouTube description"""
        return f"""{script['hook']}

🔗 TRY IT FREE:
{script['affiliate_link']}

📱 FOLLOW FOR DAILY AI TIPS
Get the latest AI tools and automation hacks

⚡ WHAT YOU'LL LEARN:
How to use {script['tool']} to {script['use_case']}

💡 WHY THIS MATTERS:
{script['pain_point']} is costing you time and money. This tool fixes that.

🎯 CALL TO ACTION:
{script['cta']}

{' '.join(hashtags)}

---
✨ This channel uses AI automation to bring you the best tools daily
💙 Your support helps me create more content
🔔 Subscribe for daily AI tips

#AI #ArtificialIntelligence #Technology #Tutorial #Shorts #Automation #Productivity"""
    
    def _generate_report(self, script: Dict, video_data: Dict, youtube_url: str = None) -> Dict:
        """Generate detailed report"""
        return {
            'cycle_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'timestamp': datetime.now().isoformat(),
            'script': {
                'hook': script['hook'],
                'tool': script['tool'],
                'use_case': script['use_case'],
                'affiliate_link': script['affiliate_link']
            },
            'video': {
                'path': video_data['video_path'],
                'youtube_url': youtube_url,
                'cloudinary_url': video_data.get('cloudinary_url')
            },
            'metadata': {
                'title': video_data['title'],
                'description': video_data['description'][:200] + '...',
                'hashtags': video_data['hashtags']
            },
            'status': 'success',
            'next_steps': [
                'Monitor YouTube analytics',
                'Track affiliate clicks',
                'Respond to comments',
                'Cross-post to TikTok/Instagram'
            ]
        }
    
    def _print_summary(self, report: Dict):
        """Print cycle summary"""
        logger.info("\n" + "╔" + "="*78 + "╗")
        logger.info("║" + " "*28 + "CYCLE SUMMARY" + " "*37 + "║")
        logger.info("╚" + "="*78 + "╝")
        
        logger.info(f"\n📝 Script Generated:")
        logger.info(f"   Hook: {report['script']['hook']}")
        logger.info(f"   Tool: {report['script']['tool']}")
        
        logger.info(f"\n🎬 Video Created:")
        logger.info(f"   Path: {report['video']['path'][:60]}...")
        
        if report['video']['youtube_url']:
            logger.info(f"\n📤 YouTube Upload:")
            logger.info(f"   URL: {report['video']['youtube_url']}")
        
        logger.info(f"\n🔗 Affiliate Link:")
        logger.info(f"   {report['script']['affiliate_link']}")
        
        logger.info(f"\n✅ Next Steps:")
        for step in report['next_steps']:
            logger.info(f"   • {step}")
    
    def run_daily_batch(self, count: int = 3, upload_to_youtube: bool = False):
        """Run multiple cycles for daily content"""
        logger.info(f"\n🚀 STARTING DAILY BATCH: {count} videos")
        
        results = []
        
        for i in range(count):
            logger.info(f"\n{'='*80}")
            logger.info(f"VIDEO {i+1}/{count}")
            logger.info(f"{'='*80}")
            
            try:
                result = self.run_full_cycle(upload_to_youtube)
                results.append(result)
                
                # Brief pause between videos
                if i < count - 1:
                    import time
                    logger.info("\n⏸️  Pausing 30 seconds before next video...")
                    time.sleep(30)
            
            except Exception as e:
                logger.error(f"❌ Video {i+1} failed: {e}")
                results.append({'status': 'failed', 'error': str(e)})
        
        # Final summary
        self._print_batch_summary(results)
        
        return results
    
    def _print_batch_summary(self, results: List[Dict]):
        """Print batch summary"""
        successful = [r for r in results if r.get('status') == 'success']
        failed = [r for r in results if r.get('status') == 'failed']
        
        logger.info("\n" + "╔" + "="*78 + "╗")
        logger.info("║" + " "*28 + "BATCH SUMMARY" + " "*37 + "║")
        logger.info("╚" + "="*78 + "╝")
        
        logger.info(f"\n📊 Results:")
        logger.info(f"   ✅ Successful: {len(successful)}")
        logger.info(f"   ❌ Failed: {len(failed)}")
        
        if successful:
            logger.info(f"\n🎬 Videos Generated:")
            for r in successful:
                logger.info(f"   • {r['script']['hook'][:60]}")
                if r['video']['youtube_url']:
                    logger.info(f"     {r['video']['youtube_url']}")
        
        if failed:
            logger.info(f"\n⚠️ Failures:")
            for r in failed:
                logger.info(f"   • Error: {r.get('error', 'Unknown')}")


# ==================== CLI ====================

def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Faceless AI Automation')
    parser.add_argument(
        '--mode',
        choices=['single', 'batch', 'daily'],
        default='single',
        help='Automation mode'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='Number of videos for batch mode'
    )
    parser.add_argument(
        '--upload',
        action='store_true',
        help='Upload to YouTube (requires OAuth)'
    )
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = CompleteAutomation()
    
    # Check YouTube upload capability
    if args.upload and not automation.youtube_uploader:
        logger.warning("⚠️ YouTube upload requested but not configured")
        logger.warning("   Run: python youtube_uploader.py to set up OAuth")
        logger.warning("   Continuing without YouTube upload...")
        args.upload = False
    
    # Run automation
    if args.mode == 'single':
        logger.info("🎬 Running single video automation")
        automation.run_full_cycle(args.upload)
    
    elif args.mode == 'batch':
        logger.info(f"🎬 Running batch automation: {args.count} videos")
        automation.run_daily_batch(args.count, args.upload)
    
    elif args.mode == 'daily':
        logger.info("🎬 Running daily automation (3 videos)")
        automation.run_daily_batch(3, args.upload)
    
    # Print analytics
    automation.analytics.print_dashboard()


if __name__ == "__main__":
    main()
