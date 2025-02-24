# Advanced Trade News Scraper

A sophisticated Python scraper that collects trade-related news from Reuters and Global Trade Alert using modern web automation techniques.

## Features

- Advanced web automation using Playwright
- Multiple fallback methods for finding content
- Intelligent date extraction from various formats
- Keyword-based filtering for trade-related content
- Comprehensive error handling and logging
- Screenshot capture for debugging
- Deduplication of content

## Requirements

1. Python 3.7+
2. Playwright and its dependencies

## Installation

1. Run the setup script:
```bash
./setup.sh
```

Or manually:

1. Install Python requirements:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

```bash
python advanced_scraper.py
```

This will:
1. Scrape Reuters for trade-related articles
2. Scrape Global Trade Alert for announcements
3. Save results to `trade_news.json`
4. Save debug screenshots for troubleshooting

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

The scraper saves several debug files:
- `reuters_*.png`: Screenshots of Reuters pages
- `gta_main.png`: Screenshot of GTA homepage
- Log output with detailed information

## Troubleshooting

If the scraper fails:
1. Check the debug screenshots
2. Look for error messages in the log output
3. Try running without headless mode by changing `headless=True` to `headless=False`
4. Increase wait times if content isn't loading
5. Check if the website structure has changed

## Notes

- The scraper uses advanced selectors to find content
- Implements intelligent date parsing
- Filters content based on trade-related keywords
- Handles dynamic web pages with proper waiting
