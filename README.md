# Trade News RSS Scraper

A Python scraper that collects trade-related news from Reuters RSS feeds and Global Trade Alert search results.

## Features

- Uses Reuters RSS feeds for reliable article access
- Searches GTA website for recent announcements
- Automatic filtering for trade-related content
- Date-based filtering for last week's content
- HTML cleaning and text normalization
- Comprehensive error handling and logging

## Requirements

- Python 3.7+
- Required packages: feedparser, requests, beautifulsoup4, python-dateutil

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python rss_scraper.py
```

This will:
1. Fetch articles from Reuters RSS feeds
2. Search GTA website for recent announcements
3. Filter for trade-related content
4. Save results to `trade_news.json`

## Trade-Related Keywords

The scraper looks for content containing:
- trade
- tariff
- import
- export
- customs
- duty
- wto
- trade war
- trade dispute
- trade agreement

## Output Format

```json
{
    "timestamp": "2025-02-24T10:00:00.000000",
    "reuters_articles": [
        {
            "title": "Article Title",
            "url": "Article URL",
            "date": "2025-02-24T10:00:00Z",
            "description": "Article description",
            "source": "Reuters"
        }
    ],
    "gta_announcements": [
        {
            "title": "Announcement Title",
            "date": "2025-02-24",
            "description": "Announcement description",
            "source": "Global Trade Alert"
        }
    ]
}
```

## Debugging

The scraper saves:
- GTA search results in `gta_search.html`
- Detailed log output

## Error Handling

The scraper includes:
- Multiple RSS feed attempts
- HTML cleaning and normalization
- Comprehensive error logging
- Data validation and filtering

## Notes

- Uses RSS feeds for more reliable access
- Implements text cleaning and normalization
- Filters content based on trade-related keywords
- Ensures content is from the last 7 days
