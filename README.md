# Trade News Scrapers

This repository contains scripts to scrape trade-related news and announcements from:
- Reuters (Business/Tariffs section)
- Global Trade Alert

## Requirements

Install the required packages:
```bash
pip install -r requirements.txt
```

You'll also need Firefox and geckodriver installed:
```bash
# For Ubuntu/Debian:
sudo apt-get install firefox-esr firefox-geckodriver
```

## Usage

### Reuters Scraper
```bash
python reuters_scraper.py
```
This will create a `reuters_articles.json` file with the last week's articles.

### Global Trade Alert Scraper
```bash
python gta_scraper.py
```
This will create a `gta_announcements.json` file with the last week's announcements.

## Output Format

The scrapers output JSON files with the following structure:

### Reuters Articles
```json
[
    {
        "title": "Article Title",
        "url": "Article URL",
        "date": "2025-02-24T10:00:00Z",
        "source": "Reuters"
    }
]
```

### Global Trade Alert Announcements
```json
[
    {
        "title": "Announcement Title",
        "date": "2025-02-24",
        "source": "Global Trade Alert"
    }
]
```
