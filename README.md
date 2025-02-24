# Trade News Scraper

A Python scraper that collects trade-related news from the World Trade Organization (WTO) website.

## Background

This scraper was developed after finding that Reuters and Global Trade Alert websites have implemented strong anti-scraping measures. Instead, it focuses on the WTO website, which provides reliable trade-related news and announcements.

## Alternative Data Sources

For Reuters and GTA data, consider:

1. Official APIs:
   - Reuters Connect API: https://www.reutersagency.com/en/products/reuters-connect/
   - Contact GTA for API access

2. News Aggregator APIs:
   - NewsAPI.org
   - Google News API
   - Event Registry API

3. Other Trade Sources:
   - Government trade websites
   - Trade policy monitoring organizations
   - International trade organizations

## Features

- Scrapes WTO news and announcements
- Automatic date parsing for various formats
- Filters for content from the last 7 days
- URL normalization
- Comprehensive error handling
- Detailed logging

## Requirements

- Python 3.7+
- Required packages: requests, beautifulsoup4

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python wto_scraper.py
```

This will:
1. Fetch recent news from WTO website
2. Filter for content from the last 7 days
3. Save results to `trade_news.json`

## Output Format

```json
{
    "timestamp": "2025-02-24T10:00:00.000000",
    "wto_news": [
        {
            "title": "News Title",
            "url": "News URL",
            "date": "2025-02-24",
            "description": "News description",
            "source": "WTO"
        }
    ]
}
```

## Next Steps

To get comprehensive trade news coverage, consider:

1. Registering for official APIs:
   - Reuters Connect
   - NewsAPI.org
   - Event Registry

2. Adding more sources:
   - UNCTAD (United Nations Conference on Trade and Development)
   - National trade ministry websites
   - Regional trade organization websites

3. Setting up automated monitoring:
   - Email notifications for new items
   - Database storage for historical tracking
   - API endpoint for data access

## Notes

- The current implementation focuses on WTO news
- Additional sources can be added as needed
- Consider API-based solutions for Reuters and GTA data
