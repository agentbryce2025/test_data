# Trade News Scraper

A Python scraper that collects trade-related news from Reuters and Global Trade Alert.

## Requirements

1. Python 3.7+
2. Firefox browser
3. Required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python run_scrapers.py
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
            "source": "Reuters"
        }
    ],
    "gta_announcements": [
        {
            "title": "Announcement Title",
            "implementing_country": "Country Name",
            "date": "2025-02-24",
            "description": "Announcement description",
            "source": "Global Trade Alert"
        }
    ]
}
```

## Troubleshooting

If the scraper fails:
1. Check your internet connection
2. Verify Firefox is installed
3. Check if the websites are accessible in your browser
4. Try running without headless mode for debugging
