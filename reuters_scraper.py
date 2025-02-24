import feedparser
from datetime import datetime, timedelta
import json
import time

class ReutersScraper:
    def __init__(self):
        self.feed_url = "https://www.reuters.com/rss/businessNews"

    def get_last_week_articles(self):
        print("Fetching Reuters RSS feed...")
        feed = feedparser.parse(self.feed_url)
        articles = []
        
        one_week_ago = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries:
            try:
                # Parse the publication date
                pub_date = datetime(*entry.published_parsed[:6])
                
                if pub_date >= one_week_ago:
                    # Check if the article is related to tariffs/trade
                    if any(keyword in entry.title.lower() or keyword in entry.description.lower() 
                           for keyword in ['tariff', 'trade', 'import', 'export', 'duty', 'customs']):
                        articles.append({
                            "title": entry.title,
                            "url": entry.link,
                            "date": entry.published,
                            "description": entry.description,
                            "source": "Reuters"
                        })
                        print(f"Found relevant article: {entry.title}")
            except Exception as e:
                print(f"Error processing entry: {e}")
                continue
                
        return articles

    def save_to_json(self, articles, filename="reuters_articles.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(articles)} articles to {filename}")

def main():
    scraper = ReutersScraper()
    articles = scraper.get_last_week_articles()
    scraper.save_to_json(articles)

if __name__ == "__main__":
    main()
