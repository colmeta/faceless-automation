#!/usr/bin/env python3
"""
🚀 AI SHORTS AUTOPILOT - COMPLETE AUTOMATION WITH MULTI-LLM ANALYSIS
Finds viral AI videos → Analyzes with Gemini/Claude/GPT → Generates shorts → Posts at optimal times
Usage: python3 autopilot.py
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import google.generativeai as genai

# Optional: Import other LLMs if keys available
try:
    import anthropic
except ImportError:
    anthropic = None

try:
    from groq import Groq
except ImportError:
    Groq = None
    
try:
    import openai
except ImportError:
    openai = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autopilot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# ==================== CONFIG ====================
class Config:
    # API Keys
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Affiliate Links (Update with YOUR links)
    AFFILIATES = {
        'CustomGPT': 'https://customgpt.ai/aff/YOUR_ID',
        'Copy.ai': 'https://copy.ai/aff/YOUR_ID',
        'Jasper': 'https://jasper.ai/aff/YOUR_ID',
        'Anyword': 'https://anyword.com/aff/YOUR_ID',
        'GetResponse': 'https://getresponse.com/aff/YOUR_ID',
    }
    
    # Posting Times (Optimal for USA/Europe)
    POSTING_SCHEDULE = {
        'Tuesday': '17:00',    # 5 PM EST (USA Peak)
        'Wednesday': '13:00',  # 1 PM CET (Europe)
        'Thursday': '19:00',   # 7 PM EST (USA Evening)
        'Friday': '15:00'      # 3 PM CET (Europe)
    }
    
    # Content preferences
    AI_TOOLS = ['ChatGPT', 'Claude', 'Gemini', 'Midjourney', 'Runway', 'HeyGen', 'Pika', 'CustomGPT']
    CONTENT_TYPES = ['Tutorial', 'Comparison', 'Hack', 'News', 'Review', 'Workflow']
    
    @staticmethod
    def check_env_vars():
        """Verify essential environment variables"""
        missing = []
        if not Config.YOUTUBE_API_KEY:
            missing.append("YOUTUBE_API_KEY")
        if not Config.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")

        if not Config.GROQ_API_KEY:
    logger.warning("⚠️ GROQ_API_KEY missing - Groq analysis disabled")
    
        if missing:
            logger.error(f"❌ Missing critical env vars: {', '.join(missing)}")
            return False
        
        if not Config.CLAUDE_API_KEY:
            logger.warning("⚠️ ANTHROPIC_API_KEY missing - Claude analysis disabled")
        if not Config.OPENAI_API_KEY:
            logger.warning("⚠️ OPENAI_API_KEY missing - GPT analysis disabled")
        
        return True

# ==================== PHASE 1: TRANSCRIPT EXTRACTOR ====================
class TranscriptExtractor:
    """Extracts and caches transcripts from YouTube videos"""
    
    def __init__(self):
        self.transcript_cache = {}
    
    def get_transcript(self, video_id: str) -> Optional[str]:
        """Fetch YouTube transcript"""
        if video_id in self.transcript_cache:
            logger.info(f"📋 Transcript found in cache for {video_id}")
            return self.transcript_cache[video_id]
        
        try:
            logger.info(f"🔍 Fetching transcript for {video_id}...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en', 'a.en']).fetch()
            
            full_transcript = " ".join([item['text'] for item in transcript])
            self.transcript_cache[video_id] = full_transcript
            
            logger.info(f"✅ Transcript retrieved: {len(full_transcript)} characters")
            return full_transcript
        
        except TranscriptsDisabled:
            logger.error(f"❌ Transcripts disabled for {video_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Transcript error: {e}")
            return None

# ==================== PHASE 2: MULTI-LLM ANALYZER ====================
class MultiLLMAnalyzer:
    """Analyzes transcripts using multiple LLM models"""
    
    def __init__(self):
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)

        self.groq_client = None
        if Config.GROQ_API_KEY and Groq:
            self.groq_client = Groq(api_key=Config.GROQ_API_KEY)

        self.claude_client = None
        if Config.CLAUDE_API_KEY and anthropic:
            self.claude_client = anthropic.Anthropic(api_key=Config.CLAUDE_API_KEY)
        
        self.openai_client = None
        if Config.OPENAI_API_KEY and openai:
            self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def get_analysis_prompt(self):
        """Returns consistent analysis prompt for all models"""
        return """Analyze this YouTube transcript and provide a JSON response with these exact fields:
{
    "summary": "Single paragraph executive summary of video content",
    "key_topics": "Comma-separated list of 5-7 key topics/keywords",
    "affiliate_angle": "Best affiliate product category for this content",
    "content_type": "Choose from: Tutorial, Comparison, Review, News, Hack, Workflow",
    "best_clips": "3 specific timestamps (format: 0:00-0:30) that would make great shorts",
    "short_hook": "Attention-grabbing 10-word hook for YouTube Short",
    "cta": "Clear call-to-action for affiliate link"
}

IMPORTANT: Return ONLY valid JSON, no markdown or extra text."""
    
    def analyze_with_gemini(self, transcript: str) -> Dict:
        """Analyze with Google Gemini"""
        if not Config.GEMINI_API_KEY:
            return {"error": "Gemini API key missing"}
        
        try:
            logger.info("🔵 Analyzing with Gemini...")
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            response = model.generate_content(
                f"{self.get_analysis_prompt()}\n\nTranscript:\n{transcript[:8000]}"
            )
            
            # Parse JSON from response
            text = response.text
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['model'] = 'Gemini'
                logger.info("✅ Gemini analysis complete")
                return result
            
            return {"error": "Failed to parse Gemini response", "raw": text, "model": "Gemini"}
        
        except Exception as e:
            logger.error(f"❌ Gemini error: {e}")
            return {"error": str(e), "model": "Gemini"}
    
    def analyze_with_claude(self, transcript: str) -> Dict:
        """Analyze with Anthropic Claude"""
        if not self.claude_client:
            return {"error": "Claude client not configured", "model": "Claude"}

        def analyze_with_groq(self, transcript: str) -> Dict:
    """Analyze with Groq (fast + free)"""
    if not self.groq_client:
        return {"error": "Groq client not configured", "model": "Groq"}
    
    try:
        logger.info("⚡ Analyzing with Groq...")
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"{self.get_analysis_prompt()}\n\nTranscript:\n{transcript[:8000]}"
                }
            ]
        )
        
        text = response.choices[0].message.content
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            result['model'] = 'Groq'
            logger.info("✅ Groq analysis complete")
            return result
        
        return {"error": "Failed to parse Groq response", "raw": text, "model": "Groq"}
    
    except Exception as e:
        logger.error(f"❌ Groq error: {e}")
        return {"error": str(e), "model": "Groq"}

        
        try:
            logger.info("🟣 Analyzing with Claude...")
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"{self.get_analysis_prompt()}\n\nTranscript:\n{transcript[:8000]}"
                    }
                ]
            )
            
            text = message.content[0].text
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['model'] = 'Claude'
                logger.info("✅ Claude analysis complete")
                return result
            
            return {"error": "Failed to parse Claude response", "raw": text, "model": "Claude"}
        
        except Exception as e:
            logger.error(f"❌ Claude error: {e}")
            return {"error": str(e), "model": "Claude"}
    
    def analyze_with_gpt(self, transcript: str) -> Dict:
        """Analyze with OpenAI GPT"""
        if not self.openai_client:
            return {"error": "GPT client not configured", "model": "GPT"}
        
        try:
            logger.info("🟢 Analyzing with GPT...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"{self.get_analysis_prompt()}\n\nTranscript:\n{transcript[:8000]}"
                    }
                ]
            )
            
            text = response.choices[0].message.content
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result['model'] = 'GPT'
                logger.info("✅ GPT analysis complete")
                return result
            
            return {"error": "Failed to parse GPT response", "raw": text, "model": "GPT"}
        
        except Exception as e:
            logger.error(f"❌ GPT error: {e}")
            return {"error": str(e), "model": "GPT"}
    
    def get_best_analysis(self, transcript: str) -> Dict:
        """Run analysis with available models and pick best result"""
        analyses = []
        
        # Try Gemini first (usually fastest and free tier available)
        gemini_result = self.analyze_with_gemini(transcript)
        if "error" not in gemini_result:
            analyses.append(gemini_result)

        # Try Groq
        groq_result = self.analyze_with_groq(transcript)
        if "error" not in groq_result:
            analyses.append(groq_result)

        # Try Claude
        claude_result = self.analyze_with_claude(transcript)
        if "error" not in claude_result:
            analyses.append(claude_result)
        
        # Try GPT
        gpt_result = self.analyze_with_gpt(transcript)
        if "error" not in gpt_result:
            analyses.append(gpt_result)
        
        if not analyses:
            logger.error("❌ All LLM analyses failed")
            return {"error": "All models failed"}
        
        # Return Gemini if available, otherwise first successful
        for analysis in analyses:
            if analysis.get('model') == 'Gemini':
                logger.info("🏆 Using Gemini analysis")
                return analysis
        
        logger.info(f"🏆 Using {analyses[0]['model']} analysis")
        return analyses[0]

# ==================== PHASE 3: VIRAL VIDEO HUNTER ====================
class ViralVideoHunter:
    """Finds trending AI videos"""
    
    def __init__(self):
        from googleapiclient.discovery import build
        self.youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)
        self.extractor = TranscriptExtractor()
        self.analyzer = MultiLLMAnalyzer()
    
    def search_trending_ai_videos(self) -> List[Dict]:
        """Search YouTube for trending AI videos"""
        try:
            logger.info("🔎 Searching for trending AI videos...")
            
            query = 'AI tools tutorial -crypto -NFT'
            request = self.youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=50,
                order='viewCount',
                publishedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z',
                regionCode='US'
            )
            
            response = request.execute()
            videos = []
            
            for item in response['items'][:10]:
                video_id = item['id']['videoId']
                video_data = self.get_video_stats(video_id)
                
                if video_data and video_data['views'] > 100000:
                    # Get transcript and analyze
                    transcript = self.extractor.get_transcript(video_id)
                    if transcript:
                        analysis = self.analyzer.get_best_analysis(transcript)
                        video_data['analysis'] = analysis
                    videos.append(video_data)
            
            logger.info(f"✅ Found {len(videos)} trending videos with analysis")
            return videos[:5]  # Return top 5
        
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return []
    
    def get_video_stats(self, video_id: str) -> Optional[Dict]:
        """Get video statistics"""
        try:
            request = self.youtube.videos().list(
                id=video_id,
                part='snippet,statistics,contentDetails'
            )
            response = request.execute()
            
            if not response['items']:
                return None
            
            item = response['items'][0]
            stats = item['statistics']
            snippet = item['snippet']
            
            engagement = (int(stats.get('likeCount', 0)) + int(stats.get('commentCount', 0))) / max(int(stats.get('viewCount', 1)), 1)
            
            return {
                'video_id': video_id,
                'title': snippet['title'],
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'engagement_rate': round(engagement * 100, 2),
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'description': snippet['description'][:200]
            }
        
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            return None

# ==================== PHASE 4: SHORT GENERATOR ====================
class ShortScriptGenerator:
    """Generates short scripts based on analysis"""
    
    def generate_script(self, analysis: Dict, affiliate_tool: str) -> Dict:
        """Generate short script from analysis"""
        try:
            logger.info(f"✍️ Generating script for {affiliate_tool}...")
            
            script = {
                'title': analysis.get('short_hook', 'Check out this AI tool'),
                'hook': analysis.get('short_hook', 'You won\'t believe this'),
                'best_clips': analysis.get('best_clips', '0:00-0:30'),
                'affiliate_tool': affiliate_tool,
                'affiliate_url': Config.AFFILIATES.get(affiliate_tool),
                'cta': analysis.get('cta', f'Try {affiliate_tool} now'),
                'key_topics': analysis.get('key_topics', ''),
                'content_type': analysis.get('content_type', 'Tutorial')
            }
            
            logger.info("✅ Script generated")
            return script
        
        except Exception as e:
            logger.error(f"❌ Script generation error: {e}")
            return {}
    
    def generate_description(self, script: Dict, video_title: str) -> str:
        """Generate YouTube description with affiliates"""
        return f"""
{script.get('title', video_title)}

🔗 AFFILIATE LINK:
{script.get('affiliate_url', 'https://example.com')}

📊 Tools Mentioned:
→ {script.get('affiliate_tool', 'AI Tool')}

⏰ Best Clips:
{script.get('best_clips', '0:00-1:00')}

🎯 KEY TOPICS:
{script.get('key_topics', 'AI, Tools, Automation')}

💡 Call to Action:
{script.get('cta', 'Try it now')}

---
I earn a small commission (at no cost to you) which helps me make more videos. Thanks for supporting! 💙

#AI #Shorts #{script.get('affiliate_tool', 'Tool').replace(' ', '')}
"""

# ==================== PHASE 5: SCHEDULER ====================
class SmartScheduler:
    """Schedules posts at optimal times"""
    
    def __init__(self):
        self.queue = []
    
    def get_next_post_time(self) -> datetime:
        """Calculate next optimal posting time"""
        now = datetime.now()
        
        for day_name, time_str in Config.POSTING_SCHEDULE.items():
            hour, minute = map(int, time_str.split(':'))
            days = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                    'Friday': 4, 'Saturday': 5, 'Sunday': 6}
            target = days.get(day_name, 1)
            current = now.weekday()
            days_ahead = (target - current) % 7
            
            if days_ahead == 0:
                days_ahead = 7
            
            post_time = now + timedelta(days=days_ahead)
            post_time = post_time.replace(hour=hour, minute=minute, second=0)
            
            if post_time > now:
                return post_time
        
        return now + timedelta(days=1, hours=17)
    
    def queue_post(self, content: Dict, post_time: datetime):
        """Queue a post"""
        self.queue.append({
            'content': content,
            'scheduled_time': post_time,
            'status': 'pending'
        })
        logger.info(f"📅 Post queued for {post_time}")

# ==================== ANALYTICS ====================
class AnalyticsTracker:
    """Tracks performance metrics"""
    
    def __init__(self):
        self.stats_file = 'affiliate_stats.json'
        self.load_stats()
    
    def load_stats(self):
        """Load stats"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {'total_posts': 0, 'affiliates': {}}
    
    def save_stats(self):
        """Save stats"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def log_post(self, title: str, affiliate: str):
        """Log post"""
        self.stats['total_posts'] += 1
        if affiliate not in self.stats['affiliates']:
            self.stats['affiliates'][affiliate] = {'posts': 0}
        self.stats['affiliates'][affiliate]['posts'] += 1
        self.save_stats()
        logger.info(f"📊 Logged: {title}")
    
    def print_stats(self):
        """Print stats"""
        logger.info("=" * 60)
        logger.info("📊 AUTOPILOT PERFORMANCE")
        logger.info("=" * 60)
        logger.info(f"Total Posts: {self.stats['total_posts']}")
        for aff, data in self.stats['affiliates'].items():
            logger.info(f"  {aff}: {data['posts']} posts")

# ==================== MAIN ORCHESTRATOR ====================
class AutopilotOrchestrator:
    """Orchestrates full pipeline"""
    
    def __init__(self):
        if not Config.check_env_vars():
            raise Exception("Missing critical environment variables")
        
        self.hunter = ViralVideoHunter()
        self.generator = ShortScriptGenerator()
        self.scheduler = SmartScheduler()
        self.analytics = AnalyticsTracker()
    
    def run_full_pipeline(self):
        """Execute full pipeline"""
        try:
            logger.info("\n" + "="*60)
            logger.info("🚀 AUTOPILOT PIPELINE STARTING")
            logger.info("="*60)
            
            # Phase 1: Hunt
            logger.info("\n📌 PHASE 1: Hunting Viral Videos...")
            videos = self.hunter.search_trending_ai_videos()
            
            if not videos:
                logger.warning("⚠️ No videos found")
                return
            
            # Phase 2: Generate
            logger.info("\n📌 PHASE 2: Generating Scripts...")
            best_video = videos[0]
            analysis = best_video.get('analysis', {})
            
            if 'error' in analysis:
                logger.error(f"Analysis failed: {analysis['error']}")
                return
            
            tool = random.choice(Config.AI_TOOLS)
            script = self.generator.generate_script(analysis, tool)
            description = self.generator.generate_description(script, best_video['title'])
            
            # Phase 3: Schedule
            logger.info("\n📌 PHASE 3: Scheduling Post...")
            post_time = self.scheduler.get_next_post_time()
            
            content = {
                'title': script.get('title', best_video['title']),
                'script': script,
                'description': description,
                'source_video': best_video['url'],
                'affiliate_tool': tool,
                'video_stats': best_video
            }
            
            self.scheduler.queue_post(content, post_time)
            self.analytics.log_post(script.get('title', 'Untitled'), tool)
            
            logger.info("\n✅ PIPELINE COMPLETE")
            logger.info(f"📅 Next post: {post_time}")
            self.analytics.print_stats()
        
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")

# ==================== MAIN ====================
def main():
    """Entry point"""
    try:
        orchestrator = AutopilotOrchestrator()
        
        # Single run
        orchestrator.run_full_pipeline()
        
        # Optional: Uncomment for continuous mode
        # schedule.every(6).hours.do(orchestrator.run_full_pipeline)
        # while True:
        #     schedule.run_pending()
        #     time.sleep(60)
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
