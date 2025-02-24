from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import requests
import json
import time
import platform
import os

class ReutersScraper:
    def __init__(self):
        self.url = "https://www.reuters.com/markets/tariffs"
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
        # Set Firefox binary location based on OS
        if platform.system() == 'Darwin':  # macOS
            firefox_paths = [
                '/Applications/Firefox.app/Contents/MacOS/firefox',
                os.path.expanduser('~/Applications/Firefox.app/Contents/MacOS/firefox')
            ]
            for path in firefox_paths:
                if os.path.exists(path):
                    self.options.binary_location = path
                    break
        elif platform.system() == 'Linux':
            self.options.binary_location = '/usr/bin/firefox-esr'
        # Windows will auto-detect Firefox location

    def get_articles(self):
        articles = []
        driver = None
        try:
            print("Starting Firefox webdriver...")
            driver = webdriver.Firefox(options=self.options)
            print(f"Accessing {self.url}...")
            driver.get(self.url)
            
            # Wait for articles to load
            print("Waiting for content to load...")
            time.sleep(5)
            
            # Find all article elements
            article_elements = driver.find_elements(By.TAG_NAME, "article")
            print(f"Found {len(article_elements)} potential articles")
            
            one_week_ago = datetime.now() - timedelta(days=7)
            
            for article in article_elements:
                try:
                    # Extract article information
                    title = article.find_element(By.CSS_SELECTOR, "h3, h4").text.strip()
                    link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    # Try to get date
                    try:
                        date_element = article.find_element(By.TAG_NAME, "time")
                        date_str = date_element.get_attribute("datetime")
                        if not date_str:
                            date_str = datetime.now().isoformat()
                    except:
                        date_str = datetime.now().isoformat()
                    
                    # Get description if available
                    try:
                        description = article.find_element(By.TAG_NAME, "p").text.strip()
                    except:
                        description = ""
                    
                    articles.append({
                        "title": title,
                        "url": link,
                        "date": date_str,
                        "description": description,
                        "source": "Reuters"
                    })
                    print(f"Added article: {title}")
                    
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in Reuters scraper: {e}")
        finally:
            if driver:
                driver.quit()
            
        return articles

class GTAScraper:
    def __init__(self):
        self.base_url = "https://www.globaltradealert.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }

    def get_announcements(self):
        announcements = []
        try:
            print("Fetching GTA data...")
            # Try to get the main page first to get any necessary cookies/tokens
            session = requests.Session()
            response = session.get(f"{self.base_url}/latest/state_acts", headers=self.headers)
            
            # Now try different endpoints
            endpoints = [
                '/latest/state_acts',
                '/interventions',
                '/data/interventions',
                '/api/v1/interventions'
            ]
            
            for endpoint in endpoints:
                try:
                    print(f"Trying endpoint: {endpoint}")
                    response = session.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        params={
                            'date_from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            'date_to': datetime.now().strftime('%Y-%m-%d'),
                            'format': 'json'
                        }
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if isinstance(data, list) and len(data) > 0:
                                for item in data:
                                    announcements.append({
                                        "title": item.get('title', ''),
                                        "implementing_country": item.get('implementing_jurisdiction', ''),
                                        "date": item.get('announcement_date', ''),
                                        "description": item.get('description', ''),
                                        "source": "Global Trade Alert"
                                    })
                                    print(f"Added announcement: {item.get('title', '')}")
                                break  # Found working endpoint
                        except:
                            continue
                except:
                    continue
                    
            if not announcements:
                print("Failed to get data from any endpoint")
                
        except Exception as e:
            print(f"Error in GTA scraper: {e}")
            
        return announcements

def main():
    # Run Reuters scraper
    reuters = ReutersScraper()
    reuters_articles = reuters.get_articles()
    
    # Run GTA scraper
    gta = GTAScraper()
    gta_announcements = gta.get_announcements()
    
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
