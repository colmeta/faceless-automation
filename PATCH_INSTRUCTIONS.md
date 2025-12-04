# CONTENT VARIATION FIX - INSTRUCTIONS FOR DEPLOYMENT

Due to file complexity, here are the MANUAL CHANGES needed for `master_automation.py`:

## Changes to Apply

### 1. Add imports at top (after line 60):
```python
# Import music manager  
try:
    from music_manager import MusicManager
    MUSIC_MANAGER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Music manager not found")
    MUSIC_MANAGER_AVAILABLE = False

# Import thumbnail generator
try:
    from thumbnail_generator import ThumbnailGenerator
    THUMBNAIL_GEN_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Thumbnail generator not found")
    THUMBNAIL_GEN_AVAILABLE = False
```

### 2. In `_create_default_analysis()` method (Line 172-230):
**CHANGE LINE 176-177 FROM:**
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
script = get_timestamp_based_script(timestamp)
```

**TO:**
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
script = get_timestamp_based_script(timestamp)

# Log for visibility
logger.info(f"🎭 Using template style: {script.get('style', 'default')}")
logger.info(f"📂 Topic category: {script['topic']['name']}")
```

### 3. In `generate_hybrid_video()` method (Line 1001):
**CHANGE LINE 1001 FROM:**
```python
topic = script.get('topic', 'technology')
```

**TO:**
```python
# Use broll_query if provided, otherwise extract from topic object
if 'broll_query' in script:
    topic = script['broll_query']
elif isinstance(script.get('topic'), dict):
    # Use primary keyword from topic object
    from content_templates import get_broll_query
    topic = get_broll_query(script['topic'])
    logger.info(f"🎬 B-roll query: '{topic}'")
else:
    topic = str(script.get('topic', 'technology'))
```

### 4. In `run_daily_automation()` method (Line 1144-1149):
**REPLACE ENTIRE SCRIPT CREATION BLOCK WITH:**
```python
# ✨ Generate varied content using templates
if TEMPLATES_AVAILABLE:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    varied_script = get_timestamp_based_script(timestamp)
    
    # Merge with analysis
    script = {
        'hook': varied_script['hook'],  # Use varied hook
        'narration': analysis['summary'],  # Use analyzed summary
        'cta': varied_script['cta'],  # Use varied CTA
        'topic':varied_script['topic']  # Full topic object with primary_keyword!
    }
    
    # Get varied b-roll query
    from content_templates import get_broll_query
    script['broll_query'] = get_broll_query(script['topic'])
    
    logger.info(f"🎭 Template: {varied_script.get('style')}")
    logger.info(f"📂 Topic: {script['topic']['name']}")
    logger.info(f"🎬 B-roll: '{script['broll_query']}'")
else:
    # Fallback
    script = {
        'hook': analysis['short_hook'],
        'narration': analysis['summary'],
        'cta': analysis['cta'],
        'topic': analysis.get('key_topics', 'technology').split(',')[0]
    }
```

### 5. After video generation (after line 1158), ADD:
```python
# Generate professional thumbnail
thumbnail_path = None
if THUMBNAIL_GEN_AVAILABLE and 'hook' in script:
    try:
        from thumbnail_generator import ThumbnailGenerator
        thumb_gen = ThumbnailGenerator()
        thumbnail_path = f"temp/thumbnail_{timestamp}.jpg"
        
        # Get color scheme
        if TEMPLATES_AVAILABLE:
            from content_templates import get_timestamp_color_scheme
            color_scheme = get_timestamp_color_scheme(timestamp)
        else:
            color_scheme = None
        
        thumb_gen.create_thumbnail(
            video_path=output_path,
            text=script['hook'],
            output_path=thumbnail_path,
            color_scheme=color_scheme
        )
        logger.info(f"✅ Thumbnail: {thumbnail_path}")
    except Exception as e:
        logger.warning(f"⚠️ Thumbnail failed: {e}")
```

## Testing

After applying changes:
```bash
cd c:\Users\LENOVO\Desktop\faceless-automation
python -c "from content_templates import generate_unique_script; print(generate_unique_script())"
```

Expected: Dict with 'hook', 'topic' (dict object), 'narration', 'cta', 'style'

## Deployment

1. Apply changes manually to `master_automation.py`
2. Commit: `git add -A && git commit -m "feat: content variation + thumbnails"`
3. Push: `git push origin main`
4. Render will auto-deploy in ~2 minutes
