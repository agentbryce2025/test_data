import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import json
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UndetectedScraper:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Initialize undetected-chromedriver"""
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = uc.Chrome(options=options)
        self.driver.set_page_load_timeout(30)
        
    def wait_and_get_elements(self, selector, selector_type=By.CSS_SELECTOR, timeout=10):
        """Wait for elements to be present and return them"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((selector_type, selector))
            )
            return self.driver.find_elements(selector_type, selector)
        except:
            return []
            
    def scroll_page(self):
        """Scroll the page to load dynamic content"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
    def get_reuters_articles(self):
        """Get articles from Reuters"""
        articles = []
        try:
            logger.info("Starting Reuters scraper...")
            urls = [
                "https://www.reuters.com/business/",
                "https://www.reuters.com/markets/",
                "https://www.reuters.com/business/finance/"
            ]
            
            for url in urls:
                try:
                    logger.info(f"Accessing {url}")
                    self.driver.get(url)
                    time.sleep(5)  # Wait for initial load
                    
                    # Scroll to load more content
                    self.scroll_page()
                    
                    # Try different selectors for articles
                    selectors = [
                        "article",
                        "div[data-testid='story-card']",
                        ".story-card",
                        ".media-story-card"
                    ]
                    
                    for selector in selectors:
                        elements = self.wait_and_get_elements(selector)
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            try:
                                # Get title and link
                                title_elem = element.find_element(By.CSS_SELECTOR, "h3, h4")
                                title = title_elem.text.strip()
                                link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                                
                                # Get date
                                try:
                                    date = element.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                                except:
                                    date = datetime.now().isoformat()
                                
                                # Get description
                                try:
                                    description = element.find_element(By.TAG_NAME, "p").text.strip()
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
                                logger.debug(f"Error processing article: {e}")
                                continue
                                
                        if articles:  # If we found articles, break the selector loop
                            break
                            
                except Exception as e:
                    logger.error(f"Error with URL {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in Reuters scraper: {e}")
            
        return articles
        
    def get_gta_data(self):
        """Get data from Global Trade Alert"""
        announcements = []
        try:
            logger.info("Starting GTA scraper...")
            urls = [
                "https://www.globaltradealert.org/latest",
                "https://www.globaltradealert.org/interventions"
            ]
            
            for url in urls:
                try:
                    logger.info(f"Accessing {url}")
                    self.driver.get(url)
                    time.sleep(5)  # Wait for initial load
                    
                    # Scroll to load more content
                    self.scroll_page()
                    
                    # Try different selectors for announcements
                    selectors = [
                        ".intervention-item",
                        ".measure-card",
                        ".announcement",
                        "tr.state-act"
                    ]
                    
                    for selector in selectors:
                        elements = self.wait_and_get_elements(selector)
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            try:
                                # Get title
                                title = element.find_element(By.CSS_SELECTOR, "h3, h4, .title").text.strip()
                                
                                # Get date
                                try:
                                    date = element.find_element(By.CSS_SELECTOR, ".date, time").text.strip()
                                except:
                                    date = datetime.now().strftime("%Y-%m-%d")
                                
                                # Get description
                                try:
                                    description = element.find_element(By.CSS_SELECTOR, "p, .description").text.strip()
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
                                logger.debug(f"Error processing announcement: {e}")
                                continue
                                
                        if announcements:  # If we found announcements, break the selector loop
                            break
                            
                except Exception as e:
                    logger.error(f"Error with URL {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in GTA scraper: {e}")
            
        return announcements
        
    def run(self):
        """Run the complete scraping process"""
        try:
            # Initialize the driver
            self.setup_driver()
            
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
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    scraper = UndetectedScraper()
    scraper.run()
