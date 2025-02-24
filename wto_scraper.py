import requests
from datetime import datetime, timedelta
import json
import logging
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WTOScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.base_url = "https://www.wto.org"
        
    def parse_date(self, date_text):
        """Parse WTO date formats"""
        date_text = date_text.strip()
        patterns = [
            (r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
             '%d %B %Y'),
            (r'(\d{4})-(\d{2})-(\d{2})',
             '%Y-%m-%d')
        ]
        
        for pattern, fmt in patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    return datetime.strptime(match.group(0), fmt)
                except ValueError:
                    continue
        return None
        
    def get_wto_news(self):
        """Get news from WTO website"""
        news_items = []
        try:
            logger.info("Starting WTO news scraper...")
            
            # Try different WTO news pages
            urls = [
                "/english/news_e/news_e.htm",
                "/english/news_e/archive_e.htm",
                "/english/tratop_e/tratop_e.htm"
            ]
            
            one_week_ago = datetime.now() - timedelta(days=7)
            
            for url_path in urls:
                try:
                    url = f"{self.base_url}{url_path}"
                    logger.info(f"Fetching: {url}")
                    
                    response = requests.get(url, headers=self.headers)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Try different news item selectors
                        for item in soup.select('.newsitem, .listitem, tr'):
                            try:
                                # Get date
                                date_elem = item.select_one('.date, .newsdate, td:first-child')
                                if not date_elem:
                                    continue
                                    
                                date = self.parse_date(date_elem.text)
                                if not date or date < one_week_ago:
                                    continue
                                
                                # Get title and link
                                title_elem = item.select_one('a, .newstitle, td a')
                                if not title_elem:
                                    continue
                                    
                                title = title_elem.text.strip()
                                link = title_elem.get('href', '')
                                if link and not link.startswith('http'):
                                    link = f"{self.base_url}{link}"
                                
                                # Get description
                                desc_elem = item.select_one('.description, .summary, td:nth-child(2)')
                                description = desc_elem.text.strip() if desc_elem else ""
                                
                                news_item = {
                                    "title": title,
                                    "url": link,
                                    "date": date.strftime('%Y-%m-%d'),
                                    "description": description,
                                    "source": "WTO"
                                }
                                
                                if news_item not in news_items:
                                    news_items.append(news_item)
                                    logger.info(f"Added news item: {title}")
                                    
                            except Exception as e:
                                logger.error(f"Error processing WTO news item: {e}")
                                continue
                                
                except Exception as e:
                    logger.error(f"Error with WTO URL {url_path}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in WTO scraper: {e}")
            
        return news_items
        
    def run(self):
        """Run the scraper"""
        try:
            # Get WTO news
            wto_news = self.get_wto_news()
            logger.info(f"Found {len(wto_news)} WTO news items")
            
            # Save results
            results = {
                "timestamp": datetime.now().isoformat(),
                "wto_news": wto_news
            }
            
            with open('trade_news.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info("Results saved to trade_news.json")
            
        except Exception as e:
            logger.error(f"Error running scraper: {e}")

if __name__ == "__main__":
    scraper = WTOScraper()
    scraper.run()
