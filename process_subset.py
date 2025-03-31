#!/usr/bin/env python3
"""
Process a small subset of podcast episodes to make testing more manageable.
"""

import os
import json
import random
from dotenv import load_dotenv
from intelliparse import IntelliParse

# Load environment variables from .env file
load_dotenv()

def main():
    """Process a subset of the episodes."""
    print("Processing a subset of podcast episodes...")
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Anthropic API key not set. Please add it to your .env file.")
        return
    
    # Load the raw episodes data
    try:
        with open("sample_output/raw_episodes.json", "r") as f:
            all_episodes = json.load(f)
    except FileNotFoundError:
        print("ERROR: raw_episodes.json not found. Please run test_real_feeds.py first.")
        return
    
    # Take a small random sample (5 episodes)
    print(f"Total episodes available: {len(all_episodes)}")
    sample_size = 5
    episode_sample = random.sample(all_episodes, min(sample_size, len(all_episodes)))
    
    print(f"Selected {len(episode_sample)} random episodes for processing.")
    
    # Display the selected episodes
    print("\nSelected episodes:")
    for i, episode in enumerate(episode_sample, 1):
        print(f"{i}. {episode['title']} ({episode['source_feed']})")
    
    # Create a custom IntelliParse class that uses our sample instead of fetching
    class SubsetIntelliParse(IntelliParse):
        def parse_feeds(self):
            """Return the sample episodes instead of parsing feeds."""
            print("Using sample of episodes...")
            return episode_sample
    
    # Define user interests
    user_interests = [
        "ai_hobbies",
        "web_accessibility",
        "bobsburgers", 
        "3d_printing",
        "retro_gaming",
        "open_source_hardware"
    ]
    
    # Initialize with empty feeds (will be ignored)
    parser = SubsetIntelliParse(feeds=[], user_interests=user_interests)
    
    try:
        print("\nProcessing with Claude API...")
        result = parser.process()
        output_file = "sample_output/subset_output.json"
        parser.save_output(result, output_file)
        
        print(f"Successfully processed subset. Output saved to {output_file}")
        
        # Print a summary
        if "feeds" in result and len(result["feeds"]) > 0:
            feed = result["feeds"][0]
            print(f"\nCreated feed: {feed['title']}")
            print(f"Total tracks: {len(feed['tracks'])}")
            print("\nTracks:")
            for i, track in enumerate(feed["tracks"], 1):
                print(f"{i}. {track['title']}")
                if "intelliparse_enrichment" in track and "intelliparse_insight" in track["intelliparse_enrichment"]:
                    print(f"   Insight: {track['intelliparse_enrichment']['intelliparse_insight']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 