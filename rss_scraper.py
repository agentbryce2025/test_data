import feedparser
import requests
from datetime import datetime, timedelta
import json
import logging
import time
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RSSNewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def clean_html(self, html_text):
        """Remove HTML tags and clean up text"""
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, 'html.parser')
        return ' '.join(soup.get_text().split())
        
    def is_trade_related(self, text):
        """Check if text contains trade-related keywords"""
        keywords = ['trade', 'tariff', 'import', 'export', 'customs', 'duty',
                   'wto', 'trade war', 'trade dispute', 'trade agreement']
        text = text.lower()
        return any(keyword in text for keyword in keywords)
        
    def get_reuters_articles(self):
        """Get articles from Reuters RSS feeds"""
        articles = []
        try:
            logger.info("Starting Reuters RSS scraper...")
            
            # Reuters RSS feeds
            feeds = [
                'https://www.reuters.com/rssfeed/business',
                'https://www.reuters.com/rssfeed/markets',
                'https://www.reuters.com/rssfeed/world'
            ]
            
            one_week_ago = datetime.now() - timedelta(days=7)
            
            for feed_url in feeds:
                try:
                    logger.info(f"Fetching feed: {feed_url}")
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries:
                        try:
                            # Get date
                            date = datetime(*entry.published_parsed[:6])
                            if date < one_week_ago:
                                continue
                                
                            # Clean and check content
                            title = self.clean_html(entry.title)
                            description = self.clean_html(entry.description)
                            combined_text = f"{title} {description}"
                            
                            if self.is_trade_related(combined_text):
                                article = {
                                    "title": title,
                                    "url": entry.link,
                                    "date": date.isoformat(),
                                    "description": description,
                                    "source": "Reuters"
                                }
                                
                                if article not in articles:
                                    articles.append(article)
                                    logger.info(f"Added article: {title}")
                                    
                        except Exception as e:
                            logger.error(f"Error processing Reuters entry: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error with Reuters feed {feed_url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in Reuters RSS scraper: {e}")
            
        return articles
        
    def get_gta_data(self):
        """Get data from GTA website"""
        announcements = []
        try:
            logger.info("Starting GTA scraper...")
            
            # Try GTA search page
            search_url = "https://www.globaltradealert.org/search"
            
            # Get past week's date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            params = {
                'selected_date_from': start_date.strftime('%Y-%m-%d'),
                'selected_date_to': end_date.strftime('%Y-%m-%d'),
                'type': 'state_act'
            }
            
            try:
                response = requests.get(search_url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Save response for debugging
                    with open('gta_search.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                        
                    # Try different selectors for results
                    for result in soup.select('.search-result, .intervention-item, .state-act'):
                        try:
                            # Get title
                            title_elem = result.select_one('h3, h4, .title')
                            if not title_elem:
                                continue
                                
                            title = title_elem.get_text().strip()
                            
                            # Get date
                            date_elem = result.select_one('.date, time')
                            date = date_elem.get_text().strip() if date_elem else end_date.strftime('%Y-%m-%d')
                            
                            # Get description
                            desc_elem = result.select_one('p, .description')
                            description = desc_elem.get_text().strip() if desc_elem else ""
                            
                            announcement = {
                                "title": title,
                                "date": date,
                                "description": description,
                                "source": "Global Trade Alert"
                            }
                            
                            if announcement not in announcements:
                                announcements.append(announcement)
                                logger.info(f"Added announcement: {title}")
                                
                        except Exception as e:
                            logger.error(f"Error processing GTA result: {e}")
                            continue
                            
            except Exception as e:
                logger.error(f"Error with GTA search: {e}")
                
        except Exception as e:
            logger.error(f"Error in GTA scraper: {e}")
            
        return announcements
        
    def run(self):
        """Run the complete scraping process"""
        try:
            # Get Reuters articles
            reuters_articles = self.get_reuters_articles()
            logger.info(f"Found {len(reuters_articles)} Reuters articles")
            
            # Get GTA announcements
            gta_announcements = self.get_gta_data()
            logger.info(f"Found {len(gta_announcements)} GTA announcements")
            
            # Combine results
            results = {
                "timestamp": datetime.now().isoformat(),
                "reuters_articles": reuters_articles,
                "gta_announcements": gta_announcements
            }
            
            # Save results
            with open('trade_news.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info("Results saved to trade_news.json")
            
        except Exception as e:
            logger.error(f"Error running scraper: {e}")

if __name__ == "__main__":
    scraper = RSSNewsScraper()
    scraper.run()
