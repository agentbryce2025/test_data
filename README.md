# Modern Trade News Scraper

A Python scraper that collects trade-related news from Reuters and Global Trade Alert using Playwright for robust web scraping.

## Features

- Uses Playwright for reliable web automation
- Works on any system architecture (Windows, macOS, Linux)
- Multiple fallback methods for finding content
- Automatic scrolling to load more content
- Comprehensive error handling and logging
- Deduplication of articles

## Requirements

1. Python 3.7+
2. Playwright and its dependencies

## Installation

1. Install Python requirements:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

## Usage

```bash
python modern_scraper.py
```

This will create a `trade_news.json` file containing:
- Recent Reuters articles about tariffs and trade
- Recent Global Trade Alert announcements

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
            "source": "Reuters",
            "category": "tariffs"
        }
    ],
    "gta_announcements": [
        {
            "title": "Announcement Title",
            "date": "2025-02-24",
            "description": "Announcement description",
            "source": "Global Trade Alert",
            "url": "https://www.globaltradealert.org/latest"
        }
    ]
}
```

## Troubleshooting

If the scraper fails:
1. Check your internet connection
2. Make sure Playwright is installed correctly:
   ```bash
   playwright install
   ```
3. Check the logs for detailed error messages
4. Try running without headless mode by changing `headless=True` to `headless=False`
5. Increase wait times if content isn't loading fast enough

## Notes

- The scraper uses Playwright to handle modern web pages
- Implements automatic scrolling to load more content
- Includes comprehensive error handling and logging
- Works across all major operating systems and architectures
