# IntelliParse MVP: Smart Podcast-to-JSON Agent for Media Aggregation

This is the minimal viable version of IntelliParse, focused on one core thing:

> **Take a couple of podcast RSS feeds, extract their content, and convert it into a structured JSON format, suitable for enrichment and media playback.**

## What It Does (Right Now)
- Uses Python's `feedparser` library to retrieve and parse RSS feeds
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

## Setup

### Requirements
- Python 3.7+
- Anthropic API key (for Claude) - [Get one here](https://console.anthropic.com/)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/intelliparse.git
   cd intelliparse
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your API key:
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key to the `.env` file
   ```
   cp .env.example .env
   # Then edit .env with your API key
   ```

## Usage

### Command Line Interface

The simplest way to use IntelliParse is through the command line interface:

```bash
# Basic usage with podcast RSS feed URLs
python cli.py --feeds https://cyberpodcast.fm/feed.xml https://aiinsightsdaily.com/rss

# Add user interests to help Claude filter and prioritize content
python cli.py --feeds https://example.com/feed1.xml https://example.com/feed2.xml \
              --interests ai_hobbies web_accessibility 3d_printing

# Specify output file
python cli.py --feeds https://example.com/feed.xml \
              --output my_custom_feed.json
```

### Test with Mock Data

You can test the functionality without using real API calls:

```bash
python test_with_mock.py
```

This will use sample podcast data and a mocked Claude response to demonstrate how the tool works.

### Python API

You can also use IntelliParse programmatically:

```python
from intelliparse import IntelliParse

# Initialize with feed URLs and user interests
parser = IntelliParse(
    feeds=["https://example.com/feed1.xml", "https://example.com/feed2.xml"],
    user_interests=["ai_hobbies", "3d_printing", "web_accessibility"]
)

# Process feeds and get enriched JSON
result = parser.process()

# Save to file
parser.save_output(result, "my_feed.json")
```

## Output Format

IntelliParse produces a JSON file that is compatible with simple media players. The output format looks like:

```json
{
  "feeds": [
    {
      "id": "intelliparse-curated",
      "title": "IntelliParse Curated Feed",
      "tracks": [
        {
          "id": "unique_episode_id",
          "title": "Episode Title",
          "description": "Enhanced description with key points",
          "audioUrl": "https://example.com/episode.mp3",
          "date_iso": "2023-06-15T12:00:00Z",
          "runtime_minutes": 45.5,
          "intelliparse_enrichment": {
            "precision_summary": "2-3 sentence focused summary",
            "technical_elements": [
              {"concept": "relevant technical concept", "relevance": 0.9}
            ],
            "content_density": "MEDIUM",
            "confidence_score": 0.85,
            "preference_match": true,
            "intelliparse_insight": "Why this might interest the user"
          }
        }
      ]
    }
  ]
}
```

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
