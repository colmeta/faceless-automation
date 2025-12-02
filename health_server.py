#!/usr/bin/env python3
"""
🏥 COMPLETE HEALTH SERVER - WITH CLOUDINARY INTEGRATION
Full-featured server with video storage, keep-alive, and all endpoints
"""

from flask import Flask, jsonify, request
import threading
import requests
import time
import os
import sys
from datetime import datetime, timezone
import logging
from dotenv import load_dotenv
import shutil
import cloudinary
import cloudinary.uploader
import cloudinary.api
from pathlib import Path

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['START_TIME'] = time.time()
app.config['VIDEOS_COUNT'] = 0
app.config['LAST_RUN'] = 'Never'
app.config['NEXT_RUN'] = 'Scheduled'

# Global lock to prevent concurrent runs (Critical for Render 512MB limit)
AUTOMATION_LOCK = threading.Lock()

# ==================== CLOUDINARY SETUP ====================
try:
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    CLOUDINARY_ENABLED = bool(os.getenv('CLOUDINARY_CLOUD_NAME'))
    if CLOUDINARY_ENABLED:
        logger.info("✅ Cloudinary configured")
except Exception as e:
    CLOUDINARY_ENABLED = False
    logger.warning(f"⚠️ Cloudinary not configured: {e}")

# ==================== ENDPOINTS ====================

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Faceless YouTube Automation',
        'status': 'running',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'message': '🚀 Full Stack Automation Live!',
        'features': {
            'video_generation': 'enabled',
            'youtube_upload': 'enabled',
            'cloudinary_storage': 'enabled' if CLOUDINARY_ENABLED else 'disabled',
            'analytics': 'enabled',
            'keep_alive': 'enabled'
        },
        'endpoints': {
            '/health': 'Health check (for keep-alive)',
            '/status': 'Detailed system status',
            '/trigger': 'Manually trigger automation (POST)',
            '/stats': 'View analytics statistics',
            '/upload': 'Upload video to Cloudinary (POST)',
            '/videos': 'List uploaded videos'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for GitHub Actions keep-alive"""
    uptime = time.time() - app.config.get('START_TIME', time.time())
    return jsonify({
        'status': 'alive',
        'timestamp': time.time(),
        'uptime_seconds': uptime,
        'uptime_hours': round(uptime / 3600, 2),
        'healthy': True
    })

@app.route('/status')
def status():
    """Detailed status information"""
    try:
        # Get disk usage
        total, used, free = shutil.disk_usage("/")
        
        # Check environment variables
        env_status = {
            'youtube_api': bool(os.getenv('YOUTUBE_API_KEY')),
            'pixabay_api': bool(os.getenv('PIXABAY_API_KEY')),
            'gemini_api': bool(os.getenv('GEMINI_API_KEY')),
            'cloudinary': CLOUDINARY_ENABLED,
            'anthropic_api': bool(os.getenv('ANTHROPIC_API_KEY')),
            'openai_api': bool(os.getenv('OPENAI_API_KEY')),
            'groq_api': bool(os.getenv('GROQ_API_KEY')),
        }
        
        return jsonify({
            'status': 'operational',
            'automation': 'running',
            'server': {
                'uptime_hours': round((time.time() - app.config['START_TIME']) / 3600, 2),
                'python_version': sys.version.split()[0],
                'platform': sys.platform
            },
            'disk_usage': {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'percent_used': round((used / total) * 100, 2)
            },
            'automation_stats': {
                'last_run': app.config.get('LAST_RUN', 'Never'),
                'next_run': app.config.get('NEXT_RUN', 'Unknown'),
                'videos_generated': app.config.get('VIDEOS_COUNT', 0)
            },
            'environment': env_status,
            'cloudinary': {
                'enabled': CLOUDINARY_ENABLED,
                'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME', 'not configured')
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/trigger', methods=['POST'])
def trigger_automation():
    """Manually trigger automation"""
    try:
        # Check authorization
        auth_header = request.headers.get('Authorization')
        expected_token = os.getenv('AUTOMATION_TOKEN', 'default-secret-token')
        
        if auth_header != f"Bearer {expected_token}":
            return jsonify({'error': 'Unauthorized'}), 401
        
        logger.info("🚀 Manual automation trigger received")
        
        # Run automation in background
        if AUTOMATION_LOCK.locked():
            return jsonify({'error': 'Automation already running', 'status': 'busy'}), 429
            
        thread = threading.Thread(target=run_automation_once, daemon=True)
        thread.start()
        
        return jsonify({
            'status': 'triggered',
            'message': 'Automation started in background',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Trigger failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def stats():
    """View automation statistics"""
    try:
        import json
        
        # Try to load analytics
        analytics_file = 'analytics.json'
        if os.path.exists(analytics_file):
            with open(analytics_file, 'r') as f:
                data = json.load(f)
            
            return jsonify({
                'total_videos': data.get('total_videos', 0),
                'total_views': data.get('total_views', 0),
                'platform_stats': data.get('platform_stats', {}),
                'best_performing': data.get('best_performing', [])[:5],
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'total_videos': 0,
                'total_views': 0,
                'message': 'No analytics data yet',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-ui')
def test_ui():
    """Mobile-friendly API testing interface"""
    html = '''
    <!-- The entire HTML from the artifact above -->
    '''
    return html
    
@app.route('/upload', methods=['POST'])
def upload_video():
    """Upload video to Cloudinary"""
    if not CLOUDINARY_ENABLED:
        return jsonify({'error': 'Cloudinary not configured'}), 503
    
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        platform = request.form.get('platform', 'youtube')
        
        # Save temporarily
        temp_path = f"/tmp/{video_file.filename}"
        video_file.save(temp_path)
        
        logger.info(f"☁️ Uploading to Cloudinary: {video_file.filename}")
        
        # Upload to Cloudinary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        public_id = f"faceless/{platform}/{timestamp}"
        
        result = cloudinary.uploader.upload_large(
            temp_path,
            resource_type="video",
            public_id=public_id,
            folder="faceless_videos",
            chunk_size=6000000
        )
        
        # Delete local file
        os.remove(temp_path)
        
        logger.info(f"✅ Uploaded: {result['secure_url']}")
        
        return jsonify({
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'duration': result.get('duration'),
            'format': result.get('format'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/videos')
def list_videos():
    """List uploaded videos from Cloudinary"""
    if not CLOUDINARY_ENABLED:
        return jsonify({'error': 'Cloudinary not configured'}), 503
    
    try:
        # Get videos from Cloudinary
        result = cloudinary.api.resources(
            type="upload",
            resource_type="video",
            prefix="faceless_videos/",
            max_results=50
        )
        
        videos = [{
            'public_id': video['public_id'],
            'url': video['secure_url'],
            'format': video['format'],
            'duration': video.get('duration'),
            'created_at': video['created_at']
        } for video in result['resources']]
        
        return jsonify({
            'count': len(videos),
            'videos': videos,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ List videos failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug-cloudinary', methods=['GET'])
def debug_cloudinary():
    """Debug Cloudinary configuration and upload"""
    try:
        # 1. Check Config
        config_status = {
            'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
            'api_key': os.getenv('CLOUDINARY_API_KEY')[:5] + '...' if os.getenv('CLOUDINARY_API_KEY') else None,
            'api_secret': 'Set' if os.getenv('CLOUDINARY_API_SECRET') else 'Missing',
            'enabled': CLOUDINARY_ENABLED
        }
        
        if not CLOUDINARY_ENABLED:
            return jsonify({'status': 'disabled', 'config': config_status}), 200
            
        # 2. Create dummy file
        dummy_path = "debug_test.txt"
        with open(dummy_path, "w") as f:
            f.write(f"Debug upload test {datetime.now()}")
            
        # 3. Try Upload
        logger.info("🧪 Starting debug upload...")
        result = cloudinary.uploader.upload(
            dummy_path,
            resource_type="raw",
            public_id=f"debug/test_{int(time.time())}",
            folder="faceless_debug"
        )
        
        # 4. Cleanup
        if os.path.exists(dummy_path):
            os.remove(dummy_path)
            
        return jsonify({
            'status': 'success',
            'url': result.get('secure_url'),
            'config': config_status
        })
        
    except Exception as e:
        logger.error(f"❌ Debug upload failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'config': config_status
        }), 500

@app.route('/debug-video', methods=['GET'])
def debug_video():
    """Debug video generation (1 second test)"""
    try:
        from faceless_automation_render import VideoGenerationPipeline
        
        pipeline = VideoGenerationPipeline()
        
        # Simple 1-second script
        script = {
            'narration': "Test.",
            'hook': "TEST",
            'cta': "TEST",
            'topic': "test"
        }
        
        # Override duration for speed
        from faceless_automation_render import VideoGenConfig
        VideoGenConfig.DURATION = 2
        
        # Generate
        logger.info("🧪 Starting debug video generation...")
        video_path = pipeline.generate_single_video(script, f"debug_{int(time.time())}.mp4")
        
        return jsonify({
            'status': 'success',
            'result': video_path,
            'is_url': video_path.startswith('http')
        })
        
    except Exception as e:
        logger.error(f"❌ Debug video failed: {e}")
        import traceback
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

def run_automation_once():
    """Run automation cycle once"""
    if AUTOMATION_LOCK.locked():
        logger.warning("⚠️ Automation already running, skipping this run")
        return

    with AUTOMATION_LOCK:
        try:
            logger.info("🚀 Starting automation cycle...")
            app.config['LAST_RUN'] = datetime.now().isoformat()
            
            # Import here to avoid circular imports
            # Use render-optimized version
            import sys
            if 'faceless_automation_render' not in sys.modules:
                logger.info("📦 Using Render-optimized pipeline")
            
            from master_automation import MasterOrchestrator
            
            orchestrator = MasterOrchestrator()
            results = orchestrator.run_daily_automation()
            
            app.config['VIDEOS_COUNT'] = app.config.get('VIDEOS_COUNT', 0) + 1
            
            # Cloudinary upload is handled within master_automation.py
            if results.get('cloudinary_url'):
                logger.info(f"✅ Video available at: {results['cloudinary_url']}")
            
            if results.get('status') == 'success':
                 logger.info("✅ Automation cycle completed successfully")
            else:
                 logger.warning("⚠️ Automation cycle completed with warnings")
            
            logger.info("✅ Automation cycle complete")
            
        except Exception as e:
            logger.error(f"❌ Automation cycle failed: {e}")

def self_ping():
    """Ping self every 10 minutes to stay awake"""
    base_url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:5000')
    
    logger.info(f"💓 Self-ping started: {base_url}")
    
    while True:
        try:
            time.sleep(600)  # Wait 10 minutes
            response = requests.get(f"{base_url}/health", timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Self-ping at {datetime.now().strftime('%H:%M:%S')}")
            else:
                logger.warning(f"⚠️ Self-ping returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Self-ping failed: {e}")
def start_scheduled_automation():
    """Start automation scheduler"""
    import schedule
    
    logger.info("⏰ Starting automation scheduler...")
    
    # Schedule daily runs (UTC times)
    schedule.every().day.at("09:00").do(run_automation_once)
    schedule.every().day.at("14:00").do(run_automation_once)
    schedule.every().day.at("19:00").do(run_automation_once)
    
    logger.info("✅ Scheduled: 9 AM, 2 PM, 7 PM UTC daily")
    
    # NEW: Check if we should run immediately (within 30 min of scheduled time)
    from datetime import datetime
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    current_minute = now.minute
    
    scheduled_hours = [9, 14, 19]
    for hour in scheduled_hours:
        if current_hour == hour and current_minute < 30:
            logger.info(f"🚀 Running missed {hour}:00 schedule...")
            threading.Thread(target=run_automation_once, daemon=True).start()
            break
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# ==================== STARTUP ====================

def initialize_app():
    """Initialize application on startup"""
    logger.info("\n" + "="*60)
    logger.info("🚀 FACELESS AUTOMATION SERVER STARTING")
    logger.info("="*60)
    
    # Check environment variables
    logger.info("\n🔍 Checking environment...")
    
    required_vars = ['YOUTUBE_API_KEY', 'PIXABAY_API_KEY', 'GEMINI_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        logger.warning(f"⚠️ Missing required vars: {', '.join(missing)}")
    else:
        logger.info("✅ All required environment variables set")
    
    # Check optional vars
    optional_vars = {
        'CLOUDINARY_CLOUD_NAME': 'Cloudinary',
        'ANTHROPIC_API_KEY': 'Claude',
        'OPENAI_API_KEY': 'GPT',
        'AUTOMATION_TOKEN': 'Security Token'
    }
    
    for var, name in optional_vars.items():
        if os.getenv(var):
            logger.info(f"✅ {name} configured")
        else:
            logger.warning(f"⚠️ {name} not configured (optional)")
    
    # Start background threads
    logger.info("\n🔧 Starting background services...")
    
    # 1. Self-ping to stay awake
    ping_thread = threading.Thread(target=self_ping, daemon=True)
    ping_thread.start()
    logger.info("✅ Self-ping thread started")
    
    # 2. Scheduled automation
    automation_thread = threading.Thread(target=start_scheduled_automation, daemon=True)
    automation_thread.start()
    logger.info("✅ Automation scheduler started")
    
    logger.info("\n" + "="*60)
    logger.info("🎉 SERVER READY - FULL STACK MODE!")
    logger.info("="*60 + "\n")

# ==================== MAIN ====================

if __name__ == '__main__':
    initialize_app()
    
    # Run Flask server
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"🌐 Starting Flask server on port {port}...")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
        )
