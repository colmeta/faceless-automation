"""
YouTube SEO Manager
Generates optimized descriptions, keywords, and hashtags for YouTube Shorts
Manages affiliate link rotation and tracking
"""
import json
import os
import random
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class YouTubeSEOManager:
    """Manages YouTube SEO optimization and affiliate link integration"""
    
    def __init__(self, affiliate_config_path: str = "affiliate_programs.json"):
        self.affiliate_programs = self._load_affiliate_programs(affiliate_config_path)
        self.channel_name = "AI Tools Daily"  # Can be configured
        
    def _load_affiliate_programs(self, config_path: str) -> List[Dict]:
        """Load affiliate program configuration"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('programs', [])
        else:
            logger.warning(f"Affiliate config not found: {config_path}")
            return self._get_default_programs()
    
    def _get_default_programs(self) -> List[Dict]:
        """Default affiliate programs (placeholders - user will add real links)"""
        return [
            {
                "name": "Synthesys AI",
                "url": "https://synthesys.io/?ref=YOURREF",
                "commission": "40% lifetime",
                "category": ["video", "ai", "content_creation"],
                "hook": "Create stunning AI videos in minutes",
                "priority": 1
            },
            {
                "name": "Jasper AI",
                "url": "https://jasper.ai/?via=YOURREF",
                "commission": "30% recurring",
                "category": ["writing", "content", "ai"],
                "hook": "AI writing tool that saves hours",
                "priority": 1
            },
            {
                "name": "Notion AI",
                "url": "https://affiliate.notion.so/YOURREF",
                "commission": "50%",
                "category": ["productivity", "organization", "ai"],
                "hook": "Your AI-powered productivity workspace",
                "priority": 1
            },
            {
                "name": "Copy.ai",
                "url": "https://copy.ai/?via=YOURREF",
                "commission": "45% first year",
                "category": ["copywriting", "marketing", "ai"],
                "hook": "Generate high-converting copy with AI",
                "priority": 2
            },
            {
                "name": "Murf AI",
                "url": "https://murf.ai/?lmref=YOURREF",
                "commission": "30% recurring",
                "category": ["voiceover", "audio", "ai"],
                "hook": "Professional AI voiceovers",
                "priority": 2
            }
        ]
    
    def generate_channel_description(self) -> str:
        """Generate SEO-optimized channel description"""
        return f"""🤖 Your #1 Source for AI Tools & Productivity Hacks

Discover game-changing AI tools that save hours every day. We test and review the latest AI innovations so you don't have to.

💡 What You'll Get:
✅ Daily AI tool discoveries
✅ Time-saving automation hacks  
✅ Honest reviews & real demonstrations
✅ Exclusive deals & early access

🎯 Perfect For:
• Entrepreneurs seeking efficiency
• Content creators scaling up
• Remote workers maximizing productivity
• Tech enthusiasts staying ahead

🔔 New shorts daily | Subscribe for your daily AI advantage

#AITools #Productivity #Automation #TechReviews
"""
    
    def generate_video_description(
        self, 
        hook: str, 
        topic: str,
        tool_name: Optional[str] = None,
        special_offer: Optional[str] = None
    ) -> str:
        """Generate SEO-optimized video description with affiliate links"""
        
        # Get relevant affiliate programs
        relevant_programs = self._get_relevant_programs(topic, limit=3)
        
        # Primary affiliate (if tool_name matches)
        primary_link = None
        for prog in self.affiliate_programs:
            if tool_name and tool_name.lower() in prog['name'].lower():
                primary_link = prog
                break
        
        if not primary_link and relevant_programs:
            primary_link = relevant_programs[0]
        
        # Build description
        description = f"""{hook}

"""
        
        # Add primary affiliate link
        if primary_link:
            offer_text = special_offer or "Limited time offer"
            description += f"""🔥 Get {primary_link['name']} Here: {primary_link['url']}
({offer_text} - {primary_link['commission']} commission for affiliates)

"""
        
        # Add value proposition
        description += f"""📌 What This Does:
Discover how this AI tool transforms your workflow. Save time, boost productivity, and stay ahead of the curve.

"""
        
        # Additional affiliate programs
        if relevant_programs:
            description += "🎯 MORE AI TOOLS YOU'LL LOVE:\n\n"
            for prog in relevant_programs[:3]:
                description += f"• {prog['name']}: {prog['url']}\n  {prog['hook']}\n\n"
        
        # Call to actions
        description += """---
📺 Subscribe for daily AI discoveries
🔔 Turn on notifications - New tool revealed daily
💬 Comment your favorite AI tool below
👍 Like if this helped you

"""
        
        # Hashtags
        hashtags = self.get_optimized_hashtags(topic)
        description += f"{' '.join(hashtags)}\n\n"
        
        # Disclaimer
        description += """---
⚠️ Disclaimer: Some links are affiliate links. We only recommend tools we genuinely use and believe add value."""
        
        return description
    
    def get_optimized_hashtags(self, topic: str) -> List[str]:
        """Generate optimized hashtag combination for topic"""
        
        # Base hashtags (always included)
        base_tags = ["#Shorts", "#AITools", "#Productivity"]
        
        # Topic-specific hashtags
        topic_lower = topic.lower()
        topic_specific = []
        
        if "video" in topic_lower or "content" in topic_lower:
            topic_specific = ["#VideoCreation", "#ContentCreation", "#AIVideo"]
        elif "writing" in topic_lower or "copy" in topic_lower:
            topic_specific = ["#Copywriting", "#AIWriting", "#ContentWriting"]
        elif "productivity" in topic_lower or "work" in topic_lower:
            topic_specific = ["#WorkFromHome", "#RemoteWork", "#TimeManagement"]
        elif "marketing" in topic_lower:
            topic_specific = ["#DigitalMarketing", "#Marketing", "#GrowthHacks"]
        else:
            topic_specific = ["#Automation", "#TechHacks", "#Innovation"]
        
        # Trending/viral hashtags
        trending = ["#TechTips", "#LifeHacks", "#MustHave"]
        
        # Combine and limit to 10 hashtags (YouTube best practice)
        all_tags = base_tags + topic_specific + trending
        return all_tags[:10]
    
    def _get_relevant_programs(self, topic: str, limit: int = 3) -> List[Dict]:
        """Get affiliate programs relevant to the topic"""
        topic_lower = topic.lower()
        relevant = []
        
        for prog in self.affiliate_programs:
            # Check if topic matches any category
            if any(cat in topic_lower for cat in prog.get('category', [])):
                relevant.append(prog)
        
        # Sort by priority
        relevant.sort(key=lambda x: x.get('priority', 999))
        
        return relevant[:limit]
    
    def get_video_title(self, hook: str, max_length: int = 100) -> str:
        """Generate SEO-optimized title"""
        # Ensure title is compelling and within length limit
        title = hook.strip()
        
        # Add #Shorts tag if not present
        if "#shorts" not in title.lower() and "#short" not in title.lower():
            title += " #Shorts"
        
        # Truncate if too long
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        return title

if __name__ == "__main__":
    # Test the SEO manager
    logging.basicConfig(level=logging.INFO)
    
    seo = YouTubeSEOManager()
    
    print("=== CHANNEL DESCRIPTION ===")
    print(seo.generate_channel_description())
    
    print("\n\n=== VIDEO DESCRIPTION ===")
    desc = seo.generate_video_description(
        hook="This AI Tool Changed Everything",
        topic="video creation ai",
        tool_name="Synthesys AI",
        special_offer="50% OFF - First 100 users"
    )
    print(desc)
    
    print("\n\n=== HASHTAGS ===")
    tags = seo.get_optimized_hashtags("remote work productivity")
    print(" ".join(tags))
