import undetected_chromedriver as uc
import time
import json
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class UndetectableKuwaitCustomsScraper:
    def __init__(self, headless=True):
        self.base_url = "https://www.customs.gov.kw"
        self.search_url = f"{self.base_url}/HSCode/HsCode"
        self.setup_logging()
        self.setup_driver(headless)
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self, headless):
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        
        # Additional options to make the scraper more robust
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=en-US')
        
        # Set up custom headers
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        
    def _wait_and_retry(self, locator, retries=3, delay=2):
        """Helper method to wait for element with retries"""
        for attempt in range(retries):
            try:
                return self.wait.until(EC.presence_of_element_located(locator))
            except TimeoutException:
                if attempt < retries - 1:
                    time.sleep(delay)
                    continue
                raise
                
    def start_session(self):
        """Initialize the scraping session"""
        try:
            self.driver.get(self.search_url)
            time.sleep(3)  # Initial longer wait to ensure page loads completely
            self.logger.info("Successfully loaded the search page")
        except Exception as e:
            self.logger.error(f"Error loading search page: {str(e)}")
            raise

    def get_sections(self):
        """Get all available sections from the dropdown"""
        try:
            section_dropdown = self._wait_and_retry((By.ID, "SectionID"))
            options = section_dropdown.find_elements(By.TAG_NAME, "option")
            sections = []
            for option in options[1:]:  # Skip the first empty option
                sections.append({
                    'value': option.get_attribute('value'),
                    'text': option.text.strip()
                })
            return sections
        except Exception as e:
            self.logger.error(f"Error getting sections: {str(e)}")
            return []

    def get_chapters(self, section_id):
        """Get chapters for a specific section"""
        try:
            # Select the section
            section_dropdown = self._wait_and_retry((By.ID, "SectionID"))
            section_dropdown.send_keys(section_id)
            time.sleep(2)  # Wait for AJAX

            # Get chapters
            chapter_dropdown = self._wait_and_retry((By.ID, "ChapterID"))
            options = chapter_dropdown.find_elements(By.TAG_NAME, "option")
            chapters = []
            for option in options[1:]:
                chapters.append({
                    'value': option.get_attribute('value'),
                    'text': option.text.strip()
                })
            return chapters
        except Exception as e:
            self.logger.error(f"Error getting chapters for section {section_id}: {str(e)}")
            return []

    def get_headings(self, section_id, chapter_id):
        """Get headings for a specific chapter"""
        try:
            # Select the section and chapter
            self.driver.find_element(By.ID, "SectionID").send_keys(section_id)
            time.sleep(2)
            self.driver.find_element(By.ID, "ChapterID").send_keys(chapter_id)
            time.sleep(2)

            # Get headings
            heading_dropdown = self._wait_and_retry((By.ID, "HeadingID"))
            options = heading_dropdown.find_elements(By.TAG_NAME, "option")
            headings = []
            for option in options[1:]:
                headings.append({
                    'value': option.get_attribute('value'),
                    'text': option.text.strip()
                })
            return headings
        except Exception as e:
            self.logger.error(f"Error getting headings for chapter {chapter_id}: {str(e)}")
            return []

    def get_subheadings(self, section_id, chapter_id, heading_id):
        """Get subheadings for a specific heading"""
        try:
            # Select the section, chapter, and heading
            self.driver.find_element(By.ID, "SectionID").send_keys(section_id)
            time.sleep(2)
            self.driver.find_element(By.ID, "ChapterID").send_keys(chapter_id)
            time.sleep(2)
            self.driver.find_element(By.ID, "HeadingID").send_keys(heading_id)
            time.sleep(2)

            # Get subheadings
            subheading_dropdown = self._wait_and_retry((By.ID, "SubHeadingID"))
            options = subheading_dropdown.find_elements(By.TAG_NAME, "option")
            subheadings = []
            for option in options[1:]:
                subheadings.append({
                    'value': option.get_attribute('value'),
                    'text': option.text.strip()
                })
            return subheadings
        except Exception as e:
            self.logger.error(f"Error getting subheadings for heading {heading_id}: {str(e)}")
            return []

    def parse_rate_and_unit(self, duty_rate_text):
        """Parse the duty rate text to extract rate and unit"""
        rate = ''
        unit = ''
        
        # Remove whitespace and normalize
        duty_rate_text = duty_rate_text.strip()
        
        # Common unit patterns
        unit_patterns = ['KG', 'kg', 'G', 'g', 'L', 'l', 'PCS', 'pcs', 'M', 'm', 'M2', 'm2', 'M3', 'm3']
        
        # Extract percentage if present
        if '%' in duty_rate_text:
            rate = duty_rate_text.split('%')[0].strip()
            unit = '%'
        else:
            # Check for known units
            for pattern in unit_patterns:
                if pattern.lower() in duty_rate_text.lower():
                    rate = duty_rate_text.split(pattern)[0].strip()
                    unit = pattern
                    break
            
            # If no unit found but there's a number
            if not unit and any(c.isdigit() for c in duty_rate_text):
                rate = duty_rate_text
                
        return rate, unit

    def search_and_get_results(self, section_id, chapter_id=None, heading_id=None, subheading_id=None):
        """Perform search and get results"""
        try:
            # Fill the form
            self.driver.find_element(By.ID, "SectionID").send_keys(section_id)
            if chapter_id:
                time.sleep(2)
                self.driver.find_element(By.ID, "ChapterID").send_keys(chapter_id)
            if heading_id:
                time.sleep(2)
                self.driver.find_element(By.ID, "HeadingID").send_keys(heading_id)
            if subheading_id:
                time.sleep(2)
                self.driver.find_element(By.ID, "SubHeadingID").send_keys(subheading_id)

            # Click search button
            search_button = self._wait_and_retry((By.ID, "btnSearch"))
            self.driver.execute_script("arguments[0].click();", search_button)
            time.sleep(3)

            # Get results table
            results_table = self._wait_and_retry((By.ID, "dataTable"))
            rows = results_table.find_elements(By.TAG_NAME, "tr")
            
            results = []
            for row in rows[1:]:  # Skip header row
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if cols:
                        duty_rate_text = cols[2].text.strip()
                        rate, unit = self.parse_rate_and_unit(duty_rate_text)
                        
                        results.append({
                            'hts_code': cols[0].text.strip(),
                            'description': cols[1].text.strip(),
                            'duty_rate': rate,
                            'unit': unit,
                            'raw_duty_text': duty_rate_text
                        })
                except StaleElementReferenceException:
                    continue
            return results
        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}")
            return []

    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()