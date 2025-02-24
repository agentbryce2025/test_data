# Trade News API Scraper

A Python scraper that collects trade-related news from Reuters and Global Trade Alert using their API endpoints.

## Features

- Uses official APIs where available
- Multiple fallback methods
- Automatic filtering for trade-related content
- Date-based filtering for last week's content
- Comprehensive error handling and logging
- Debug output for troubleshooting

## Requirements

- Python 3.7+
- Required packages: requests, python-dateutil

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python api_scraper.py
```

This will:
1. Fetch recent articles from Reuters API
2. Fetch announcements from GTA API
3. Filter for trade-related content
4. Save results to `trade_news.json`

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
            "implementing_country": "Country Name",
            "source": "Global Trade Alert"
        }
    ]
}
```

## Debugging

The scraper saves API responses for debugging:
- `reuters_api_*.json`: Reuters API responses
- `gta_api_*.json`: GTA API responses

## Error Handling

The scraper includes:
- Multiple API endpoint attempts
- Comprehensive error logging
- Graceful degradation if endpoints fail
- Data validation and filtering

## Notes

- Uses official APIs where available
- Implements multiple fallback methods
- Filters content based on trade-related keywords
- Ensures content is from the last 7 days
