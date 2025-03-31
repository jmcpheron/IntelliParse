# JMcPheron's AI & Media Feed

This is a personalized feed for JMcPheron, focused on content at the intersection of artificial intelligence, media production, and creative technology.

## What's in This Feed

This feed demonstrates how IntelliParse can be used to create highly personalized media collections based on specific interests. The content is curated from:

- Lex Fridman Podcast
- The TWIML AI Podcast

Content is filtered and enriched based on JMcPheron's specific interests:
- Artificial intelligence
- Machine learning
- Entertainment technology
- Media production
- Creative technology
- Technology ethics

## Files

- `jmcpheron_ai_media_feed.json`: The enriched feed with AI-selected episodes
- `raw_episodes.json`: The raw episode data before AI processing

## Special Features

The JMcPheron feed includes custom enrichments:

1. **Content curation**: Episodes selected specifically for relevance to JMcPheron's interests
2. **Enhanced descriptions**: Rewritten to highlight the aspects most relevant to AI and media
3. **Technical elements**: Important concepts in each episode with relevance scores
4. **JMcPheron relevance**: Custom explanations of why each episode would be interesting to JMcPheron

## Creating Your Own Personal Feed

You can use this as a template for creating your own personalized feed:

1. Modify the `jmcpheron_interests` list in `create_jmcpheron_feed.py` with your own interests
2. Add or change the podcast feed URLs
3. Customize the filtering keywords
4. Run the script with your Anthropic API key

```bash
python create_jmcpheron_feed.py
```

The output will be saved to `examples/jmcpheron/jmcpheron_ai_media_feed.json` and can be used with any media player that supports the IntelliParse JSON format.

## Why This Matters

This personalized feed demonstrates the power of AI to cut through the noise and deliver exactly the content that aligns with your specific interests. Rather than browsing through hundreds of episodes manually, IntelliParse can identify the most relevant content and enhance it with insights specific to your needs. 