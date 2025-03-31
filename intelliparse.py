import sys
import os

# Patch for the cgi module issue in Python 3.13+
if sys.version_info >= (3, 13):
    import html
    sys.modules['cgi'] = type('CGIModule', (), {
        'parse_header': lambda header: (header, {}),
        'escape': html.escape,
    })

import feedparser
import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Claude API endpoint and credentials
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

class IntelliParse:
    def __init__(self, feeds: List[str], user_interests: List[str]):
        """
        Initialize IntelliParse with a list of RSS feed URLs and user interests.
        
        Args:
            feeds: List of podcast RSS feed URLs
            user_interests: List of user interest tags
        """
        self.feeds = feeds
        self.user_interests = user_interests
        
    def parse_feeds(self) -> List[Dict[str, Any]]:
        """Parse all feeds and return list of episodes with metadata."""
        all_episodes = []
        
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    episode = {
                        "id": entry.get("id", entry.get("guid", f"ep-{hash(entry.title)}")),
                        "title": entry.get("title", "Unknown Title"),
                        "date": entry.get("published", datetime.now().isoformat()),
                        "summary": entry.get("summary", entry.get("description", "")),
                        "source_feed": feed.feed.get("title", feed_url),
                        "media_url": None,
                        "duration": None,
                    }
                    
                    # Extract media URL and duration if available
                    if "enclosures" in entry and len(entry.enclosures) > 0:
                        for enclosure in entry.enclosures:
                            if enclosure.get("type", "").startswith("audio/"):
                                episode["media_url"] = enclosure.get("href", None)
                                break
                    
                    # Try to find duration
                    if "itunes_duration" in entry:
                        episode["duration"] = entry.itunes_duration
                    
                    all_episodes.append(episode)
            except Exception as e:
                print(f"Error parsing feed {feed_url}: {str(e)}")
        
        return all_episodes
    
    def create_text_blob(self, episodes: List[Dict[str, Any]]) -> str:
        """Convert episode metadata to a natural language text blob."""
        text_blob = f"PODCAST FEED CONTENT ({len(episodes)} episodes):\n\n"
        
        for episode in episodes:
            text_blob += f"EPISODE: {episode['title']}\n"
            text_blob += f"DATE: {episode['date']}\n"
            text_blob += f"SOURCE: {episode['source_feed']}\n"
            text_blob += f"MEDIA URL: {episode['media_url']}\n"
            
            if episode['duration']:
                text_blob += f"DURATION: {episode['duration']}\n"
                
            text_blob += f"SUMMARY: {episode['summary']}\n\n"
            text_blob += "---\n\n"
        
        return text_blob
    
    def create_claude_prompt(self, text_blob: str) -> str:
        """Create prompt for Claude with user interests and feed content."""
        interests_text = "\n- ".join(self.user_interests)
        
        prompt = f"""You are IntelliParse, an LLM agent that identifies relevant episodes from podcast feeds and returns JSON content for use in a simple media player.

This user is interested in the following topics:
- {interests_text}

Below is a mix of episodes from multiple podcast feeds. Extract relevant ones and enhance them.

Craft the JSON output with attention to where topics intersect with these interests or themes, and note intersections where appropriate in the `intelliparse_insight` section.

Return structured JSON in this format:
{{
  "feeds": [
    {{
      "id": "intelliparse-curated",
      "title": "IntelliParse Curated Feed",
      "tracks": [
        {{
          "id": "episode_id", 
          "title": "Episode Title",
          "description": "Enhanced description with key points",
          "audioUrl": "media_url",
          "date_iso": "ISO-formatted date",
          "runtime_minutes": minutes,
          "intelliparse_enrichment": {{
            "precision_summary": "2-3 sentence focused summary",
            "technical_elements": [
              {{"concept": "relevant technical concept", "relevance": 0.0-1.0}}
            ],
            "content_density": "LOW/MEDIUM/HIGH",
            "confidence_score": 0.0-1.0,
            "preference_match": true/false,
            "intelliparse_insight": "Why this might interest the user"
          }}
        }}
      ]
    }}
  ]
}}

FEED CONTENT:
{text_blob}
"""
        return prompt
    
    def call_claude_api(self, prompt: str) -> Dict[str, Any]:
        """Submit prompt to Claude API and return JSON response."""
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(CLAUDE_API_URL, headers=headers, json=data)
        
        if response.status_code != 200:
            raise Exception(f"Claude API error: {response.status_code} {response.text}")
        
        response_data = response.json()
        
        # Extract text from the response
        response_text = response_data["content"][0]["text"]
        
        # Extract JSON from response text
        try:
            # Find JSON in the response (it might be wrapped in ```json and ```)
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_str = response_text[json_start:json_end]
            
            parsed_json = json.loads(json_str)
            return parsed_json
        except Exception as e:
            raise Exception(f"Failed to parse JSON from Claude response: {str(e)}")
    
    def process(self) -> Dict[str, Any]:
        """Run the full IntelliParse process and return enriched JSON."""
        # 1. Parse all feeds to extract raw episode data
        episodes = self.parse_feeds()
        
        # 2. Convert episodes to text blob
        text_blob = self.create_text_blob(episodes)
        
        # 3. Create Claude prompt with text blob and user interests
        prompt = self.create_claude_prompt(text_blob)
        
        # 4. Call Claude API with the prompt
        enriched_json = self.call_claude_api(prompt)
        
        return enriched_json
    
    def save_output(self, data: Dict[str, Any], filename: str = "intelliparse_output.json"):
        """Save the enriched JSON output to a file."""
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved output to {filename}")


def main():
    """Example usage of IntelliParse."""
    # Example feed URLs
    feeds = [
        "https://cyberpodcast.fm/feed.xml",
        "https://aiinsightsdaily.com/rss"
    ]
    
    # Example user interests from README
    user_interests = [
        "ai_hobbies",  # new tag the user is creating
        "web_accessibility",
        "bobsburgers", 
        "3d_printing",
        "retro_gaming",
        "open_source_hardware"
    ]
    
    # Initialize and run IntelliParse
    parser = IntelliParse(feeds=feeds, user_interests=user_interests)
    
    try:
        result = parser.process()
        parser.save_output(result)
        print("IntelliParse processing complete!")
    except Exception as e:
        print(f"Error during IntelliParse processing: {str(e)}")


if __name__ == "__main__":
    main() 