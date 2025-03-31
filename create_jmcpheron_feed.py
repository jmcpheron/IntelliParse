#!/usr/bin/env python3
"""
Create a custom JMcPheron feed focused on AI and entertainment content.
This demonstrates how IntelliParse can be used to create personalized content feeds.
"""

import os
import json
from dotenv import load_dotenv
from intelliparse import IntelliParse

# Load environment variables from .env file
load_dotenv()

def main():
    """Create a specialized JMcPheron feed."""
    print("Creating JMcPheron specialized feed...")
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Anthropic API key not set. Please add it to your .env file.")
        return
    
    # Define podcast feeds that align with JMcPheron's interests
    # Using Lex Fridman and TWIML AI Podcast as they have strong AI content
    feeds = [
        "https://lexfridman.com/feed/podcast/",           # Lex Fridman Podcast
        "https://feeds.megaphone.fm/MLN2155636147"        # TWIML AI Podcast
    ]
    
    # Define JMcPheron's specific interests
    jmcpheron_interests = [
        "artificial_intelligence",
        "machine_learning", 
        "entertainment_tech",
        "media_production",
        "creative_technology",
        "technology_ethics"
    ]
    
    print(f"Using interests: {', '.join(jmcpheron_interests)}")
    
    # Initialize IntelliParse with JMcPheron's preferences
    parser = IntelliParse(feeds=feeds, user_interests=jmcpheron_interests)
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs("examples/jmcpheron", exist_ok=True)
        
        # First, just fetch the episodes without calling Claude
        print("Fetching episodes from feeds...")
        episodes = parser.parse_feeds()
        
        # Save raw episodes to a file
        with open("examples/jmcpheron/raw_episodes.json", "w") as f:
            json.dump(episodes, f, indent=2)
        
        print(f"Fetched {len(episodes)} episodes")
        
        # Filter episodes to ones containing AI and media keywords (to reduce sample size)
        keywords = [
            "ai", "artificial intelligence", "machine learning", "deep learning",
            "neural network", "llm", "language model", "reinforcement learning",
            "creative", "media", "entertainment", "ethics", "future"
        ]
        
        filtered_episodes = []
        for episode in episodes:
            # Create string for search by combining title and summary
            searchable_text = f"{episode.get('title', '')} {episode.get('summary', '')}".lower()
            
            # Check if any keyword appears in the episode
            if any(keyword.lower() in searchable_text for keyword in keywords):
                filtered_episodes.append(episode)
        
        print(f"Filtered to {len(filtered_episodes)} relevant episodes")
        
        # Limit to 30 episodes max to be practical for API usage
        if len(filtered_episodes) > 30:
            print(f"Limiting to 30 episodes for processing")
            filtered_episodes = filtered_episodes[:30]
        
        # Create a custom IntelliParse class that uses our filtered episodes
        class JMcPheronIntelliParse(IntelliParse):
            def parse_feeds(self):
                """Return the filtered episodes instead of parsing feeds."""
                return filtered_episodes
                
            def create_claude_prompt(self, text_blob: str) -> str:
                """Create a custom prompt specifically for JMcPheron's feed."""
                interests_text = "\n- ".join(self.user_interests)
                
                prompt = f"""You are IntelliParse, an LLM agent that identifies relevant episodes from podcast feeds and returns JSON content for use in JMcPheron's personal media player.

This feed is being created specifically for JMcPheron, who is interested in:
- {interests_text}

JMcPheron is particularly interested in the intersection of AI with creative fields, media production, and ethical considerations.

Below is a mix of episodes from multiple podcast feeds. Extract the most relevant ones for JMcPheron and enhance them.

For each episode, provide:
1. A precise but engaging description that captures the key points
2. Technical elements and concepts covered with their relevance score
3. A short precision summary (1-3 sentences)
4. Why this might be interesting to JMcPheron specifically

Return structured JSON in this format:
{{
  "feeds": [
    {{
      "id": "jmcpheron-ai-media-feed",
      "title": "JMcPheron's AI & Media Feed",
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
            "jmcpheron_relevance": "Why this is specifically relevant to JMcPheron's interests"
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
        custom_parser = JMcPheronIntelliParse(feeds=[], user_interests=jmcpheron_interests)
        
        print("Processing with Claude API to create JMcPheron's personalized feed...")
        result = custom_parser.process()
        
        # Save the result
        output_file = "examples/jmcpheron/jmcpheron_ai_media_feed.json"
        custom_parser.save_output(result, output_file)
        
        print(f"Successfully created JMcPheron's feed. Output saved to {output_file}")
        
        # Print a summary
        if "feeds" in result and len(result["feeds"]) > 0:
            feed = result["feeds"][0]
            print(f"\nCreated feed: {feed['title']}")
            print(f"Total tracks: {len(feed['tracks'])}")
            print("\nSample tracks:")
            for i, track in enumerate(feed["tracks"][:5], 1):
                print(f"{i}. {track['title']}")
                if "intelliparse_enrichment" in track and "jmcpheron_relevance" in track["intelliparse_enrichment"]:
                    print(f"   Relevance: {track['intelliparse_enrichment']['jmcpheron_relevance']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 