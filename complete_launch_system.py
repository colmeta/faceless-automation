#!/usr/bin/env python3
"""
🚀 COMPLETE FACELESS LAUNCH SYSTEM
Everything you need to launch TODAY - Scripts, Hashtags, Analytics, Thumbnails, Competitor Analysis
""" 

import os
import json
import random
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 1. VIRAL SCRIPT GENERATOR ====================
class ViralScriptGenerator:
    """30+ proven viral hooks and script templates"""
    
    VIRAL_HOOKS = {
        'shock': [
            "I tested AI for 30 days and this happened",
            "This AI tool replaced my entire team",
            "Nobody talks about this AI feature",
            "I made $10K with this free AI tool",
            "This AI does what ChatGPT can't",
            "Stop using ChatGPT. Use this instead",
            "I found ChatGPT's secret weapon"
        ],
        'curiosity': [
            "The AI tool billionaires use secretly",
            "Why everyone's switching to this AI",
            "This AI feature is hidden for a reason",
            "What happens when you combine these AI tools",
            "The AI hack nobody's talking about"
        ],
        'urgency': [
            "This AI deal ends in 24 hours",
            "Before ChatGPT removes this feature",
            "This AI is free but not for long",
            "Get this AI tool before they charge"
        ],
        'comparison': [
            "ChatGPT vs This AI - I'm shocked",
            "I tested 10 AI tools. This won",
            "Free AI vs $100 AI - surprising results",
            "Google Gemini can't do this"
        ],
        'tutorial': [
            "How I automate everything with AI",
            "My AI workflow that saves 10 hours",
            "The AI prompt that changed my life",
            "Copy this AI prompt right now"
        ],
        'problem_solution': [
            "Tired of ChatGPT's limits? Try this",
            "ChatGPT keeps lying? Use this instead",
            "Can't afford AI tools? Watch this",
            "This AI fixes ChatGPT's biggest problem"
        ]
    }
    
    SCRIPT_TEMPLATES = {
        'tutorial': """
Hook: {hook}

Problem: You're wasting hours on {problem}

Solution: {tool_name} automates this in seconds

Demo: Watch me {demo_action}

Results: I went from {before} to {after}

CTA: {cta}
""",
        'comparison': """
Hook: {hook}

Setup: I tested {tool_a} vs {tool_b}

Test: Same task, same prompts

Results: {tool_b} was {percentage}% better

Proof: Here's the side-by-side

CTA: {cta}
""",
        'hack': """
Hook: {hook}

The Hack: Use {tool_name} + {secret_feature}

Why it works: {explanation}

Demo: Watch this transformation

Results: {metric} improvement

CTA: {cta}
"""
    }
    
    AI_TOOLS_DATABASE = {
        'CustomGPT': {
            'use_cases': ['chatbots', 'customer support', 'lead generation'],
            'affiliate': 'https://customgpt.ai/aff/YOUR_ID',
            'pain_points': ['expensive devs', 'slow support', 'no automation']
        },
        'Copy.ai': {
            'use_cases': ['copywriting', 'ads', 'social media'],
            'affiliate': 'https://copy.ai/aff/YOUR_ID',
            'pain_points': ['writer\'s block', 'slow content', 'bad copy']
        },
        'Jasper': {
            'use_cases': ['blog posts', 'marketing', 'SEO'],
            'affiliate': 'https://jasper.ai/aff/YOUR_ID',
            'pain_points': ['SEO struggles', 'content ideas', 'consistency']
        },
        'Midjourney': {
            'use_cases': ['design', 'mockups', 'branding'],
            'affiliate': 'https://midjourney.com',
            'pain_points': ['expensive designers', 'slow revisions', 'bad vision']
        },
        'HeyGen': {
            'use_cases': ['video avatars', 'training videos', 'ads'],
            'affiliate': 'https://heygen.com/aff/YOUR_ID',
            'pain_points': ['camera shy', 'editing time', 'video costs']
        }
    }
    
    def generate_script(self, tool_name: str = None, hook_type: str = 'shock') -> Dict:
        """Generate complete viral script"""
        if not tool_name:
            tool_name = random.choice(list(self.AI_TOOLS_DATABASE.keys()))
        
        tool_data = self.AI_TOOLS_DATABASE[tool_name]
        hook = random.choice(self.VIRAL_HOOKS[hook_type])
        
        script = {
            'hook': hook.replace('AI tool', tool_name),
            'tool': tool_name,
            'use_case': random.choice(tool_data['use_cases']),
            'pain_point': random.choice(tool_data['pain_points']),
            'affiliate_link': tool_data['affiliate'],
            'cta': f"Try {tool_name} free - Link in bio",
            'full_script': self._build_full_script(hook, tool_name, tool_data),
            'duration': '45-60 seconds',
            'topic_tags': tool_data['use_cases']
        }
        
        return script
    
    def _build_full_script(self, hook: str, tool: str, data: Dict) -> str:
        """Build complete narration script"""
        return f"""{hook}

I was struggling with {random.choice(data['pain_points'])} until I found {tool}.

Here's what changed: This tool handles {random.choice(data['use_cases'])} automatically.

The best part? You can try it completely free.

Results? I'm saving 10+ hours every week.

Link in bio to try {tool} yourself. You won't regret it."""
    
    def generate_batch(self, count: int = 30) -> List[Dict]:
        """Generate 30 days of scripts"""
        scripts = []
        tools = list(self.AI_TOOLS_DATABASE.keys())
        hook_types = list(self.VIRAL_HOOKS.keys())
        
        for i in range(count):
            tool = tools[i % len(tools)]
            hook_type = hook_types[i % len(hook_types)]
            scripts.append(self.generate_script(tool, hook_type))
        
        return scripts

# ==================== 2. HASHTAG STRATEGY ENGINE ====================
class HashtagStrategy:
    """Research-based hashtag optimization"""
    
    HASHTAG_DATABASE = {
        'mega': {  # 10M+ posts
            'youtube': ['#Shorts', '#AI', '#Tech', '#Viral', '#Tutorial'],
            'tiktok': ['#fyp', '#foryou', '#viral', '#ai', '#tech'],
            'instagram': ['#reels', '#ai', '#technology', '#viral', '#explore']
        },
        'large': {  # 1M-10M posts
            'youtube': ['#AITools', '#ChatGPT', '#Automation', '#NoCode', '#Productivity'],
            'tiktok': ['#aitools', '#chatgpt', '#techtok', '#productivity', '#automation'],
            'instagram': ['#aitools', '#chatgpt', '#productivityhacks', '#techreels', '#automation']
        },
        'medium': {  # 100K-1M posts
            'youtube': ['#AIHacks', '#TechTips', '#AITutorial', '#DigitalMarketing', '#OnlineBusiness'],
            'tiktok': ['#aihacks', '#techtips', '#aitutorial', '#sidehustle', '#digitalmarketing'],
            'instagram': ['#aihacks', '#techtips', '#aitutorial', '#sidehustleideas', '#onlinebiz']
        },
        'niche': {  # 10K-100K posts
            'youtube': ['#CustomGPT', '#AIWorkflow', '#NoCodeAI', '#AIForBusiness', '#AutomateEverything'],
            'tiktok': ['#customgpt', '#aiworkflow', '#nocodeai', '#aiforbusiness', '#aiautomation'],
            'instagram': ['#customgpt', '#aiworkflow', '#nocodetools', '#aiforbusiness', '#aiautomation']
        }
    }
    
    TRENDING_TOPICS = {
        'ai_tools': ['chatgpt', 'gemini', 'claude', 'midjourney', 'runway'],
        'use_cases': ['automation', 'productivity', 'sidehustle', 'business', 'marketing'],
        'outcomes': ['timesaver', 'moneymaker', 'gamechanger', 'efficient', 'smart']
    }
    
    def generate_hashtags(self, platform: str, tool_name: str = None) -> List[str]:
        """Generate optimized hashtag mix"""
        hashtags = []
        
        # 2 mega (reach)
        hashtags.extend(random.sample(self.HASHTAG_DATABASE['mega'][platform], 2))
        
        # 2 large (visibility)
        hashtags.extend(random.sample(self.HASHTAG_DATABASE['large'][platform], 2))
        
        # 2 medium (engagement)
        hashtags.extend(random.sample(self.HASHTAG_DATABASE['medium'][platform], 2))
        
        # 2 niche (conversion)
        hashtags.extend(random.sample(self.HASHTAG_DATABASE['niche'][platform], 2))
        
        # Add tool-specific if provided
        if tool_name:
            hashtags.append(f'#{tool_name.replace(" ", "").lower()}')
        
        return hashtags[:10]  # Max 10 for best performance
    
    def get_caption_template(self, platform: str, script: Dict) -> str:
        """Generate optimized caption"""
        hashtags = ' '.join(self.generate_hashtags(platform, script['tool']))
        
        if platform == 'youtube':
            return f"""{script['hook']} 

{script['cta']}

{hashtags}"""
        
        elif platform == 'tiktok':
            return f"""{script['hook']} 🔥

Drop a 💯 if you're trying this!

{hashtags}"""
        
        else:  # Instagram
            return f"""{script['hook']} ✨

Double tap if this helps! 💙
Save for later 📌

{hashtags}

—
Follow @YourHandle for daily AI tips"""
    
    def analyze_performance(self, hashtags: List[str], views: int) -> Dict:
        """Track which hashtags perform best"""
        return {
            'hashtags': hashtags,
            'views': views,
            'avg_views_per_tag': views / len(hashtags),
            'recommendation': 'Keep using' if views > 10000 else 'Test alternatives'
        }

# ==================== 3. ANALYTICS TRACKER ====================
class AnalyticsTracker:
    """Monitor performance and optimize"""
    
    def __init__(self):
        self.db_file = 'analytics.json'
        self.load_data()
    
    def load_data(self):
        """Load analytics data"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'videos': [],
                'total_views': 0,
                'total_videos': 0,
                'best_performing': [],
                'platform_stats': {'youtube': {}, 'tiktok': {}, 'instagram': {}}
            }
    
    def save_data(self):
        """Save analytics data"""
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def track_video(self, video_data: Dict):
        """Track new video"""
        video_data['timestamp'] = datetime.now().isoformat()
        video_data['id'] = f"vid_{len(self.data['videos']) + 1}"
        
        self.data['videos'].append(video_data)
        self.data['total_videos'] += 1
        
        self.save_data()
        logger.info(f"✅ Tracked: {video_data['title']}")
    
    def update_stats(self, video_id: str, platform: str, views: int, likes: int, comments: int):
        """Update video stats"""
        for video in self.data['videos']:
            if video['id'] == video_id:
                video[platform] = {
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'engagement_rate': ((likes + comments) / max(views, 1)) * 100,
                    'updated': datetime.now().isoformat()
                }
                
                self.data['total_views'] += views
                break
        
        self.save_data()
    
    def get_best_performers(self, top_n: int = 10) -> List[Dict]:
        """Get top performing videos"""
        ranked = sorted(
            self.data['videos'],
            key=lambda x: sum([x.get(p, {}).get('views', 0) for p in ['youtube', 'tiktok', 'instagram']]),
            reverse=True
        )
        return ranked[:top_n]
    
    def get_optimization_insights(self) -> Dict:
        """Get actionable insights"""
        if not self.data['videos']:
            return {'message': 'No data yet. Upload more videos!'}
        
        # Analyze patterns
        best = self.get_best_performers(5)
        
        # Extract patterns
        common_hooks = {}
        common_tools = {}
        
        for video in best:
            hook_type = video.get('hook_type', 'unknown')
            tool = video.get('tool', 'unknown')
            
            common_hooks[hook_type] = common_hooks.get(hook_type, 0) + 1
            common_tools[tool] = common_tools.get(tool, 0) + 1
        
        return {
            'best_hook_types': sorted(common_hooks.items(), key=lambda x: x[1], reverse=True),
            'best_tools': sorted(common_tools.items(), key=lambda x: x[1], reverse=True),
            'avg_views': self.data['total_views'] / max(self.data['total_videos'], 1),
            'recommendation': 'Focus on ' + max(common_hooks, key=common_hooks.get) + ' hooks'
        }
    
    def print_dashboard(self):
        """Print analytics dashboard"""
        print("\n" + "="*60)
        print("📊 ANALYTICS DASHBOARD")
        print("="*60)
        print(f"Total Videos: {self.data['total_videos']}")
        print(f"Total Views: {self.data['total_views']:,}")
        print(f"Avg Views/Video: {self.data['total_views'] / max(self.data['total_videos'], 1):.0f}")
        
        print("\n🏆 TOP 5 PERFORMERS:")
        for i, video in enumerate(self.get_best_performers(5), 1):
            total_views = sum([video.get(p, {}).get('views', 0) for p in ['youtube', 'tiktok', 'instagram']])
            print(f"{i}. {video['title'][:50]} - {total_views:,} views")
        
        insights = self.get_optimization_insights()
        if 'recommendation' in insights:
            print(f"\n💡 INSIGHT: {insights['recommendation']}")
        
        print("="*60 + "\n")

# ==================== 4. THUMBNAIL GENERATOR ====================
class ThumbnailGenerator:
    """Auto-generate eye-catching thumbnails"""
    
    COLOR_SCHEMES = {
        'tech': [(255, 0, 110), (0, 170, 255), (255, 215, 0)],  # Hot pink, blue, gold
        'business': [(0, 123, 255), (40, 167, 69), (255, 193, 7)],  # Blue, green, yellow
        'shocking': [(255, 0, 0), (255, 255, 0), (0, 0, 0)]  # Red, yellow, black
    }
    
    EMOJI_FACES = {
        'shock': '😱',
        'excited': '🤯',
        'money': '💰',
        'fire': '🔥',
        'thinking': '🤔',
        'point': '👉'
    }
    
    def generate_thumbnail(self, script: Dict, output_path: str, theme: str = 'tech') -> str:
        """Generate viral thumbnail"""
        try:
            # Create base image
            img = Image.new('RGB', (1920, 1080), color=self.COLOR_SCHEMES[theme][0])
            draw = ImageDraw.Draw(img)
            
            # Add gradient effect
            for y in range(1080):
                color_ratio = y / 1080
                color = tuple([
                    int(self.COLOR_SCHEMES[theme][0][i] * (1 - color_ratio) + 
                        self.COLOR_SCHEMES[theme][1][i] * color_ratio)
                    for i in range(3)
                ])
                draw.rectangle([(0, y), (1920, y+1)], fill=color)
            
            # Add text
            try:
                # Try to use Arial Bold
                title_font = ImageFont.truetype("Arial-Bold.ttf", 120)
                subtitle_font = ImageFont.truetype("Arial-Bold.ttf", 80)
            except:
                # Fallback to default
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            # Main text (hook)
            hook_text = script['hook'].upper()
            words = hook_text.split()
            
            # Multi-line text
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 20:
                    lines.append(' '.join(current_line))
                    current_line = []
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw text with outline
            y_offset = 300
            for line in lines[:3]:  # Max 3 lines
                # Get text size
                bbox = draw.textbbox((0, 0), line, font=title_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (1920 - text_width) // 2
                
                # Draw outline
                for adj in range(-5, 6, 2):
                    for adj_y in range(-5, 6, 2):
                        draw.text((x+adj, y_offset+adj_y), line, font=title_font, fill=(0, 0, 0))
                
                # Draw main text
                draw.text((x, y_offset), line, font=title_font, fill=(255, 255, 255))
                y_offset += 140
            
            # Add emoji/icon
            emoji = self.EMOJI_FACES.get('fire', '🔥')
            try:
                emoji_font = ImageFont.truetype("Segoe UI Emoji.ttf", 200)
                draw.text((1600, 100), emoji, font=emoji_font, fill=(255, 255, 255))
            except:
                pass  # Skip emoji if font not available
            
            # Add CTA bar at bottom
            draw.rectangle([(0, 900), (1920, 1080)], fill=(0, 0, 0))
            cta_text = script['cta'].upper()
            bbox = draw.textbbox((0, 0), cta_text, font=subtitle_font)
            text_width = bbox[2] - bbox[0]
            draw.text(((1920 - text_width) // 2, 950), cta_text, font=subtitle_font, fill=(255, 215, 0))
            
            # Save
            img.save(output_path, quality=95)
            logger.info(f"✅ Thumbnail created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Thumbnail generation failed: {e}")
            # Create simple fallback
            img = Image.new('RGB', (1920, 1080), color=(255, 0, 110))
            draw = ImageDraw.Draw(img)
            draw.text((960, 540), script['hook'][:30], fill=(255, 255, 255), anchor="mm")
            img.save(output_path)
            return output_path

# ==================== 5. COMPETITOR ANALYSIS ====================
class CompetitorSpy:
    """Analyze successful competitors"""
    
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    
    def find_top_channels(self, niche: str = 'AI tools') -> List[Dict]:
        """Find top performing channels in niche"""
        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            request = youtube.search().list(
                q=f'{niche} tutorial',
                part='snippet',
                type='channel',
                maxResults=10,
                order='viewCount'
            )
            
            response = request.execute()
            
            channels = []
            for item in response['items']:
                channel_id = item['snippet']['channelId']
                channel_data = self.analyze_channel(channel_id)
                if channel_data:
                    channels.append(channel_data)
            
            return sorted(channels, key=lambda x: x['subscribers'], reverse=True)
            
        except Exception as e:
            logger.error(f"Channel search failed: {e}")
            return []
    
    def analyze_channel(self, channel_id: str) -> Dict:
        """Analyze specific channel"""
        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            # Get channel stats
            request = youtube.channels().list(
                id=channel_id,
                part='snippet,statistics,contentDetails'
            )
            response = request.execute()
            
            if not response['items']:
                return None
            
            item = response['items'][0]
            stats = item['statistics']
            
            return {
                'channel_id': channel_id,
                'name': item['snippet']['title'],
                'subscribers': int(stats.get('subscriberCount', 0)),
                'total_views': int(stats.get('viewCount', 0)),
                'video_count': int(stats.get('videoCount', 0)),
                'avg_views_per_video': int(stats.get('viewCount', 0)) / max(int(stats.get('videoCount', 1)), 1)
            }
            
        except Exception as e:
            logger.error(f"Channel analysis failed: {e}")
            return None
    
    def analyze_viral_videos(self, channel_id: str) -> List[Dict]:
        """Get top performing videos from channel"""
        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            # Get uploads playlist
            channel_request = youtube.channels().list(
                id=channel_id,
                part='contentDetails'
            )
            channel_response = channel_request.execute()
            uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos
            videos_request = youtube.playlistItems().list(
                playlistId=uploads_id,
                part='snippet',
                maxResults=50
            )
            videos_response = videos_request.execute()
            
            viral_videos = []
            for item in videos_response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                video_stats = self.get_video_stats(video_id)
                if video_stats and video_stats['views'] > 100000:
                    viral_videos.append(video_stats)
            
            return sorted(viral_videos, key=lambda x: x['views'], reverse=True)[:10]
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return []
    
    def get_video_stats(self, video_id: str) -> Dict:
        """Get detailed video stats"""
        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            request = youtube.videos().list(
                id=video_id,
                part='snippet,statistics'
            )
            response = request.execute()
            
            if not response['items']:
                return None
            
            item = response['items'][0]
            return {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0)),
                'comments': int(item['statistics'].get('commentCount', 0)),
                'url': f'https://youtube.com/watch?v={video_id}'
            }
            
        except Exception as e:
            return None
    
    def extract_patterns(self, viral_videos: List[Dict]) -> Dict:
        """Extract winning patterns"""
        if not viral_videos:
            return {}
        
        # Analyze titles
        common_words = {}
        for video in viral_videos:
            title = video['title'].lower()
            words = title.split()
            for word in words:
                if len(word) > 3:
                    common_words[word] = common_words.get(word, 0) + 1
        
        top_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'avg_views': sum(v['views'] for v in viral_videos) / len(viral_videos),
            'avg_title_length': sum(len(v['title']) for v in viral_videos) / len(viral_videos),
            'common_words': top_words,
            'avg_engagement': sum((v['likes'] + v['comments']) / max(v['views'], 1) for v in viral_videos) / len(viral_videos) * 100
        }

# ==================== LAUNCH COMMAND CENTER ====================
class LaunchCommandCenter:
    """Complete launch orchestration"""
    
    def __init__(self):
        self.script_gen = ViralScriptGenerator()
        self.hashtag_engine = HashtagStrategy()
        self.analytics = AnalyticsTracker()
        self.thumbnail_gen = ThumbnailGenerator()
        self.competitor_spy = CompetitorSpy()
        
        # Create directories
        Path('scripts').mkdir(exist_ok=True)
        Path('thumbnails').mkdir(exist_ok=True)
        Path('reports').mkdir(exist_ok=True)
    
    def prepare_30_day_launch(self) -> Dict:
        """Prepare everything for 30-day launch"""
        logger.info("🚀 PREPARING 30-DAY LAUNCH...")
        
        # Generate 30 scripts
        scripts = self.script_gen.generate_batch(30)
        
        # Generate thumbnails
        thumbnails = []
        for i, script in enumerate(scripts, 1):
            thumb_path = f'thumbnails/day_{i}_thumbnail.png'
            self.thumbnail_gen.generate_thumbnail(script, thumb_path)
            thumbnails.append(thumb_path)
        
        # Generate hashtag strategy
        hashtag_plan = {}
        for platform in ['youtube', 'tiktok', 'instagram']:
            hashtag_plan[platform] = [
                self.hashtag_engine.generate_hashtags(platform, script['tool'])
                for script in scripts
            ]
        
        # Save everything
        launch_package = {
            'scripts': scripts,
            'thumbnails': thumbnails,
            'hashtag_plan': hashtag_plan,
            'created': datetime.now().isoformat()
        }
        
        with open('reports/30_day_launch_plan.json', 'w') as f:
            json.dump(launch_package, f, indent=2)
        
        # Create human-readable plan
        self._create_readable_plan(scripts, hashtag_plan)
        
        logger.info("✅ 30-DAY LAUNCH PACKAGE READY!")
        return launch_package
    
    def _create_readable_plan(self, scripts: List[Dict], hashtag_plan: Dict):
        """Create readable launch plan"""
        with open('reports/LAUNCH_PLAN.txt', 'w') as f:
            f.write("="*60 + "\n")
            f.write("30-DAY FACELESS YOUTUBE LAUNCH PLAN\n")
            f.write("="*60 + "\n\n")
            
            for i, script in enumerate(scripts, 1):
                f.write(f"\nDAY {i}: {script['hook']}\n")
                f.write("-" * 60 + "\n")
                f.write(f"Tool: {script['tool']}\n")
                f.write(f"Affiliate: {script['affiliate_link']}\n\n")
                f.write("SCRIPT:\n")
                f.write(script['full_script'] + "\n\n")
                f.write("YOUTUBE HASHTAGS:\n")
                f.write(' '.join(hashtag_plan['youtube'][i-1]) + "\n\n")
                f.write("TIKTOK HASHTAGS:\n")
                f.write(' '.join(hashtag_plan['tiktok'][i-1]) + "\n\n")
                f.write("INSTAGRAM HASHTAGS:\n")
                f.write(' '.join(hashtag_plan['instagram'][i-1]) + "\n\n")
                f.write("="*60 + "\n")
        
        logger.info("✅ Launch plan saved: reports/LAUNCH_PLAN.txt")
    
    def analyze_competition(self, niche: str = 'AI tools') -> Dict:
        """Spy on competition"""
        logger.info(f"🕵️ Analyzing {niche} competition...")
        
        top_channels = self.competitor_spy.find_top_channels(niche)
        
        report = {
            'niche': niche,
            'top_channels': top_channels,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Analyze top 3 channels deeply
        for channel in top_channels[:3]:
            viral_videos = self.competitor_spy.analyze_viral_videos(channel['channel_id'])
            channel['viral_videos'] = viral_videos
        
        with open('reports/competitor_analysis.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Competition analysis complete: {len(top_channels)} channels analyzed")
        return report

if __name__ == "__main__":
    center = LaunchCommandCenter()
    center.prepare_30_day_launch()
