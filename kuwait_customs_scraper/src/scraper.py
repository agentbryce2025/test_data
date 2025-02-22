import time
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

class KuwaitCustomsScraper:
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
        options = Options()
        if headless:
            options.add_argument('--headless')
        
        # Set up Firefox profile for English language
        options.set_preference('intl.accept_languages', 'en-US, en')
        
        self.driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 10)

    def start_session(self):
        """Initialize the scraping session"""
        try:
            self.driver.get(self.search_url)
            time.sleep(2)  # Allow page to load
            self.logger.info("Successfully loaded the search page")
        except Exception as e:
            self.logger.error(f"Error loading search page: {str(e)}")
            raise

    def get_sections(self):
        """Get all available sections from the dropdown"""
        try:
            section_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "SectionID"))
            )
            options = section_dropdown.find_elements(By.TAG_NAME, "option")
            sections = []
            for option in options[1:]:  # Skip the first empty option
                sections.append({
                    'value': option.get_attribute('value'),
                    'text': option.text
                })
            return sections
        except Exception as e:
            self.logger.error(f"Error getting sections: {str(e)}")
            return []

    def get_chapters(self, section_id):
        """Get chapters for a specific section"""
        try:
            # Select the section
            section_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "SectionID"))
            )
            section_dropdown.send_keys(section_id)
            time.sleep(1)  # Wait for AJAX

            # Get chapters
            chapter_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "ChapterID"))
            )
            options = chapter_dropdown.find_elements(By.TAG_NAME, "option")
            chapters = []
            for option in options[1:]:
                chapters.append({
                    'value': option.get_attribute('value'),
                    'text': option.text
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
            time.sleep(1)
            self.driver.find_element(By.ID, "ChapterID").send_keys(chapter_id)
            time.sleep(1)

            # Get headings
            heading_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "HeadingID"))
            )
            options = heading_dropdown.find_elements(By.TAG_NAME, "option")
            headings = []
            for option in options[1:]:
                headings.append({
                    'value': option.get_attribute('value'),
                    'text': option.text
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
            time.sleep(1)
            self.driver.find_element(By.ID, "ChapterID").send_keys(chapter_id)
            time.sleep(1)
            self.driver.find_element(By.ID, "HeadingID").send_keys(heading_id)
            time.sleep(1)

            # Get subheadings
            subheading_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "SubHeadingID"))
            )
            options = subheading_dropdown.find_elements(By.TAG_NAME, "option")
            subheadings = []
            for option in options[1:]:
                subheadings.append({
                    'value': option.get_attribute('value'),
                    'text': option.text
                })
            return subheadings
        except Exception as e:
            self.logger.error(f"Error getting subheadings for heading {heading_id}: {str(e)}")
            return []

    def search_and_get_results(self, section_id, chapter_id=None, heading_id=None, subheading_id=None):
        """Perform search and get results"""
        try:
            # Fill the form
            self.driver.find_element(By.ID, "SectionID").send_keys(section_id)
            if chapter_id:
                time.sleep(1)
                self.driver.find_element(By.ID, "ChapterID").send_keys(chapter_id)
            if heading_id:
                time.sleep(1)
                self.driver.find_element(By.ID, "HeadingID").send_keys(heading_id)
            if subheading_id:
                time.sleep(1)
                self.driver.find_element(By.ID, "SubHeadingID").send_keys(subheading_id)

            # Click search button
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "btnSearch"))
            )
            search_button.click()
            time.sleep(2)

            # Get results table
            results_table = self.wait.until(
                EC.presence_of_element_located((By.ID, "dataTable"))
            )
            rows = results_table.find_elements(By.TAG_NAME, "tr")
            
            results = []
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    results.append({
                        'hs_code': cols[0].text,
                        'description': cols[1].text,
                        'duty_rate': cols[2].text
                    })
            return results
        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}")
            return []

    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()