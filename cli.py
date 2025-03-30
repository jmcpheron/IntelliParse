#!/usr/bin/env python3
import argparse
import json
import os
from dotenv import load_dotenv
from intelliparse import IntelliParse

# Load environment variables from .env file if present
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="IntelliParse - Convert podcast RSS feeds to enriched JSON"
    )
    
    parser.add_argument(
        "-f", "--feeds",
        nargs="+",
        help="List of podcast RSS feed URLs",
        required=True
    )
    
    parser.add_argument(
        "-i", "--interests",
        nargs="+",
        help="List of user interest tags",
        default=[]
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file path",
        default="intelliparse_output.json"
    )
    
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (can also be set via ANTHROPIC_API_KEY env var)"
    )
    
    return parser.parse_args()

def main():
    """Run IntelliParse from command line arguments."""
    args = parse_args()
    
    # Set API key from args if provided
    if args.api_key:
        os.environ["ANTHROPIC_API_KEY"] = args.api_key
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Anthropic API key not provided. Set with --api-key or ANTHROPIC_API_KEY env var.")
        exit(1)
    
    # Initialize IntelliParse
    parser = IntelliParse(feeds=args.feeds, user_interests=args.interests)
    
    try:
        print(f"Processing {len(args.feeds)} feeds...")
        result = parser.process()
        parser.save_output(result, args.output)
        print(f"Successfully processed feeds. Output saved to {args.output}")
        
        # Print a summary
        if "feeds" in result and len(result["feeds"]) > 0:
            feed = result["feeds"][0]
            print(f"\nCreated feed: {feed['title']}")
            print(f"Total tracks: {len(feed['tracks'])}")
            print("\nTracks:")
            for i, track in enumerate(feed["tracks"], 1):
                print(f"{i}. {track['title']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 