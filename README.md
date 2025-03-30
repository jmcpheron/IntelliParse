# IntelliParse MVP: Smart Podcast-to-JSON Agent for Media Aggregation

This is the minimal viable version of IntelliParse, focused on one core thing:

> **Take a couple of podcast RSS feeds, extract their content, and convert it into a structured JSON format, suitable for enrichment and media playback.**

## What It Does (Right Now)
- Uses Python’s `feedparser` library to retrieve and parse RSS feeds
- Extracts raw metadata for each episode (title, date, summary, media URL, duration if available)
- Bundles the episodes into a natural-language blob with minimal cleanup
- Passes that blob to Claude (Anthropic API) along with a prompt and user interests
- Claude returns a structured JSON object following the simple IntelliParse schema

## Project Goals (MVP)
- ✅ Aggregate 2+ podcast feeds
- ✅ Convert raw feed content into general-purpose natural language text
- ✅ Submit text + metadata to Claude with smart instructions
- ✅ Receive back enriched metadata in JSON
- ✅ Include user preferences and interest tags in the prompt

## Example User Profile Tags
This MVP includes sample interests tagged as follows:
- `ai_hobbies` (new tag the user is creating)
- `web_accessibility`
- `bobsburgers`
- `3d_printing`
- `retro_gaming`
- `open_source_hardware`

These tags help Claude decide what content to keep, prioritize, or summarize.

## Example Prompt (abbreviated)
```
You are IntelliParse, an LLM agent that identifies relevant episodes from podcast feeds and returns JSON content for use in a simple media player.

This user is creating a new tag called "ai_hobbies" to group interesting media about artificial intelligence, emerging tech, and tools.
Their broader interests also include:
- Web accessibility
- The TV show Bob's Burgers
- 3D printing
- Retro gaming
- Open source hardware

Below is a mix of episodes from multiple podcast feeds. Extract relevant ones and enhance them.

Craft the JSON output with attention to where topics intersect with these hobbies or themes, and note intersections where appropriate in the `intelliparse_insight` section.

Return structured JSON in this format:
{
  "episode_id": "unique_id",
  "core_data": {
    "title": "...",
    "date_iso": "...",
    "runtime_minutes": ...,
    "media_url": "..."
  },
  "intelliparse_enrichment": {
    "precision_summary": "...",
    "technical_elements": [
      {"concept": "...", "relevance": ...}
    ],
    "content_density": "...",
    "confidence_score": ...,
    "preference_match": true,
    "intelliparse_insight": "..."
  }
}
```

## Example Feeds (sample only)
- `https://cyberpodcast.fm/feed.xml`
- `https://aiinsightsdaily.com/rss`

## Stack
- Python 3.x
- `feedparser` for RSS
- `requests` for HTTP
- Claude via Anthropic API

## Coming Soon (Post-MVP)
- Simple web UI to paste in RSS feeds
- Optional HTML blog/video content input
- Save output to `.json` or preview inline

This MVP is intentionally lean. The goal is to get from feed → text blob → Claude → JSON with minimal friction, while respecting personal interests and discovering relevant content.

Let's make messy media work for humans.
