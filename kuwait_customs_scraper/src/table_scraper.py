import time
import json
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class KuwaitCustomsTableScraper:
    def __init__(self, output_dir="data", headless=False):
        self.base_url = "https://www.customs.gov.kw"
        self.search_url = f"{self.base_url}/HSCode/HsCode"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()
        self.setup_driver(headless)
        self.data = []

    def setup_logging(self):
        log_file = self.output_dir / f"test_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self, headless):
        options = Options()
        if headless:
            options.add_argument('--headless')
        
        # Set Firefox preferences
        options.set_preference('intl.accept_languages', 'en-US, en')
        options.set_preference('javascript.enabled', True)
        options.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/120.0')
        
        options.binary_location = '/usr/bin/firefox-esr'
        
        service = Service('/usr/local/bin/geckodriver')
        self.driver = webdriver.Firefox(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)

    def extract_data_from_table(self):
        """Extract data from the current page's table"""
        try:
            # Wait for table to be present
            table = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table")))
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            page_data = []
            for row in rows[1:]:  # Skip header
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 4:  # Make sure we have all columns
                    # The first column might contain a button, get the code from the link
                    code_link = cols[0].find_element(By.TAG_NAME, "a")
                    href = code_link.get_attribute("href")
                    hts_code = href.split("DataSearch=")[-1] if href else ""
                    
                    item = {
                        'hts_code': hts_code,
                        'duty_rate': cols[1].text.strip(),
                        'description': cols[2].text.strip(),
                        'unit': cols[3].text.strip() if len(cols) > 3 else ''
                    }
                    page_data.append(item)
                    self.logger.info(f"Found HTS code: {item['hts_code']}")
            
            return page_data
        except Exception as e:
            self.logger.error(f"Error extracting table data: {str(e)}")
            return []

    def get_total_pages(self):
        """Get the total number of pages from pagination"""
        try:
            pagination = self.driver.find_element(By.CLASS_NAME, "pagination-container")
            last_page_link = pagination.find_element(By.CLASS_NAME, "PagedList-skipToLast")
            href = last_page_link.find_element(By.TAG_NAME, "a").get_attribute("href")
            return int(href.split("page=")[-1])
        except Exception as e:
            self.logger.error(f"Error getting total pages: {str(e)}")
            return 0

    def go_to_page(self, page_num):
        """Navigate to a specific page"""
        try:
            url = f"{self.search_url}/PageFilter?page={page_num}"
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to page {page_num}: {str(e)}")
            return False

    def save_progress(self):
        """Save the current data to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"kuwait_customs_data_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Progress saved to {output_file}")

    def scrape_all_pages(self):
        """Scrape data from all pages"""
        try:
            # Load initial page
            self.logger.info("Loading first page...")
            self.driver.get(self.search_url)
            time.sleep(5)

            # Get total pages
            total_pages = self.get_total_pages()
            self.logger.info(f"Found {total_pages} pages to scrape")

            # Scrape each page
            for page in range(1, total_pages + 1):
                self.logger.info(f"Processing page {page} of {total_pages}")
                
                if page > 1:
                    if not self.go_to_page(page):
                        continue

                # Extract data from current page
                page_data = self.extract_data_from_table()
                self.data.extend(page_data)
                
                # Save progress every 10 pages
                if page % 10 == 0:
                    self.save_progress()
                    self.logger.info(f"Processed {len(self.data)} items so far")

            # Final save
            self.save_progress()
            self.logger.info(f"Scraping completed. Total items: {len(self.data)}")

        except Exception as e:
            self.logger.error(f"Error in scrape_all_pages: {str(e)}")
            self.save_progress()  # Save whatever we have
            raise
        finally:
            self.close()

    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    try:
        # Initialize the scraper
        scraper = KuwaitCustomsTableScraper(headless=False)
        
        # Start the scraping process
        scraper.scrape_all_pages()
        
    except Exception as e:
        logging.error(f"Main script error: {str(e)}")
        raise

if __name__ == "__main__":
    main()