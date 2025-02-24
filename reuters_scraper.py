from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import json
import time

class ReutersScraper:
    def __init__(self):
        self.url = "https://www.reuters.com/business/tariffs/"
        self.options = Options()
        self.options.add_argument('--headless')
        self.driver = None

    def setup_driver(self):
        service = Service('geckodriver')
        self.driver = webdriver.Firefox(service=service, options=self.options)

    def get_last_week_articles(self):
        self.setup_driver()
        articles = []
        try:
            self.driver.get(self.url)
            # Wait for articles to load
            time.sleep(5)
            
            # Find all article elements
            article_elements = self.driver.find_elements(By.CSS_SELECTOR, "article")
            
            one_week_ago = datetime.now() - timedelta(days=7)
            
            for article in article_elements:
                try:
                    # Extract article information
                    title = article.find_element(By.CSS_SELECTOR, "h3").text
                    link = article.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    try:
                        date_element = article.find_element(By.CSS_SELECTOR, "time")
                        date_str = date_element.get_attribute("datetime")
                        article_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                    except:
                        continue
                        
                    if article_date >= one_week_ago:
                        articles.append({
                            "title": title,
                            "url": link,
                            "date": date_str,
                            "source": "Reuters"
                        })
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Reuters: {e}")
        finally:
            self.driver.quit()
            
        return articles

    def save_to_json(self, articles, filename="reuters_articles.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)

def main():
    scraper = ReutersScraper()
    articles = scraper.get_last_week_articles()
    scraper.save_to_json(articles)

if __name__ == "__main__":
    main()
