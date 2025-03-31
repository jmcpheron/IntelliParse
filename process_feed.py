#!/usr/bin/env python3
"""
Process RSS feeds based on configuration file.
A more straightforward approach to feed processing with IntelliParse.
"""

import os
import json
import argparse
from dotenv import load_dotenv
from intelliparse import IntelliParse

# Load environment variables from .env file
load_dotenv()

def load_config(config_file="feeds_config.json"):
    """Load feed configurations from JSON file."""
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file {config_file} not found.")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Configuration file {config_file} contains invalid JSON.")
        return None

def process_feed(feed_config):
    """Process a single feed based on its configuration."""
    print(f"Processing feed: {feed_config['name']} - {feed_config['description']}")
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Anthropic API key not set. Please add it to your .env file.")
        return False
    
    # Print feed info
    print(f"Primary interest: {feed_config['primary_interest']}")
    print(f"Additional interests: {', '.join(feed_config['additional_interests'])}")
    print(f"Sources: {', '.join(feed_config['sources'])}")
    
    # Initialize IntelliParse with feed sources and interests
    all_interests = [feed_config['primary_interest']] + feed_config['additional_interests']
    parser = IntelliParse(feeds=feed_config['sources'], user_interests=all_interests)
    
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(feed_config['output_file'])
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # First, fetch the episodes
        print("Fetching episodes from feeds...")
        episodes = parser.parse_feeds()
        
        # Save raw episodes if requested
        raw_file = f"{output_dir}/{feed_config['name']}_raw.json" if output_dir else f"{feed_config['name']}_raw.json"
        with open(raw_file, "w") as f:
            json.dump(episodes, f, indent=2)
        
        print(f"Fetched {len(episodes)} episodes")
        
        # Filter episodes based on keywords
        if 'filter_keywords' in feed_config and feed_config['filter_keywords']:
            keywords = feed_config['filter_keywords']
            filtered_episodes = []
            
            for episode in episodes:
                # Create string for search
                searchable_text = f"{episode.get('title', '')} {episode.get('summary', '')}".lower()
                
                # Check if any keyword appears in the episode
                if any(keyword.lower() in searchable_text for keyword in keywords):
                    filtered_episodes.append(episode)
            
            print(f"Filtered to {len(filtered_episodes)} relevant episodes")
            episodes = filtered_episodes
        
        # Limit to max episodes
        max_episodes = feed_config.get('max_episodes', 30)
        if len(episodes) > max_episodes:
            print(f"Limiting to {max_episodes} episodes for processing")
            episodes = episodes[:max_episodes]
        
        # Create a custom IntelliParse class that uses our filtered episodes
        class ConfiguredIntelliParse(IntelliParse):
            def parse_feeds(self):
                """Return the filtered episodes instead of parsing feeds."""
                return episodes
                
            def create_claude_prompt(self, text_blob: str) -> str:
                """Create a custom prompt based on the feed configuration."""
                interests_text = "\n- ".join(self.user_interests)
                primary_interest = feed_config['primary_interest']
                feed_name = feed_config['name']
                
                prompt = f"""You are IntelliParse, an LLM agent that identifies relevant episodes from podcast feeds and returns JSON content for a media player.

This feed is focused primarily on {primary_interest}, with these additional interests:
- {interests_text}

Below is a mix of episodes from multiple podcast feeds. Extract the most relevant ones and enhance them.

For each episode, provide:
1. A precise but engaging description that captures the key points
2. Technical elements and concepts covered with their relevance score
3. A short precision summary (1-3 sentences)
4. Why this content matches the primary interest and any additional interests

Return structured JSON in this format:
{{
  "feeds": [
    {{
      "id": "{feed_name}-feed",
      "title": "{feed_config['description']}",
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
            "relevance_match": "How this content matches the primary and additional interests"
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
        
        # Create the custom parser
        custom_parser = ConfiguredIntelliParse(feeds=[], user_interests=all_interests)
        
        print("Processing with Claude API...")
        result = custom_parser.process()
        
        # Save the result
        output_file = feed_config['output_file']
        custom_parser.save_output(result, output_file)
        
        print(f"Successfully created feed. Output saved to {output_file}")
        
        # Print a summary
        if "feeds" in result and len(result["feeds"]) > 0:
            feed = result["feeds"][0]
            print(f"\nCreated feed: {feed['title']}")
            print(f"Total tracks: {len(feed['tracks'])}")
            print("\nSample tracks:")
            for i, track in enumerate(feed["tracks"][:3], 1):
                print(f"{i}. {track['title']}")
                if "intelliparse_enrichment" in track and "relevance_match" in track["intelliparse_enrichment"]:
                    relevance = track["intelliparse_enrichment"]["relevance_match"]
                    # Truncate if too long
                    if len(relevance) > 100:
                        relevance = relevance[:97] + "..."
                    print(f"   Relevance: {relevance}")
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Process feeds based on command-line arguments and configuration."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process podcast feeds based on configuration")
    parser.add_argument("--config", default="feeds_config.json",
                        help="Path to configuration file (default: feeds_config.json)")
    parser.add_argument("--feed", help="Process only the specified feed")
    parser.add_argument("--list", action="store_true", help="List available feeds")
    parser.add_argument("--api-key", help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["ANTHROPIC_API_KEY"] = args.api_key
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        return
    
    # List feeds if requested
    if args.list:
        print("Available feeds:")
        for i, feed in enumerate(config["feeds"], 1):
            print(f"{i}. {feed['name']} - {feed['description']}")
        return
    
    # Process specific feed if requested
    if args.feed:
        for feed in config["feeds"]:
            if feed["name"] == args.feed:
                process_feed(feed)
                return
        print(f"ERROR: Feed '{args.feed}' not found in configuration.")
        return
    
    # Process all feeds
    success_count = 0
    for feed in config["feeds"]:
        success = process_feed(feed)
        if success:
            success_count += 1
        print("\n" + "-"*50 + "\n")
    
    print(f"Processed {success_count}/{len(config['feeds'])} feeds successfully.")


if __name__ == "__main__":
    main() 