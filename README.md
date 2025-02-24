# Trade News Scrapers

This repository contains scripts to collect trade-related news and announcements from:
- Reuters Business News (via RSS feed)
- Global Trade Alert (via API)

## Features

- Collects news articles and announcements from the last 7 days
- Filters Reuters articles for trade-related content
- Outputs data in JSON format
- Combined scraper that aggregates data from both sources

## Requirements

Install the required packages:
```bash
pip install feedparser requests
```

## Usage

### Run individual scrapers:

```bash
# For Reuters articles
python reuters_scraper.py

# For Global Trade Alert announcements
python gta_scraper.py
```

### Run combined scraper:

```bash
python run_scrapers.py
```

This will create a `trade_news.json` file containing data from both sources.

## Output Format

The combined output JSON has the following structure:

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
            "title": "Intervention Title",
            "implementing_country": "Country Name",
            "announcement_date": "2025-02-24",
            "implementation_date": "2025-02-24",
            "description": "Intervention description",
            "source": "Global Trade Alert"
        }
    ]
}
```
