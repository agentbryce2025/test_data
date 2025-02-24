from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import json
import logging
import time
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        
    def setup(self):
        """Initialize Playwright"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=['--disable-web-security', '--disable-features=IsolateOrigins']
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
    def cleanup(self):
        """Clean up Playwright resources"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
    def wait_for_content(self, page):
        """Wait for dynamic content to load"""
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(5000)  # Wait additional 5 seconds
        
    def scroll_page(self, page):
        """Scroll the page to load dynamic content"""
        for _ in range(3):
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(2000)
            
    def extract_date(self, text):
        """Extract date from various formats"""
        patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',  # ISO format
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # 1 Jan 2024
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}'  # Jan 1, 2024
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return datetime.now().strftime('%Y-%m-%d')
            
    def get_reuters_articles(self):
        """Get articles from Reuters"""
        articles = []
        try:
            logger.info("Starting Reuters scraper...")
            page = self.context.new_page()
            
            # Try different Reuters URLs
            urls = [
                "https://www.reuters.com/markets/global/",
                "https://www.reuters.com/business/",
                "https://www.reuters.com/markets/us/"
            ]
            
            for url in urls:
                logger.info(f"Trying URL: {url}")
                page.goto(url)
                self.wait_for_content(page)
                self.scroll_page(page)
                
                # Save the current state for debugging
                page.screenshot(path=f"reuters_{url.split('/')[-2]}.png")
                
                # Try different selectors
                selectors = [
                    "xpath=//div[contains(@class, 'media-story-card') or contains(@class, 'story-card')]",
                    "xpath=//article",
                    "xpath=//*[contains(@class, 'article-card')]",
                    "xpath=//*[@data-testid='Heading']/ancestor::div[contains(@class, 'story')]"
                ]
                
                for selector in selectors:
                    try:
                        elements = page.locator(selector).all()
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            try:
                                # Extract title and link
                                title = element.locator("xpath=.//*[self::h3 or self::h4]").first.inner_text().strip()
                                link = element.locator("a").first.get_attribute("href")
                                if link and not link.startswith("http"):
                                    link = f"https://www.reuters.com{link}"
                                
                                # Extract date
                                date_text = element.locator("time").first.inner_text()
                                date = self.extract_date(date_text)
                                
                                # Extract description
                                try:
                                    description = element.locator("p").first.inner_text().strip()
                                except:
                                    description = ""
                                
                                # Check if it's trade related
                                keywords = ['trade', 'tariff', 'import', 'export', 'customs', 'duty']
                                text = f"{title} {description}".lower()
                                if any(keyword in text for keyword in keywords):
                                    article = {
                                        "title": title,
                                        "url": link,
                                        "date": date,
                                        "description": description,
                                        "source": "Reuters"
                                    }
                                    
                                    if article not in articles:
                                        articles.append(article)
                                        logger.info(f"Added article: {title}")
                                        
                            except Exception as e:
                                logger.debug(f"Error processing article element: {e}")
                                continue
                                
                    except Exception as e:
                        logger.debug(f"Error with selector {selector}: {e}")
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
            
            # Try the main page
            page.goto("https://www.globaltradealert.org")
            self.wait_for_content(page)
            self.scroll_page(page)
            
            # Save the current state
            page.screenshot(path="gta_main.png")
            
            # Try different selectors
            selectors = [
                "xpath=//*[contains(@class, 'report-card')]",
                "xpath=//*[contains(@class, 'intervention')]",
                "xpath=//*[contains(@class, 'update-card')]",
                "xpath=//*[contains(@class, 'announcement')]"
            ]
            
            for selector in selectors:
                try:
                    elements = page.locator(selector).all()
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements:
                        try:
                            # Get title
                            title = element.locator("xpath=.//*[self::h3 or self::h4 or contains(@class, 'title')]").first.inner_text().strip()
                            
                            # Get date
                            try:
                                date_text = element.locator("xpath=.//*[contains(@class, 'date') or self::time]").first.inner_text()
                                date = self.extract_date(date_text)
                            except:
                                date = datetime.now().strftime('%Y-%m-%d')
                            
                            # Get description
                            try:
                                description = element.locator("p").first.inner_text().strip()
                            except:
                                description = ""
                            
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
                            logger.debug(f"Error processing GTA element: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error with GTA selector {selector}: {e}")
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
    scraper = AdvancedScraper()
    scraper.run()
