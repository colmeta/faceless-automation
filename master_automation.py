#!/usr/bin/env python3
"""
👑 MASTER AUTOMATION - COMPLETE FACELESS EMPIRE
Combines: Viral Hunting + Video Generation + Multi-Platform Upload + Analytics
Run once daily = Fully automated income stream
"""

import os
import sys
import json
import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Import all modules
try:
    # Your original autopilot
    from autopilot import AutopilotOrchestrator, Config as AutopilotConfig
    
    # New video generation system
    from faceless_automation import FacelessAutomationPipeline, FreeConfig
    
    # Launch system components
    from complete_launch_system import (
        ViralScriptGenerator,
        HashtagStrategy,
        AnalyticsTracker,
        ThumbnailGenerator,
        CompetitorSpy,
        LaunchCommandCenter
    )
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Make sure all Python files are in the same directory!")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== MASTER CONFIGURATION ====================
class MasterConfig:
    """Master configuration for entire system"""
    
    # Working directories
    ROOT_DIR = Path("faceless_empire")
    GENERATED_VIDEOS = ROOT_DIR / "videos"
    UPLOADED_VIDEOS = ROOT_DIR / "uploaded"
    THUMBNAILS = ROOT_DIR / "thumbnails"
    SCRIPTS = ROOT_DIR / "scripts"
    REPORTS = ROOT_DIR / "reports"
    
    # Automation schedule
    DAILY_RUN_TIME = "09:00"  # Run daily at 9 AM
    VIDEOS_PER_DAY = {
        'youtube': 2,    # Auto-uploaded
        'tiktok': 3,     # Manual (instructions created)
        'instagram': 2   # Manual (instructions created)
    }
    
    # Revenue tracking
    AFFILIATE_PROGRAMS = {
        'CustomGPT': 'https://customgpt.ai/aff/YOUR_ID',
        'Copy.ai': 'https://copy.ai/aff/YOUR_ID',
        'Jasper': 'https://jasper.ai/aff/YOUR_ID',
    }
    
    @classmethod
    def init_all_dirs(cls):
        """Initialize all directories"""
        for dir_path in [cls.GENERATED_VIDEOS, cls.UPLOADED_VIDEOS, 
                        cls.THUMBNAILS, cls.SCRIPTS, cls.REPORTS]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Also init sub-module dirs
        FreeConfig.init_dirs()

# ==================== MASTER ORCHESTRATOR ====================
class MasterOrchestrator:
    """Controls entire automation pipeline"""
    
    def __init__(self):
        MasterConfig.init_all_dirs()
        
        # Initialize all sub-systems
        logger.info("🎬 Initializing Master Orchestrator...")
        
        try:
            self.autopilot = AutopilotOrchestrator()
            self.video_pipeline = FacelessAutomationPipeline()
            self.script_generator = ViralScriptGenerator()
            self.hashtag_engine = HashtagStrategy()
            self.analytics = AnalyticsTracker()
            self.thumbnail_gen = ThumbnailGenerator()
            self.commander = LaunchCommandCenter()
            
            logger.info("✅ All systems initialized!")
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    def run_daily_automation(self):
        """Main daily automation routine"""
        try:
            logger.info("\n" + "="*80)
            logger.info(f"🚀 DAILY AUTOMATION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*80 + "\n")
            
            # PHASE 1: Find viral content
            logger.info("📍 PHASE 1: Hunting viral videos...")
            videos = self.autopilot.hunter.search_trending_ai_videos()
            
            if not videos:
                logger.warning("⚠️  No viral videos found. Using backup script generator.")
                # Fallback: Generate script without source
                script = self.script_generator.generate_script()
                analysis = {
                    'short_hook': script['hook'],
                    'summary': script['full_script'],
                    'key_topics': ', '.join(script['topic_tags']),
                    'cta': script['cta'],
                    'affiliate_angle': script['tool']
                }
            else:
                best_video = videos[0]
                analysis = best_video.get('analysis', {})
                
                # If analysis failed, generate backup
                if 'error' in analysis:
                    logger.warning("⚠️  Analysis failed. Using backup script.")
                    script = self.script_generator.generate_script()
                    analysis = {
                        'short_hook': script['hook'],
                        'summary': script['full_script'],
                        'key_topics': ', '.join(script['topic_tags']),
                        'cta': script['cta'],
                        'affiliate_angle': script['tool']
                    }
            
            logger.info("✅ Content source identified")
            
            # PHASE 2: Generate videos for all platforms
            logger.info("\n📍 PHASE 2: Generating multi-platform videos...")
            
            results = self.video_pipeline.run_full_pipeline(analysis)
            
            logger.info("✅ Videos generated for all platforms")
            
            # PHASE 3: Generate thumbnail
            logger.info("\n📍 PHASE 3: Creating thumbnail...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            thumbnail_path = MasterConfig.THUMBNAILS / f"thumb_{timestamp}.png"
            
            script_for_thumb = {
                'hook': analysis['short_hook'],
                'cta': analysis['cta']
            }
            
            self.thumbnail_gen.generate_thumbnail(script_for_thumb, str(thumbnail_path))
            logger.info("✅ Thumbnail created")
            
            # PHASE 4: Track analytics
            logger.info("\n📍 PHASE 4: Tracking analytics...")
            
            self.analytics.track_video({
                'title': analysis['short_hook'],
                'tool': analysis.get('affiliate_angle', 'AI Tool'),
                'hook_type': 'shock',  # Could be detected from analysis
                'platforms': ['youtube', 'tiktok', 'instagram'],
                'youtube_url': results.get('youtube_url'),
                'thumbnail': str(thumbnail_path)
            })
            
            logger.info("✅ Analytics tracked")
            
            # PHASE 5: Save daily report
            logger.info("\n📍 PHASE 5: Generating daily report...")
            
            self._generate_daily_report(analysis, results, thumbnail_path)
            
            logger.info("✅ Daily report saved")
            
            # PHASE 6: Print summary
            self._print_daily_summary(analysis, results)
            
            logger.info("\n" + "="*80)
            logger.info("🎉 DAILY AUTOMATION COMPLETE!")
            logger.info("="*80 + "\n")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Daily automation failed: {e}")
            raise
    
    def _generate_daily_report(self, analysis: Dict, results: Dict, thumbnail_path: Path):
        """Generate daily report"""
        
        report = {
            'date': datetime.now().isoformat(),
            'analysis': analysis,
            'videos_created': results.get('videos', {}),
            'youtube_url': results.get('youtube_url'),
            'thumbnail': str(thumbnail_path),
            'manual_upload_instructions': results.get('instructions', {})
        }
        
        # Save JSON report
        report_file = MasterConfig.REPORTS / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save human-readable report
        readable_file = MasterConfig.REPORTS / f"DAILY_REPORT_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(readable_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"DAILY AUTOMATION REPORT - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"📹 VIDEO TITLE: {analysis['short_hook']}\n\n")
            
            f.write("🎬 GENERATED VIDEOS:\n")
            for platform, path in results.get('videos', {}).items():
                f.write(f"  ✅ {platform.upper()}: {path}\n")
            
            f.write(f"\n🖼️  THUMBNAIL: {thumbnail_path}\n")
            
            f.write(f"\n📊 YOUTUBE:\n")
            f.write(f"  Status: Auto-uploaded\n")
            f.write(f"  URL: {results.get('youtube_url', 'Upload failed')}\n")
            
            f.write(f"\n📱 TIKTOK (Manual Upload):\n")
            tiktok_inst = results.get('instructions', {}).get('tiktok', {})
            if tiktok_inst:
                f.write(f"  Time: {tiktok_inst.get('scheduled_time')}\n")
                f.write(f"  Video: {tiktok_inst.get('video_path')}\n")
            
            f.write(f"\n📸 INSTAGRAM (Manual Upload):\n")
            insta_inst = results.get('instructions', {}).get('instagram', {})
            if insta_inst:
                f.write(f"  Time: {insta_inst.get('scheduled_time')}\n")
                f.write(f"  Video: {insta_inst.get('video_path')}\n")
            
            f.write("\n" + "="*80 + "\n")
    
    def _print_daily_summary(self, analysis: Dict, results: Dict):
        """Print daily summary to console"""
        
        print("\n" + "╔" + "═"*78 + "╗")
        print("║" + " "*25 + "📊 DAILY SUMMARY" + " "*37 + "║")
        print("╚" + "═"*78 + "╝\n")
        
        print(f"📹 Title: {analysis['short_hook']}")
        print(f"🎯 Tool: {analysis.get('affiliate_angle', 'AI Tool')}")
        print(f"💡 CTA: {analysis['cta']}\n")
        
        print("✅ COMPLETED:")
        print(f"  • 3 videos generated (YouTube, TikTok, Instagram)")
        print(f"  • Thumbnail created")
        print(f"  • YouTube auto-uploaded: {results.get('youtube_url', 'Failed')}")
        print(f"  • Manual upload instructions saved")
        print(f"  • Analytics tracked\n")
        
        print("📋 NEXT STEPS:")
        print(f"  1. Check: upload_queue/README.txt")
        print(f"  2. Upload to TikTok (5 minutes)")
        print(f"  3. Upload to Instagram (5 minutes)")
        print(f"  4. Reply to comments within 1 hour")
        print(f"  5. Check analytics tomorrow\n")
        
        print("╔" + "═"*78 + "╗")
        print("║" + " "*20 + "🔥 KEEP GRINDING! EMPIRE BUILDING! 🔥" + " "*20 + "║")
        print("╚" + "═"*78 + "╝\n")
    
    def run_weekly_analysis(self):
        """Run comprehensive weekly analysis"""
        try:
            logger.info("\n" + "="*80)
            logger.info("📊 WEEKLY ANALYSIS STARTING...")
            logger.info("="*80 + "\n")
            
            # Get best performers
            best_videos = self.analytics.get_best_performers(10)
            insights = self.analytics.get_optimization_insights()
            
            # Analyze competition
            try:
                competitor_report = self.commander.analyze_competition('AI tools')
            except:
                competitor_report = None
                logger.warning("⚠️  Competitor analysis skipped")
            
            # Generate weekly report
            report_file = MasterConfig.REPORTS / f"WEEKLY_REPORT_{datetime.now().strftime('%Y_W%W')}.txt"
            
            with open(report_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write(f"WEEKLY PERFORMANCE REPORT - Week {datetime.now().strftime('%W, %Y')}\n")
                f.write("="*80 + "\n\n")
                
                f.write("🏆 TOP 10 PERFORMERS:\n\n")
                for i, video in enumerate(best_videos, 1):
                    total_views = sum([video.get(p, {}).get('views', 0) for p in ['youtube', 'tiktok', 'instagram']])
                    f.write(f"{i}. {video['title']}\n")
                    f.write(f"   Total Views: {total_views:,}\n")
                    f.write(f"   Tool: {video.get('tool', 'Unknown')}\n\n")
                
                f.write("\n💡 KEY INSIGHTS:\n\n")
                if insights.get('best_hook_types'):
                    f.write(f"Best Hook Type: {insights['best_hook_types'][0][0]}\n")
                if insights.get('best_tools'):
                    f.write(f"Best Performing Tool: {insights['best_tools'][0][0]}\n")
                f.write(f"Average Views: {insights.get('avg_views', 0):,.0f}\n")
                
                f.write(f"\n📈 RECOMMENDATION:\n")
                f.write(f"{insights.get('recommendation', 'Keep posting consistently!')}\n")
                
                f.write("\n" + "="*80 + "\n")
            
            # Print analytics dashboard
            self.analytics.print_dashboard()
            
            logger.info(f"✅ Weekly report saved: {report_file}\n")
            
        except Exception as e:
            logger.error(f"❌ Weekly analysis failed: {e}")
    
    def setup_scheduler(self):
        """Setup automated scheduling"""
        logger.info("⏰ Setting up automation scheduler...")
        
        # Daily run at 9 AM
        schedule.every().day.at(MasterConfig.DAILY_RUN_TIME).do(self.run_daily_automation)
        
        # Weekly analysis every Monday at 10 AM
        schedule.every().monday.at("10:00").do(self.run_weekly_analysis)
        
        logger.info(f"✅ Scheduled daily runs at {MasterConfig.DAILY_RUN_TIME}")
        logger.info("✅ Scheduled weekly analysis every Monday at 10:00")
        logger.info("\n🤖 Automation is now running in the background...")
        logger.info("Press Ctrl+C to stop\n")
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

# ==================== CLI INTERFACE ====================
def print_banner():
    """Print fancy banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ███████╗ █████╗  ██████╗███████╗██╗     ███████╗███████╗███████╗        ║
║     ██╔════╝██╔══██╗██╔════╝██╔════╝██║     ██╔════╝██╔════╝██╔════╝        ║
║     █████╗  ███████║██║     █████╗  ██║     █████╗  ███████╗███████╗        ║
║     ██╔══╝  ██╔══██║██║     ██╔══╝  ██║     ██╔══╝  ╚════██║╚════██║        ║
║     ██║     ██║  ██║╚██████╗███████╗███████╗███████╗███████║███████║        ║
║     ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝        ║
║                                                                               ║
║              🤖 COMPLETE AUTOMATION MASTER CONTROL 🤖                         ║
║                     Build Your Empire While You Sleep                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """Main entry point"""
    
    print_banner()
    
    print("\n🎯 MASTER AUTOMATION MODES:\n")
    print("  1. 🚀 Run Once (Generate today's content)")
    print("  2. 🤖 Auto Mode (Run daily automatically)")
    print("  3. 📊 View Analytics")
    print("  4. 📋 Launch Setup (First time setup)")
    print("  5. 🕵️  Analyze Competition")
    print("  6. ❌ Exit\n")
    
    choice = input("Select mode (1-6): ").strip()
    
    try:
        orchestrator = MasterOrchestrator()
        
        if choice == '1':
            # Run once
            print("\n🚀 Running single automation cycle...\n")
            orchestrator.run_daily_automation()
            
        elif choice == '2':
            # Auto mode
            print("\n🤖 Starting automated mode...\n")
            orchestrator.setup_scheduler()
            
        elif choice == '3':
            # Analytics
            print("\n📊 Loading analytics...\n")
            orchestrator.analytics.print_dashboard()
            
        elif choice == '4':
            # Launch setup
            print("\n📋 Running launch setup...\n")
            launch_package = orchestrator.commander.prepare_30_day_launch()
            checklist = orchestrator.commander.create_launch_checklist()
            print(checklist)
            
        elif choice == '5':
            # Competition analysis
            print("\n🕵️  Analyzing competition...\n")
            orchestrator.commander.analyze_competition('AI tools')
            
        elif choice == '6':
            print("\n👋 Goodbye! Keep grinding!\n")
            sys.exit(0)
            
        else:
            print("\n❌ Invalid choice. Please select 1-6.\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Automation stopped by user. Goodbye!\n")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}\n")
        print("\n💡 TIP: Make sure all dependencies are installed and API keys are set!\n")
        sys.exit(1)

if __name__ == "__main__":
    main()