from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import json
import logging
import time
import asyncio
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        
    def setup(self):
        """Initialize Playwright"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
    def cleanup(self):
        """Clean up Playwright resources"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
    def get_reuters_articles(self):
        """Get articles from Reuters"""
        articles = []
        try:
            logger.info("Starting Reuters scraper...")
            page = self.context.new_page()
            
            # Try different Reuters URLs
            urls = [
                "https://www.reuters.com/business/tariffs/",
                "https://www.reuters.com/markets/commodities/",
                "https://www.reuters.com/business/trade/"
            ]
            
            for url in urls:
                logger.info(f"Trying URL: {url}")
                page.goto(url, wait_until='networkidle')
                page.wait_for_timeout(5000)  # Wait 5 seconds
                
                # Scroll down to load more content
                for _ in range(3):
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_timeout(2000)
                
                # Try different selectors
                selectors = [
                    "article",
                    "div[data-testid='story-card']",
                    ".story-card",
                    ".article"
                ]
                
                for selector in selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            try:
                                # Get title and link
                                title_element = element.query_selector("a h3, a h4")
                                if not title_element:
                                    continue
                                    
                                title = title_element.text_content().strip()
                                link = element.query_selector("a").get_attribute("href")
                                if link and not link.startswith("http"):
                                    link = f"https://www.reuters.com{link}"
                                
                                # Get date
                                date_element = element.query_selector("time")
                                date = date_element.get_attribute("datetime") if date_element else datetime.now().isoformat()
                                
                                # Get description
                                desc_element = element.query_selector("p")
                                description = desc_element.text_content().strip() if desc_element else ""
                                
                                if title and link:
                                    article = {
                                        "title": title,
                                        "url": link,
                                        "date": date,
                                        "description": description,
                                        "source": "Reuters",
                                        "category": url.split("/")[-2]
                                    }
                                    
                                    if article not in articles:
                                        articles.append(article)
                                        logger.info(f"Added article: {title}")
                                        
                            except Exception as e:
                                logger.error(f"Error processing article element: {e}")
                                continue
                                
                    except Exception as e:
                        logger.error(f"Error with selector {selector}: {e}")
                        continue
                        
                if articles:
                    break
                    
            page.close()
            
        except Exception as e:
            logger.error(f"Error in Reuters scraper: {e}")
            
        return articles
        
    def get_gta_data(self):
        """Get data from Global Trade Alert"""
        announcements = []
        try:
            logger.info("Starting GTA scraper...")
            page = self.context.new_page()
            
            # Try the activity tracker
            url = "https://www.globaltradealert.org/latest"
            logger.info(f"Accessing {url}")
            page.goto(url, wait_until='networkidle')
            page.wait_for_timeout(5000)
            
            # Try different selectors
            selectors = [
                ".intervention-item",
                ".state-act",
                ".measure-card",
                "tr.intervention"
            ]
            
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements:
                        try:
                            # Get title
                            title_element = element.query_selector("h3, h4, .title")
                            if not title_element:
                                continue
                                
                            title = title_element.text_content().strip()
                            
                            # Get date
                            date_element = element.query_selector("time, .date")
                            date = date_element.text_content().strip() if date_element else datetime.now().strftime("%Y-%m-%d")
                            
                            # Get description
                            desc_element = element.query_selector("p, .description")
                            description = desc_element.text_content().strip() if desc_element else ""
                            
                            announcement = {
                                "title": title,
                                "date": date,
                                "description": description,
                                "source": "Global Trade Alert",
                                "url": "https://www.globaltradealert.org/latest"
                            }
                            
                            if announcement not in announcements:
                                announcements.append(announcement)
                                logger.info(f"Added announcement: {title}")
                                
                        except Exception as e:
                            logger.error(f"Error processing GTA element: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error with GTA selector {selector}: {e}")
                    continue
                    
                if announcements:
                    break
                    
            page.close()
            
        except Exception as e:
            logger.error(f"Error in GTA scraper: {e}")
            
        return announcements
        
    def run(self):
        """Run the complete scraping process"""
        try:
            self.setup()
            
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
        finally:
            self.cleanup()

if __name__ == "__main__":
    scraper = NewsScraper()
    scraper.run()
