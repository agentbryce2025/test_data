from reuters_scraper import ReutersScraper
from gta_scraper import GTAScraper
import json
from datetime import datetime

def main():
    # Run Reuters scraper
    reuters = ReutersScraper()
    reuters_articles = reuters.get_last_week_articles()
    
    # Run GTA scraper
    gta = GTAScraper()
    gta_announcements = gta.get_last_week_announcements()
    
    # Combine results
    combined_data = {
        "timestamp": datetime.now().isoformat(),
        "reuters_articles": reuters_articles,
        "gta_announcements": gta_announcements
    }
    
    # Save combined results
    with open('trade_news.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4, ensure_ascii=False)
    print(f"Saved combined data with {len(reuters_articles)} Reuters articles and {len(gta_announcements)} GTA announcements")

if __name__ == "__main__":
    main()
