#!/usr/bin/env python3
"""
🏥 HEALTH SERVER - COMPLETE WORKING VERSION
"""

from flask import Flask, jsonify, request
import threading
import requests
import time
import os
import sys
from datetime import datetime
import logging
from dotenv import load_dotenv
import shutil

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['START_TIME'] = time.time()
app.config['VIDEOS_COUNT'] = 0
app.config['LAST_RUN'] = 'Never'
app.config['NEXT_RUN'] = 'Scheduled'

# ==================== ENDPOINTS ====================

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Faceless YouTube Automation',
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'message': '🚀 Automation is live!',
        'endpoints': {
            '/health': 'Health check',
            '/status': 'Detailed status',
            '/trigger': 'Manually trigger automation',
            '/stats': 'View statistics'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for keep-alive pings"""
    return jsonify({
        'status': 'alive',
        'timestamp': time.time(),
        'uptime_seconds': time.time() - app.config.get('START_TIME', time.time())
    })

@app.route('/status')
def status():
    """Detailed status information"""
    try:
        # Get disk usage
        total, used, free = shutil.disk_usage("/")
        
        return jsonify({
            'status': 'operational',
            'automation': 'running',
            'disk_usage': {
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'percent_used': round((used / total) * 100, 2)
            },
            'last_run': app.config.get('LAST_RUN', 'Never'),
            'next_run': app.config.get('NEXT_RUN', 'Unknown'),
            'videos_generated': app.config.get('VIDEOS_COUNT', 0),
            'uptime_hours': round((time.time() - app.config['START_TIME']) / 3600, 2),
            'environment': {
                'youtube_api': 'configured' if os.getenv('YOUTUBE_API_KEY') else 'not configured',
                'pixabay_api': 'configured' if os.getenv('PIXABAY_API_KEY') else 'not configured',
                'gemini_api': 'configured' if os.getenv('GEMINI_API_KEY') else 'not configured'
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
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
        return jsonify({'error': str(e)}), 500

# ==================== BACKGROUND TASKS ====================

def run_automation_once():
    """Run automation cycle once"""
    try:
        logger.info("🚀 Starting automation cycle...")
        app.config['LAST_RUN'] = datetime.now().isoformat()
        
        # Import here to avoid circular imports
        from master_automation import MasterOrchestrator
        
        orchestrator = MasterOrchestrator()
        results = orchestrator.run_daily_automation()
        
        app.config['VIDEOS_COUNT'] = app.config.get('VIDEOS_COUNT', 0) + 1
        
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
            response = requests.get(f"{base_url}/health", timeout=5)
            
            if response.status_code == 200:
                logger.info(f"✅ Self-ping successful at {datetime.now().strftime('%H:%M:%S')}")
            else:
                logger.warning(f"⚠️ Self-ping returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Self-ping failed: {e}")

def start_scheduled_automation():
    """Start automation scheduler"""
    import schedule
    
    logger.info("⏰ Starting automation scheduler...")
    
    # Schedule daily runs
    schedule.every().day.at("09:00").do(run_automation_once)
    schedule.every().day.at("14:00").do(run_automation_once)
    schedule.every().day.at("19:00").do(run_automation_once)
    
    logger.info("✅ Scheduled: 9 AM, 2 PM, 7 PM daily")
    
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
    required_vars = ['YOUTUBE_API_KEY', 'PIXABAY_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        logger.warning(f"⚠️ Missing env vars: {', '.join(missing)}")
    else:
        logger.info("✅ All required environment variables set")
    
    # Start background threads
    
    # 1. Self-ping to stay awake
    ping_thread = threading.Thread(target=self_ping, daemon=True)
    ping_thread.start()
    logger.info("✅ Self-ping thread started")
    
    # 2. Scheduled automation
    automation_thread = threading.Thread(target=start_scheduled_automation, daemon=True)
    automation_thread.start()
    logger.info("✅ Automation scheduler started")
    
    logger.info("\n" + "="*60)
    logger.info("🎉 SERVER READY!")
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
