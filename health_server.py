#!/usr/bin/env python3
"""
Keep-alive HTTP server for Render free tier
"""

from flask import Flask, jsonify
import threading
import requests
import time
import os

app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'alive',
        'timestamp': time.time()
    })

@app.route('/')
def home():
    """Root endpoint"""
    return "Faceless Automation Running! 🚀"

def self_ping():
    """Ping self every 10 minutes to stay awake"""
    url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:5000')
    while True:
        try:
            time.sleep(600)  # Wait 10 minutes
            requests.get(f"{url}/health", timeout=5)
            print(f"✅ Self-ping at {time.ctime()}")
        except Exception as e:
            print(f"⚠️ Ping failed: {e}")

def start_automation():
    """Start your main automation in background"""
    from master_automation import MasterOrchestrator
    orchestrator = MasterOrchestrator()
    orchestrator.setup_scheduler()

if __name__ == '__main__':
    # Start self-ping in background
    ping_thread = threading.Thread(target=self_ping, daemon=True)
    ping_thread.start()
    
    # Start automation in background
    automation_thread = threading.Thread(target=start_automation, daemon=True)
    automation_thread.start()
    
    # Run Flask server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
