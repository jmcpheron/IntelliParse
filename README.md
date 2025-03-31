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
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

### Configuration-Based Approach (Recommended)

The simplest way to use IntelliParse is with the configuration-based approach:

1. Define your feeds in `feeds_config.json`:
   ```json
   {
     "feeds": [
       {
         "name": "ai_feed",
         "description": "AI and Machine Learning Feed",
         "sources": [
           "https://example.com/feed1.xml",
           "https://example.com/feed2.xml"
         ],
         "primary_interest": "artificial_intelligence",
         "additional_interests": [
           "machine_learning",
           "deep_learning"
         ],
         "filter_keywords": [
           "ai", "neural", "machine learning"
         ],
         "max_episodes": 20,
         "output_file": "outputs/ai_feed.json"
       }
     ]
   }
   ```

2. Process your feeds:
   ```bash
   # List available feeds
   python process_feed.py --list
   
   # Process all feeds
   python process_feed.py
   
   # Process a specific feed
   python process_feed.py --feed ai_feed
   
   # Use a different config file
   python process_feed.py --config my_config.json
   ```

This approach makes it easy to define multiple feeds with different interests and sources.

### Command Line Interface (Legacy)

You can also use the original command line interface:

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

### Testing Options

#### Test with Mock Data

You can test the functionality without using real API calls:

```bash
python test_with_mock.py
```

This will use sample podcast data and a mocked Claude response to demonstrate how the tool works.

#### Test with Real Feeds

To test with real podcast feeds:

```bash
# Parse feeds but don't call Claude API
python test_real_feeds.py

# Process a small subset of episodes (5 random episodes)
python process_subset.py

# Process all episodes with Claude API (uses more API credits)
PROCESS_FULL=true python test_real_feeds.py
```

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

## Configuration Format

The `feeds_config.json` file uses the following format:

```json
{
  "feeds": [
    {
      "name": "feed_name",                      // Short name for the feed
      "description": "Feed description",        // Human-readable description
      "sources": [                              // Array of RSS feed URLs
        "https://example.com/feed1.xml",
        "https://example.com/feed2.xml"
      ],
      "primary_interest": "main_interest",      // Primary tag/theme
      "additional_interests": [                 // Other related interests
        "interest1",
        "interest2"
      ],
      "filter_keywords": [                      // Keywords to filter episodes
        "keyword1", "keyword2"
      ],
      "max_episodes": 30,                       // Max episodes to process
      "output_file": "outputs/feed_name.json"   // Output file path
    }
  ]
}
```

This structure makes it easy to define multiple feeds with different interests and sources.

## Examples

The `examples/` directory contains sample files to demonstrate the input and output formats:

- `examples/output/raw_episodes_sample.json`: Sample of the raw episode data extracted from feeds
- `examples/output/mock_enriched_feed.json`: Sample of the enriched JSON output from Claude

These examples show the data format at each stage of processing and can be used as references for building compatible media players or customizing the output format.

## Output Format

IntelliParse produces a JSON file that is compatible with simple media players. The output format looks like:

```json
{
  "feeds": [
    {
      "id": "feed-name",
      "title": "Feed Description",
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
            "relevance_match": "How this content matches the interests"
          }
        }
      ]
    }
  ]
}
```

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
