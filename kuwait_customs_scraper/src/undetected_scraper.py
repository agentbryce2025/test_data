import time
import json
import logging
from datetime import datetime
from pathlib import Path
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class KuwaitCustomsUndetectedScraper:
    def __init__(self, output_dir="data", headless=True):
        self.base_url = "https://www.customs.gov.kw"
        self.search_url = f"{self.base_url}/HSCode/HsCode"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()
        self.setup_driver(headless)
        self.data = []

    def setup_logging(self):
        log_file = self.output_dir / f"scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        
        # Add language preference
        options.add_argument('--lang=en-US')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def get_sections(self):
        """Get all available sections"""
        try:
            # First load the page
            self.driver.get(self.search_url)
            time.sleep(2)  # Wait for page to load

            # Get sections from dropdown
            section_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "SectionID"))
            )
            options = section_select.find_elements(By.TAG_NAME, "option")
            sections = []
            
            for option in options[1:]:  # Skip first empty option
                sections.append({
                    'value': option.get_attribute('value'),
                    'text': option.text.strip()
                })
                
            self.logger.info(f"Found {len(sections)} sections")
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
                    'text': option.text.strip()
                })
            return subheadings
        except Exception as e:
            self.logger.error(f"Error getting subheadings for heading {heading_id}: {str(e)}")
            return []

    def search_and_get_results(self):
        """Get results from the current search"""
        try:
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
                        'hts_code': cols[0].text.strip(),
                        'description': cols[1].text.strip(),
                        'duty_rate': cols[2].text.strip() if len(cols) > 2 else '',
                        'unit': cols[3].text.strip() if len(cols) > 3 else ''
                    })
            return results
        except Exception as e:
            self.logger.error(f"Error getting search results: {str(e)}")
            return []

    def save_progress(self):
        """Save current progress to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"kuwait_customs_data_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Progress saved to {output_file}")

    def scrape_all_codes(self):
        """Scrape all HTS codes with their duty rates and units"""
        try:
            # Load the initial page
            self.driver.get(self.search_url)
            time.sleep(2)

            sections = self.get_sections()
            self.logger.info(f"Found {len(sections)} sections")
            
            for section in sections:
                section_id = section['value']
                self.logger.info(f"Processing section {section_id}")
                
                chapters = self.get_chapters(section_id)
                for chapter in chapters:
                    chapter_id = chapter['value']
                    self.logger.info(f"Processing chapter {chapter_id}")
                    
                    headings = self.get_headings(section_id, chapter_id)
                    for heading in headings:
                        heading_id = heading['value']
                        self.logger.info(f"Processing heading {heading_id}")
                        
                        subheadings = self.get_subheadings(section_id, chapter_id, heading_id)
                        if subheadings:
                            for subheading in subheadings:
                                subheading_id = subheading['value']
                                
                                # Fill the form
                                self.driver.find_element(By.ID, "SectionID").send_keys(section_id)
                                time.sleep(0.5)
                                self.driver.find_element(By.ID, "ChapterID").send_keys(chapter_id)
                                time.sleep(0.5)
                                self.driver.find_element(By.ID, "HeadingID").send_keys(heading_id)
                                time.sleep(0.5)
                                self.driver.find_element(By.ID, "SubHeadingID").send_keys(subheading_id)
                                time.sleep(0.5)
                                
                                results = self.search_and_get_results()
                                self.data.extend(results)
                                time.sleep(1)  # Be nice to the server
                                
                                # Refresh the page to clear form
                                self.driver.get(self.search_url)
                                time.sleep(1)
                        else:
                            # Fill the form without subheading
                            self.driver.find_element(By.ID, "SectionID").send_keys(section_id)
                            time.sleep(0.5)
                            self.driver.find_element(By.ID, "ChapterID").send_keys(chapter_id)
                            time.sleep(0.5)
                            self.driver.find_element(By.ID, "HeadingID").send_keys(heading_id)
                            time.sleep(0.5)
                            
                            results = self.search_and_get_results()
                            self.data.extend(results)
                            time.sleep(1)
                            
                            # Refresh the page to clear form
                            self.driver.get(self.search_url)
                            time.sleep(1)
                        
                        # Save progress periodically
                        if len(self.data) % 100 == 0:
                            self.save_progress()
                
                # Save progress after each section
                self.save_progress()
                
        except Exception as e:
            self.logger.error(f"Error in scrape_all_codes: {str(e)}")
            self.save_progress()  # Save whatever we have
            raise
        finally:
            self.close()

    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()