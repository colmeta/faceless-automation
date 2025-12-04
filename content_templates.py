#!/usr/bin/env python3
"""
🎨 CONTENT TEMPLATES - Ensure Each Video is Unique
Provides rotating templates for hooks, narration, topics, and CTAs
"""

import random
from typing import Dict, List

# ==================== HOOK TEMPLATES ====================
HOOK_TEMPLATES = [
    "This AI Secret Changes Everything",
    "Stop Wasting Time on This",
    "The Tool Nobody Talks About",
    "I Tried This For 30 Days",
    "This Mistake Costs You Hours",
    "The Future of Work is Here",
    "Why Everyone is Switching",
    "This Will Blow Your Mind",
    "The Hidden Productivity Hack",
    "What Experts Don't Tell You",
    "The Game-Changing Strategy",
    "This AI Tool is Insane",
    "The Secret Top Performers Use",
    "Stop Doing This Wrong",
    "The Shortcut You Need",
]

# ==================== TOPIC CATEGORIES ====================
TOPIC_CATEGORIES = {
    "AI Automation": {
        "keywords": ["AI", "automation", "artificial intelligence", "machine learning"],
        "focus": "AI tools and automation technology"
    },
    "Productivity": {
        "keywords": ["productivity", "efficiency", "time management", "workflow"],
        "focus": "productivity tools and techniques"
    },
    "Business Growth": {
        "keywords": ["business", "growth", "strategy", "scaling"],
        "focus": "business growth and entrepreneurship"
    },
    "Tech Trends": {
        "keywords": ["technology", "innovation", "trends", "future"],
        "focus": "emerging technology trends"
    },
    "Side Hustles": {
        "keywords": ["side hustle", "income", "money", "passive income"],
        "focus": "side hustles and income generation"
    },
    "Digital Marketing": {
        "keywords": ["marketing", "social media", "content", "advertising"],
        "focus": "digital marketing strategies"
    },
    "Online Income": {
        "keywords": ["online income", "make money", "earnings", "revenue"],
        "focus": "making money online"
    },
    "Software Tools": {
        "keywords": ["software", "tools", "apps", "platforms"],
        "focus": "software and digital tools"
    },
    "Work From Home": {
        "keywords": ["remote work", "work from home", "flexibility", "digital nomad"],
        "focus": "remote work and flexibility"
    },
    "Creator Economy": {
        "keywords": ["creator", "content creation", "influencer", "monetization"],
        "focus": "content creation and monetization"
    },
}

# ==================== NARRATION TEMPLATES ====================
NARRATION_TEMPLATES = [
    {
        "style": "problem_solution",
        "template": "Most people waste hours on {problem}. But there's a smarter way. {solution} can transform your workflow in minutes. Imagine saving {benefit} every single day. Join thousands who've already made the switch. Don't get left behind."
    },
    {
        "style": "discovery",
        "template": "I discovered {solution} and everything changed. No more {problem}. No more wasted time. Just pure efficiency. This tool handles {feature} automatically. You focus on what matters. The results speak for themselves."
    },
    {
        "style": "urgent",
        "template": "Stop right now if you're still {problem}. You're losing {cost} every day. {solution} fixes this instantly. It's that simple. {benefit} in just minutes. Time is money. Don't waste another second."
    },
    {
        "style": "curiosity",
        "template": "What if I told you {claim}? Sounds impossible? It's not. {solution} makes it real. Here's how it works. {explanation}. Mind-blowing, right? That's just the beginning."
    },
    {
        "style": "social_proof",
        "template": "Over {number} people switched to {solution} this month. Why? Because it solves {problem} instantly. No learning curve. No complexity. Just results. They're saving {benefit} daily. You should too."
    },
    {
        "style": "transformation",
        "template": "Before {solution}, I struggled with {problem}. Everything took forever. Now? Everything's automated. {benefit} saved every single day. My productivity skyrocketed. This could be your story too."
    },
    {
        "style": "comparison",
        "template": "Traditional methods for {task} are outdated. Hours of manual work. Constant errors. {solution} changes the game. Same results. Ten times faster. Zero mistakes. The choice is obvious."
    },
    {
        "style": "shock",
        "template": "You're doing {task} wrong. Everyone is. Here's why. {problem} kills your productivity. But {solution} fixes it instantly. {benefit} guaranteed. No more struggle. Just pure efficiency."
    },
    {
        "style": "insider",
        "template": "Industry insiders have known this secret for years. {solution} for {task}. Now it's available to everyone. {benefit} from day one. Don't miss this opportunity. Join the smart ones."
    },
    {
        "style": "future",
        "template": "The future of {category} is here. {solution} is revolutionizing how we work. Imagine {vision}. It's happening now. Early adopters are winning. Will you join them?"
    },
]

# ==================== CTA TEMPLATES ====================
CTA_TEMPLATES = [
    "Try it free today",
    "Get started now",
    "Join thousands of users",
    "Start your free trial",
    "Click the link below",
    "Don't miss out",
    "Transform your workflow",
    "Get instant access",
    "Limited time offer",
    "Sign up free now",
    "Boost your productivity",
    "See it in action",
    "Unlock the power",
    "Experience the difference",
    "Make the switch today",
]

# ==================== PLACEHOLDERS ====================
PROBLEM_EXAMPLES = [
    "manual tasks",
    "repetitive work",
    "data entry",
    "content creation",
    "research",
    "scheduling",
    "email management",
    "report generation",
]

SOLUTION_EXAMPLES = [
    "this AI tool",
    "this automation platform",
    "this smart software",
    "this game-changer",
    "this innovation",
]

BENEFIT_EXAMPLES = [
    "10 hours per week",
    "countless hours",
    "valuable time",
    "money and time",
    "stress and effort",
]

# ==================== HELPER FUNCTIONS ====================

def get_random_hook() -> str:
    """Get a random hook from templates"""
    return random.choice(HOOK_TEMPLATES)

def get_random_topic() -> Dict[str, any]:
    """Get a random topic category"""
    topic_name = random.choice(list(TOPIC_CATEGORIES.keys()))
    topic_data = TOPIC_CATEGORIES[topic_name]
    return {
        "name": topic_name,
        "keywords": ", ".join(topic_data["keywords"]),
        "focus": topic_data["focus"],
        "primary_keyword": topic_data["keywords"][0]
    }

def get_random_narration(topic: Dict = None) -> str:
    """Generate random narration from templates"""
    template_data = random.choice(NARRATION_TEMPLATES)
    template = template_data["template"]
    
    # Fill in placeholders
    narration = template.format(
        problem=random.choice(PROBLEM_EXAMPLES),
        solution=random.choice(SOLUTION_EXAMPLES),
        benefit=random.choice(BENEFIT_EXAMPLES),
        feature="complex tasks",
        claim="you could save 10 hours this week",
        cost="time and money",
        explanation="Advanced AI handles everything automatically",
        number="10,000",
        task="productivity tasks",
        category=topic["name"] if topic else "work",
        vision="perfect efficiency with zero effort"
    )
    
    return narration

def get_random_cta() -> str:
    """Get a random CTA"""
    return random.choice(CTA_TEMPLATES)

def generate_unique_script() -> Dict[str, str]:
    """Generate a complete unique script with all variations"""
    topic = get_random_topic()
    
    return {
        "hook": get_random_hook(),
        "topic": topic,
        "narration": get_random_narration(topic),
        "cta": get_random_cta(),
        "style": random.choice(NARRATION_TEMPLATES)["style"]
    }

def get_timestamp_based_script(timestamp: str) -> Dict[str, str]:
    """Generate script based on timestamp for reproducible variety"""
    # Use timestamp as seed for consistent but varied results
    seed = sum(ord(c) for c in timestamp)
    random.seed(seed)
    
    script = generate_unique_script()
    
    # Reset random seed
    random.seed()
    
    return script

# ==================== COLOR SCHEMES FOR BACKGROUNDS ====================
COLOR_SCHEMES = [
    # Vibrant gradients
    [(45, 0, 90), (0, 45, 90)],      # Purple to Blue
    [(90, 0, 30), (45, 0, 90)],      # Red to Purple
    [(0, 90, 60), (0, 45, 90)],      # Teal to Blue
    [(45, 90, 0), (90, 90, 0)],      # Green to Yellow
    [(90, 30, 0), (45, 0, 90)],      # Orange to Purple
    [(0, 15, 45), (0, 45, 90)],      # Dark Blue to Blue
    [(90, 0, 45), (0, 0, 30)],       # Magenta to Dark
    [(75, 45, 0), (30, 15, 0)],      # Bronze gradient
    [(0, 60, 75), (0, 30, 45)],      # Ocean gradient
    [(45, 0, 60), (15, 0, 30)],      # Deep Purple gradient
]

def get_random_color_scheme() -> List[tuple]:
    """Get random color scheme for background"""
    return random.choice(COLOR_SCHEMES)

def get_timestamp_color_scheme(timestamp: str) -> List[tuple]:
    """Get color scheme based on timestamp"""
    seed = sum(ord(c) for c in timestamp)
    random.seed(seed)
    scheme = random.choice(COLOR_SCHEMES)
    random.seed()
    return scheme

def get_broll_query(topic: Dict) -> str:
    """
    Get varied b-roll search query for a topic
    Returns different search terms each time for the same topic
    """
    # Expanded b-roll queries per topic
    BROLL_QUERIES = {
        "AI Automation": [
            "artificial intelligence technology",
            "AI coding programming",
            "machine learning data",
            "automation workflow",
            "futuristic technology",
            "digital transformation"
        ],
        "Productivity": [
            "productive workspace setup",
            "time management planning",
            "organized desk office",
            "focused work environment",
            "professional workspace",
            "business productivity"
        ],
        "Business Growth": [
            "startup office teamwork",
            "business meeting strategy",
            "entrepreneur working laptop",
            "corporate growth success",
            "business analytics data",
            "team collaboration office"
        ],
        "Tech Trends": [
            "innovative technology future",
            "digital innovation screen",
            "technology trends modern",
            "futuristic interface",
            "tech startup workspace",
            "modern technology devices"
        ],
        "Side Hustles": [
            "side hustle laptop",
            "freelance work home",
            "online business computer",
            "entrepreneur working remotely",
            "digital nomad workspace",
            "passive income laptop"
        ],
        "Digital Marketing": [
            "social media marketing",
            "content creation filming",
            "digital advertising screen",
            "marketing analytics data",
            "influencer content creation",
            "brand marketing design"
        ],
        "Online Income": [
            "making money online",
            "ecommerce business",
            "online entrepreneur laptop",
            "digital business growth",
            "internet marketing",
            "online revenue analytics"
        ],
        "Software Tools": [
            "software development coding",
            "digital tools interface",
            "app development screen",
            "technology software design",
            "productivity apps phone",
            "modern software platform"
        ],
        "Work From Home": [
            "remote work home office",
            "home workspace setup",
            "telecommuting laptop",
            "digital nomad lifestyle",
            "flexible work environment",
            "cozy home office"
        ],
        "Creator Economy": [
            "content creator filming",
            "influencer recording video",
            "video production studio",
            "creator workspace setup",
            "social media content",
            "monetization creator"
        ]
    }
    
    topic_name = topic.get("name", "")
    
    # Get queries for this topic
    queries = BROLL_QUERIES.get(topic_name, [
        "business technology",
        "modern workspace",
        "digital innovation"
    ])
    
    # Return random query
    return random.choice(queries)

# ==================== MAIN TEST ====================
if __name__ == "__main__":
    print("🎨 Content Templates Test\n")
    
    print("=" * 60)
    print("Generating 3 unique scripts:")
    print("=" * 60)
    
    for i in range(3):
        script = generate_unique_script()
        print(f"\n📝 Script {i+1}:")
        print(f"   Hook: {script['hook']}")
        print(f"   Topic: {script['topic']['name']}")
        print(f"   Narration: {script['narration'][:80]}...")
        print(f"   CTA: {script['cta']}")
        print(f"   Style: {script['style']}")
    
    print("\n" + "=" * 60)
    print("✅ All templates loaded successfully!")
