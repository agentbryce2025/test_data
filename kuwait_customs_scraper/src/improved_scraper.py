import time
import json
import os
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class KuwaitCustomsScraper:
    def __init__(self):
        self.url = "https://www.customs.gov.kw/HSCode/HsCode"
        self.options = uc.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--lang=ar')  # Set language to Arabic
        
    def setup_driver(self):
        self.driver = uc.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def close_driver(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            
    def wait_and_find_element(self, by, value, timeout=10):
        """Wait for element to be present and return it"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def safe_click(self, element, retries=3):
        """Attempt to click an element safely with retries"""
        for i in range(retries):
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                element.click()
                return True
            except ElementClickInterceptedException:
                if i == retries - 1:
                    raise
                time.sleep(1)
        return False

    def get_hts_data(self):
        try:
            self.setup_driver()
            self.driver.get(self.url)
            logging.info("Navigated to website")
            
            # Wait for page to load
            time.sleep(5)
            
            # Find and fill the search fields
            section = self.wait_and_find_element(By.ID, "section")
            section.send_keys("1")  # Start with section 1
            
            chapter = self.wait_and_find_element(By.ID, "chapter")
            chapter.send_keys("01")  # Start with chapter 01
            
            search_button = self.wait_and_find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            
            time.sleep(2)
            
            all_data = []
            
            # Process search results
            while True:
                try:
                    # Find table rows
                    rows = self.wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
                    )
                    
                    for row in rows:
                        try:
                            columns = row.find_elements(By.TAG_NAME, "td")
                            if len(columns) >= 4:
                                data = {
                                    "hts_code": columns[0].text.strip(),
                                    "description": columns[1].text.strip(),
                                    "duty_rate": columns[2].text.strip(),
                                    "unit": columns[3].text.strip()
                                }
                                all_data.append(data)
                                logging.info(f"Extracted data for HTS code: {data['hts_code']}")
                        except Exception as e:
                            logging.error(f"Error processing row: {str(e)}")
                            continue
                    
                    # Try to find and click next page button
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Next page']")
                        if "disabled" in next_button.get_attribute("class"):
                            break
                        self.safe_click(next_button)
                        time.sleep(2)
                    except NoSuchElementException:
                        break
                        
                except Exception as e:
                    logging.error(f"Error processing page: {str(e)}")
                    break
            
            return all_data
            
        except Exception as e:
            logging.error(f"Major error: {str(e)}")
            return []
            
        finally:
            self.close_driver()
            
    def save_data(self, data, filename):
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Data saved to {filepath}")
            
def main():
    scraper = KuwaitCustomsScraper()
    data = scraper.get_hts_data()
    if data:
        scraper.save_data(data, 'kuwait_hts_data.json')
        logging.info(f"Successfully scraped {len(data)} records")
    else:
        logging.error("No data was scraped")

if __name__ == "__main__":
    main()