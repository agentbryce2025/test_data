# Undetected Trade News Scraper

A Python scraper that uses undetected-chromedriver to bypass anti-bot measures and collect trade-related news from Reuters and Global Trade Alert.

## Features

- Uses undetected-chromedriver to bypass detection
- Automatic scrolling to load dynamic content
- Multiple selectors for resilient scraping
- Trade-related keyword filtering
- Comprehensive error handling
- Detailed logging

## Requirements

1. Python 3.7+
2. Chrome browser
3. Required packages: undetected-chromedriver, selenium

## Installation

1. Install Chrome browser if not already installed:
```bash
# On macOS:
brew install --cask google-chrome

# On Ubuntu:
sudo apt-get install google-chrome-stable

# On Windows:
# Download and install Chrome from https://www.google.com/chrome/
```

2. Install Python requirements:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python undetected_scraper.py
```

This will:
1. Launch an undetected Chrome instance
2. Scrape Reuters for trade-related articles
3. Scrape Global Trade Alert for announcements
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
            "source": "Global Trade Alert"
        }
    ]
}
```

## Troubleshooting

If the scraper fails:
1. Try without headless mode (remove the `--headless` option)
2. Increase wait times between actions
3. Check if Chrome is up to date
4. Look for error messages in the logs
5. Verify your internet connection

## Notes

- Uses undetected-chromedriver to bypass anti-bot measures
- Implements multiple fallback selectors
- Includes trade-related keyword filtering
- Handles dynamic page loading
