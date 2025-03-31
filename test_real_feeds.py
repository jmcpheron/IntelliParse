#!/usr/bin/env python3
"""
Test script for IntelliParse using real podcast RSS feeds.
Note: This requires a valid Anthropic API key in your .env file.
"""

import os
import json
from dotenv import load_dotenv
from intelliparse import IntelliParse

# Load environment variables from .env file
load_dotenv()

def main():
    """Run IntelliParse with real podcast feeds."""
    print("Starting IntelliParse with real podcast feeds...")
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Anthropic API key not set. Please add it to your .env file.")
        return
    
    # Define feeds to parse
    feeds = [
        "https://lexfridman.com/feed/podcast/",       # Lex Fridman Podcast
        "https://feeds.megaphone.fm/MLN2155636147",   # AI Podcast by NVIDIA
    ]
    
    # Define user interests (from README)
    user_interests = [
        "ai_hobbies",
        "web_accessibility",
        "bobsburgers", 
        "3d_printing",
        "retro_gaming",
        "open_source_hardware"
    ]
    
    # Initialize IntelliParse
    parser = IntelliParse(feeds=feeds, user_interests=user_interests)
    
    try:
        print(f"Fetching and parsing {len(feeds)} feeds...")
        
        # First, just fetch the episodes without calling Claude
        episodes = parser.parse_feeds()
        print(f"Successfully fetched {len(episodes)} episodes.")
        
        # Save raw episodes to a file for reference
        with open("sample_output/raw_episodes.json", "w") as f:
            json.dump(episodes, f, indent=2)
        print("Saved raw episode data to sample_output/raw_episodes.json")
        
        # Display the first few episodes
        print("\nSample episodes:")
        for i, episode in enumerate(episodes[:3], 1):
            print(f"{i}. {episode['title']} ({episode['source_feed']})")
        
        # Now process the complete pipeline if the PROCESS_FULL env var is set
        if os.environ.get("PROCESS_FULL", "").lower() in ("true", "1", "yes"):
            print("\nProcessing complete pipeline including Claude API...")
            result = parser.process()
            parser.save_output(result, "sample_output/intelliparse_output.json")
            
            # Print a summary
            if "feeds" in result and len(result["feeds"]) > 0:
                feed = result["feeds"][0]
                print(f"\nCreated feed: {feed['title']}")
                print(f"Total tracks: {len(feed['tracks'])}")
                print("\nSample tracks:")
                for i, track in enumerate(feed["tracks"][:3], 1):
                    print(f"{i}. {track['title']}")
                    if "intelliparse_enrichment" in track and "intelliparse_insight" in track["intelliparse_enrichment"]:
                        print(f"   Insight: {track['intelliparse_enrichment']['intelliparse_insight']}")
        else:
            print("\nSkipping Claude API processing. Set PROCESS_FULL=true to process with Claude.")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 