#!/usr/bin/env python3
"""
Process RSS feeds into a format compatible with "Did you hear that?" player.
Creates JSON files that adhere to the required feed structure.
"""

import os
import json
import argparse
import re
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

def sanitize_id(text):
    """Convert text to a valid ID format."""
    # Remove non-alphanumeric characters and replace spaces with hyphens
    return re.sub(r'[^a-zA-Z0-9-]', '', text.lower().replace(' ', '-'))

def process_feed(feed_config, player_format=True):
    """Process a single feed based on its configuration."""
    print(f"Processing feed: {feed_config['name']} - {feed_config['description']}")
    
    # Check for API key if we're using enrichment
    if not os.environ.get("ANTHROPIC_API_KEY") and player_format == False:
        print("WARNING: Anthropic API key not set. Will generate basic feed without enrichment.")
    
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
        
        # Fetch the episodes
        print("Fetching episodes from feeds...")
        episodes = parser.parse_feeds()
        
        print(f"Fetched {len(episodes)} episodes")
        
        # Filter episodes based on keywords if specified
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
        
        # If we just want the player format without enrichment
        if player_format:
            # Create the player-compatible feed structure
            feed_id = sanitize_id(feed_config['name'])
            
            result = {
                "feeds": [
                    {
                        "id": feed_id,
                        "title": feed_config['description'],
                        "tracks": []
                    }
                ]
            }
            
            # Convert episodes to the required track format
            for episode in episodes:
                track_id = sanitize_id(episode.get('title', 'unknown-track'))
                
                # Get the audio URL - check different formats
                audio_url = ''
                if 'media_url' in episode and episode['media_url']:
                    # Direct media_url field
                    audio_url = episode['media_url']
                elif 'enclosures' in episode and episode['enclosures']:
                    # Extract from enclosures list
                    for enclosure in episode['enclosures']:
                        if 'href' in enclosure:
                            audio_url = enclosure['href']
                            break
                
                track = {
                    "id": track_id,
                    "title": episode.get('title', 'Untitled Track'),
                    "audioUrl": audio_url,
                    "description": episode.get('summary', '')
                }
                
                # Add image if available
                if 'image' in episode and 'href' in episode['image']:
                    track["albumArt"] = episode['image']['href']
                elif 'image_url' in episode and episode['image_url']:
                    track["albumArt"] = episode['image_url']
                
                # Only add tracks with valid audio URLs
                if track["audioUrl"]:
                    result["feeds"][0]["tracks"].append(track)
                else:
                    print(f"Warning: No audio URL found for track: {track['title']}")
            
            # Save the result
            output_file = feed_config['output_file']
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"Successfully created player-compatible feed. Output saved to {output_file}")
            print(f"Total tracks: {len(result['feeds'][0]['tracks'])}")
            
            return True
            
        else:
            # For enriched format, use Claude API
            # This is similar to the existing process_feed.py functionality
            all_interests = [feed_config['primary_interest']] + feed_config['additional_interests']
            
            # Create a custom IntelliParse class with the proper output format
            class PlayerFormatIntelliParse(IntelliParse):
                def parse_feeds(self):
                    """Return the filtered episodes instead of parsing feeds."""
                    return episodes
                    
                def create_claude_prompt(self, text_blob: str) -> str:
                    """Create a prompt that will produce player-compatible output."""
                    interests_text = "\n- ".join(self.user_interests)
                    feed_name = feed_config['name']
                    feed_id = sanitize_id(feed_name)
                    
                    prompt = f"""You are IntelliParse, an agent that processes podcast feeds into a specific JSON format for the "Did you hear that?" audio player.

Below is a mix of episodes from podcast feeds. Extract the relevant ones and format them according to these exact requirements:

1. Each feed must have an "id", "title", and "tracks" array
2. Each track must have an "id", "title", and "audioUrl"
3. Tracks can optionally have "description" and "albumArt"
4. The output structure must follow this exact format

The feed is focused on {feed_config['primary_interest']}, with these additional interests:
- {interests_text}

Return structured JSON in this EXACT format - do not add any additional fields:
{{
  "feeds": [
    {{
      "id": "{feed_id}",
      "title": "{feed_config['description']}",
      "tracks": [
        {{
          "id": "track-id", 
          "title": "Episode Title",
          "audioUrl": "media_url",
          "description": "Episode description",
          "albumArt": "image_url"
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
            custom_parser = PlayerFormatIntelliParse(feeds=[], user_interests=all_interests)
            
            print("Processing with Claude API...")
            result = custom_parser.process()
            
            # Save the result
            output_file = feed_config['output_file']
            custom_parser.save_output(result, output_file)
            
            print(f"Successfully created enriched player-compatible feed. Output saved to {output_file}")
            
            # Print a summary
            if "feeds" in result and len(result["feeds"]) > 0:
                feed = result["feeds"][0]
                print(f"\nCreated feed: {feed['title']}")
                print(f"Total tracks: {len(feed['tracks'])}")
            
            return True
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    """Process feeds based on command-line arguments and configuration."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process podcast feeds into 'Did you hear that?' player format")
    parser.add_argument("--config", default="feeds_config.json",
                        help="Path to configuration file (default: feeds_config.json)")
    parser.add_argument("--feed", help="Process only the specified feed")
    parser.add_argument("--list", action="store_true", help="List available feeds")
    parser.add_argument("--api-key", help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)")
    parser.add_argument("--enrich", action="store_true", help="Use Claude API to enrich the feed content")
    parser.add_argument("--output-dir", default="player_feeds", help="Directory to save player-compatible feeds")
    
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
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Update output files to use the output directory
    for feed in config["feeds"]:
        # Make sure all feeds save to the output directory
        feed_name = sanitize_id(feed['name'])
        feed['output_file'] = f"{args.output_dir}/{feed_name}.json"
    
    # Process specific feed if requested
    if args.feed:
        for feed in config["feeds"]:
            if feed["name"] == args.feed:
                process_feed(feed, player_format=not args.enrich)
                return
        print(f"ERROR: Feed '{args.feed}' not found in configuration.")
        return
    
    # Process all feeds
    success_count = 0
    for feed in config["feeds"]:
        success = process_feed(feed, player_format=not args.enrich)
        if success:
            success_count += 1
        print("\n" + "-"*50 + "\n")
    
    print(f"Processed {success_count}/{len(config['feeds'])} feeds successfully.")
    print(f"Player-compatible feeds saved to {args.output_dir}/")
    print(f"\nTo use these feeds in 'Did you hear that?' player:")
    print(f"1. Host these JSON files on a server with CORS enabled")
    print(f"2. Add the URL to your hosted JSON file in the player")


if __name__ == "__main__":
    main() 