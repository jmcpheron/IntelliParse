#!/usr/bin/env python3
"""
Test script for IntelliParse using mock data.
This allows testing the basic functionality without real API calls.
"""

import json
import os
from intelliparse import IntelliParse

# Mock episode data to simulate feedparser results
MOCK_EPISODES = [
    {
        "id": "ep1",
        "title": "The Future of AI for Hobbyists",
        "date": "2023-05-15T12:00:00Z",
        "summary": "In this episode, we discuss how artificial intelligence is becoming more accessible to hobbyists and makers. We cover open source tools, affordable hardware options, and creative projects anyone can try at home with basic skills.",
        "source_feed": "Tech Hobbyist Podcast",
        "media_url": "https://example.com/podcasts/tech-hobbyist/ep1.mp3",
        "duration": "45:30"
    },
    {
        "id": "ep2",
        "title": "Web Accessibility Best Practices in 2023",
        "date": "2023-06-01T14:30:00Z",
        "summary": "We discuss the latest web accessibility standards and how developers can ensure their websites are usable by everyone. Topics include ARIA roles, keyboard navigation, color contrast, and testing tools.",
        "source_feed": "Web Dev Weekly",
        "media_url": "https://example.com/podcasts/webdev/ep45.mp3",
        "duration": "38:15"
    },
    {
        "id": "ep3",
        "title": "Bob's Burgers Season Finale Review",
        "date": "2023-05-28T18:45:00Z",
        "summary": "A detailed discussion of the latest Bob's Burgers season finale. We analyze the character development, plot twists, and favorite moments from the Belcher family's latest adventures.",
        "source_feed": "Animation Nation",
        "media_url": "https://example.com/podcasts/animation/ep67.mp3",
        "duration": "52:10"
    },
    {
        "id": "ep4",
        "title": "Budget 3D Printers Comparison",
        "date": "2023-06-10T09:15:00Z",
        "summary": "We compare the top five budget 3D printers under $300, discussing print quality, reliability, features, and which one provides the best value for beginners and hobbyists.",
        "source_feed": "Maker Movement",
        "media_url": "https://example.com/podcasts/maker/ep33.mp3",
        "duration": "61:45"
    },
    {
        "id": "ep5",
        "title": "Retro Gaming Preservation",
        "date": "2023-05-20T15:00:00Z",
        "summary": "How enthusiasts and organizations are working to preserve classic video games and hardware. We explore emulation, ROM libraries, hardware restoration, and the legal challenges facing preservation efforts.",
        "source_feed": "Retro Game Club",
        "media_url": "https://example.com/podcasts/retrogames/ep88.mp3",
        "duration": "48:20"
    }
]

# Mock Claude API response to simulate AI processing
MOCK_CLAUDE_RESPONSE = {
    "feeds": [
        {
            "id": "intelliparse-curated",
            "title": "IntelliParse Curated Feed",
            "tracks": [
                {
                    "id": "ep1",
                    "title": "The Future of AI for Hobbyists",
                    "description": "Exploration of accessible AI tools and projects for hobbyists and makers, with emphasis on open source solutions and affordable hardware options.",
                    "audioUrl": "https://example.com/podcasts/tech-hobbyist/ep1.mp3",
                    "date_iso": "2023-05-15T12:00:00Z",
                    "runtime_minutes": 45.5,
                    "intelliparse_enrichment": {
                        "precision_summary": "This episode covers how AI is becoming more accessible to hobbyists through open source tools and affordable hardware, with practical project suggestions for beginners.",
                        "technical_elements": [
                            {"concept": "open source AI", "relevance": 0.9},
                            {"concept": "maker projects", "relevance": 0.8},
                            {"concept": "DIY artificial intelligence", "relevance": 0.7}
                        ],
                        "content_density": "HIGH",
                        "confidence_score": 0.95,
                        "preference_match": True,
                        "intelliparse_insight": "Directly matches user's ai_hobbies interest and has crossover with open_source_hardware"
                    }
                },
                {
                    "id": "ep2",
                    "title": "Web Accessibility Best Practices in 2023",
                    "description": "Comprehensive guide to implementing web accessibility standards, including ARIA roles, keyboard navigation, and color contrast best practices.",
                    "audioUrl": "https://example.com/podcasts/webdev/ep45.mp3",
                    "date_iso": "2023-06-01T14:30:00Z",
                    "runtime_minutes": 38.25,
                    "intelliparse_enrichment": {
                        "precision_summary": "A practical guide to implementing current web accessibility standards, covering ARIA roles, keyboard navigation, and testing methodologies.",
                        "technical_elements": [
                            {"concept": "ARIA roles", "relevance": 0.9},
                            {"concept": "keyboard navigation", "relevance": 0.8},
                            {"concept": "color contrast", "relevance": 0.7}
                        ],
                        "content_density": "HIGH",
                        "confidence_score": 0.9,
                        "preference_match": True,
                        "intelliparse_insight": "Directly aligns with user's web_accessibility interest"
                    }
                },
                {
                    "id": "ep4",
                    "title": "Budget 3D Printers Comparison",
                    "description": "Detailed analysis of five sub-$300 3D printers, evaluating print quality, reliability, and feature sets for hobbyist use.",
                    "audioUrl": "https://example.com/podcasts/maker/ep33.mp3",
                    "date_iso": "2023-06-10T09:15:00Z",
                    "runtime_minutes": 61.75,
                    "intelliparse_enrichment": {
                        "precision_summary": "Comprehensive comparison of five budget 3D printers under $300, analyzing print quality, build volume, and which models offer the best value for beginners.",
                        "technical_elements": [
                            {"concept": "FDM printing", "relevance": 0.8},
                            {"concept": "print quality metrics", "relevance": 0.7},
                            {"concept": "budget hardware", "relevance": 0.9}
                        ],
                        "content_density": "MEDIUM",
                        "confidence_score": 0.85,
                        "preference_match": True,
                        "intelliparse_insight": "Matches user's 3d_printing interest with practical buying advice"
                    }
                }
            ]
        }
    ]
}

class MockIntelliParse(IntelliParse):
    """Modified IntelliParse that uses mock data instead of real APIs."""
    
    def parse_feeds(self):
        """Return mock episode data instead of parsing real feeds."""
        print("Using mock feed data...")
        return MOCK_EPISODES
    
    def call_claude_api(self, prompt):
        """Return mock Claude API response instead of making a real API call."""
        print("Using mock Claude API response...")
        return MOCK_CLAUDE_RESPONSE


def main():
    """Run the mock test."""
    print("Starting IntelliParse mock test...")
    
    # Example user interests from README
    user_interests = [
        "ai_hobbies",
        "web_accessibility",
        "bobsburgers", 
        "3d_printing",
        "retro_gaming",
        "open_source_hardware"
    ]
    
    # Initialize the mock parser with empty feeds (will be ignored)
    parser = MockIntelliParse(feeds=[], user_interests=user_interests)
    
    try:
        # Process the mock data
        result = parser.process()
        
        # Save output to a file
        output_file = "mock_test_output.json"
        parser.save_output(result, output_file)
        
        print(f"\nSuccessfully processed mock data. Output saved to {output_file}")
        
        # Print a summary
        if "feeds" in result and len(result["feeds"]) > 0:
            feed = result["feeds"][0]
            print(f"\nCreated feed: {feed['title']}")
            print(f"Total tracks: {len(feed['tracks'])}")
            print("\nTracks:")
            for i, track in enumerate(feed["tracks"], 1):
                print(f"{i}. {track['title']}")
                print(f"   Match: {track['intelliparse_enrichment']['intelliparse_insight']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 