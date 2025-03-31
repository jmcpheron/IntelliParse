# IntelliParse Examples

This directory contains example files to demonstrate the input and output formats for IntelliParse.

## Directory Structure

- `output/`: Contains sample output files

## Sample Files

### Raw Episodes Data

The file `output/raw_episodes_sample.json` shows the format of the raw episode data extracted from podcast RSS feeds using the `feedparser` library. This is the intermediate data format before it's processed by Claude.

Each episode contains:
- `id`: Unique identifier for the episode
- `title`: Episode title
- `date`: Publication date
- `summary`: Episode description or summary
- `source_feed`: Name of the podcast feed
- `media_url`: URL to the audio file
- `duration`: Episode duration (if available)

### Enriched Output

The file `output/mock_enriched_feed.json` demonstrates the enriched JSON output after processing by Claude. This is the format that's compatible with simple media players.

The enriched output contains:
- A curated feed with AI-selected episodes
- Enhanced descriptions and summaries
- Technical elements extracted from the content
- Content density ratings
- User preference matching
- Custom insights explaining why each episode might be interesting

## Using These Examples

You can use these examples as references for:
1. Understanding the data format at each stage of processing
2. Testing your own modifications to the IntelliParse code
3. Building compatible media players that can consume the output format
4. Customizing the prompt or output format to meet your specific needs

To generate your own output in the same format, run:

```bash
# Test with mock data
python test_with_mock.py

# Test with real podcast feeds
python test_real_feeds.py

# Process a subset of episodes
python process_subset.py
``` 