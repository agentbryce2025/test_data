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

class TestChapterScraper:
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
        
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.binary_location = '/usr/bin/firefox-esr'
        
        service = Service('/usr/local/bin/geckodriver')
        self.driver = webdriver.Firefox(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)
        
        # Set English language cookie
        self.driver.get(self.base_url)
        self.driver.add_cookie({
            'name': 'language',
            'value': 'en',
            'path': '/',
            'domain': '.customs.gov.kw'
        })

    def wait_and_find_element(self, by, value, timeout=30):
        """Wait for and find an element"""
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def scrape_chapter(self, section_id="1", chapter_id="01"):
        """Scrape a specific chapter"""
        try:
            # Load the page
            self.logger.info("Loading search page...")
            self.driver.get(self.search_url)
            
            # Wait for page to load and check for errors
            time.sleep(5)
            
            # Log the page title and any error messages
            self.logger.info(f"Page title: {self.driver.title}")
            self.logger.info(f"Current URL: {self.driver.current_url}")
            
            # Take screenshot before any actions
            self.driver.save_screenshot("before_action.png")
            self.logger.info("Saved initial screenshot")

            # Try to find the section dropdown using various methods
            # Analyze page content
            self.logger.info("Analyzing page content...")
            
            # Get all elements
            elements = self.driver.find_elements(By.XPATH, "//*")
            self.logger.info(f"Total elements on page: {len(elements)}")
            
            # Look for form elements
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            self.logger.info(f"Found {len(forms)} form elements")
            for form in forms:
                self.logger.info(f"Form ID: {form.get_attribute('id')}")
                self.logger.info(f"Form Action: {form.get_attribute('action')}")
            
            # Look for select elements with any ID
            selects = self.driver.find_elements(By.XPATH, "//select[@id]")
            self.logger.info(f"Found {len(selects)} select elements with IDs")
            for select in selects:
                self.logger.info(f"Select ID: {select.get_attribute('id')}")
            
            # Look for elements with 'section' in their ID or name
            section_elements = self.driver.find_elements(
                By.XPATH, 
                "//*[contains(@id, 'section') or contains(@id, 'Section') or contains(@name, 'section') or contains(@name, 'Section')]"
            )
            self.logger.info(f"Found {len(section_elements)} elements related to sections")
            for elem in section_elements:
                self.logger.info(f"Section element - Tag: {elem.tag_name}, ID: {elem.get_attribute('id')}, Name: {elem.get_attribute('name')}")
            
            # Get the page source for analysis
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            self.logger.info("Saved page source for analysis")
            
            # Take a screenshot
            self.driver.save_screenshot("page_analysis.png")
            
            # Try to find the section dropdown
            try:
                section_select = self.driver.find_element(By.ID, "SectionID")
                self.logger.info("Found section dropdown by ID")
            except:
                raise Exception("Could not find section dropdown after analysis")

            # Print current selected value
            self.logger.info(f"Current section value: {section_select.get_attribute('value')}")
            
            # Try to change the value
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                section_select, section_id
            )
            time.sleep(2)

            # Take screenshot after action
            self.driver.save_screenshot("after_action.png")
            self.logger.info("Saved action screenshot")

            # Select chapter
            self.logger.info(f"Selecting chapter {chapter_id}...")
            chapter_select = self.wait_and_find_element(By.ID, "ChapterID")
            chapter_select.send_keys(chapter_id)
            time.sleep(2)

            # Click search
            self.logger.info("Clicking search button...")
            search_button = self.wait_and_find_element(By.ID, "btnSearch")
            search_button.click()
            time.sleep(3)

            # Get results
            self.logger.info("Getting results...")
            results_table = self.wait_and_find_element(By.ID, "dataTable")
            rows = results_table.find_elements(By.TAG_NAME, "tr")
            
            # Skip header row
            for row in rows[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    data = {
                        'hts_code': cols[0].text.strip(),
                        'description': cols[1].text.strip(),
                        'duty_rate': cols[2].text.strip() if len(cols) > 2 else '',
                        'unit': cols[3].text.strip() if len(cols) > 3 else ''
                    }
                    self.data.append(data)
                    self.logger.info(f"Found HTS code: {data['hts_code']}")

            # Save results
            self.save_results()

        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            raise
        finally:
            self.close()

    def save_results(self):
        """Save the results to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"test_chapter_data_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Results saved to {output_file}")

    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    try:
        # Initialize the scraper
        scraper = TestChapterScraper(headless=False)
        
        # Scrape chapter 1 from section 1
        scraper.scrape_chapter(section_id="1", chapter_id="01")
        
    except Exception as e:
        logging.error(f"Main script error: {str(e)}")
        raise

if __name__ == "__main__":
    main()