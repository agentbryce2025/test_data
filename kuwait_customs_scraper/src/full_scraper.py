import time
import json
import logging
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager

class KuwaitCustomsFullScraper:
    def __init__(self, headless=True, output_dir="data"):
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
        max_attempts = 3
        delay = 2
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Attempt {attempt + 1} to start Firefox")
                
                options = Options()
                if headless:
                    options.add_argument('--headless')
                
                # Create a fresh profile
                profile = webdriver.FirefoxProfile()
                
                # Set up Firefox profile preferences
                profile.set_preference('intl.accept_languages', 'en-US, en')
                profile.set_preference('javascript.enabled', True)
                profile.set_preference('dom.webdriver.enabled', False)
                profile.set_preference('useAutomationExtension', False)
                profile.set_preference('browser.download.folderList', 2)
                profile.set_preference('browser.link.open_newwindow', 3)
                
                options.profile = profile
                options.binary_location = '/usr/bin/firefox-esr'
                
                service = Service('/usr/local/bin/geckodriver')
                service.start()
                
                self.driver = webdriver.Firefox(
                    service=service,
                    options=options
                )
                
                # Set longer timeout for slow pages
                self.wait = WebDriverWait(self.driver, 30)
                self.driver.set_page_load_timeout(30)
                
                # Set window size and position
                self.driver.set_window_size(1280, 1024)
                self.driver.set_window_position(0, 0)
                
                # Test the browser by loading a simple page
                self.driver.get("about:blank")
                self.logger.info("Firefox started successfully")
                return
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Failed to start Firefox (attempt {attempt + 1}): {str(e)}")
                
                # Clean up if driver was created
                if hasattr(self, 'driver'):
                    try:
                        self.driver.quit()
                    except:
                        pass
                
                if attempt < max_attempts - 1:
                    time.sleep(delay * (attempt + 1))
                    continue
                else:
                    raise Exception(f"Failed to start Firefox after {max_attempts} attempts. Last error: {last_error}")

    def retry_function(self, func, max_retries=3, delay=2):
        """Retry a function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                time.sleep(delay * (2 ** attempt))

    def ensure_page_loaded(self, url, timeout=30):
        """Ensure page is loaded completely and all elements are available"""
        try:
            self.driver.get(url)
            
            # Wait for document ready state
            start_time = time.time()
            while time.time() - start_time < timeout:
                state = self.driver.execute_script('return document.readyState;')
                if state == 'complete':
                    # Additional check for key elements
                    try:
                        self.wait.until(EC.presence_of_element_located((By.ID, "SectionID")))
                        self.wait.until(EC.presence_of_element_located((By.ID, "ChapterID")))
                        self.wait.until(EC.presence_of_element_located((By.ID, "HeadingID")))
                        self.wait.until(EC.presence_of_element_located((By.ID, "btnSearch")))
                        self.logger.info("All key elements found on page")
                        return True
                    except Exception as e:
                        self.logger.warning(f"Key elements not found: {str(e)}")
                time.sleep(1)
            
            self.logger.error("Page load timeout")
            return False
        except Exception as e:
            self.logger.error(f"Error loading page {url}: {str(e)}")
            return False

    def get_element_text(self, element, selector):
        """Safely get text from an element"""
        try:
            return element.find_element(By.CSS_SELECTOR, selector).text.strip()
        except NoSuchElementException:
            return ""

    def save_progress(self):
        """Save current progress to a JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"kuwait_customs_data_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Progress saved to {output_file}")

    def extract_detailed_info(self, row):
        """Extract all information from a result row"""
        cols = row.find_elements(By.TAG_NAME, "td")
        if not cols:
            return None

        # The website structure shows these columns:
        # HS Code | Description | Duty Rate | Unit
        try:
            info = {
                'hts_code': cols[0].text.strip(),
                'description': cols[1].text.strip(),
                'duty_rate': cols[2].text.strip(),
                'unit': cols[3].text.strip() if len(cols) > 3 else '',
            }
            return info
        except Exception as e:
            self.logger.error(f"Error extracting row info: {str(e)}")
            return None

    def search_and_get_results(self, selection_dict):
        """Perform search with the given selections and get results"""
        try:
            # Fill the form with provided selections
            for field_id, value in selection_dict.items():
                if value:
                    self.wait.until(EC.presence_of_element_located((By.ID, field_id)))
                    self.driver.find_element(By.ID, field_id).send_keys(value)
                    time.sleep(1)  # Wait for AJAX

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
                result = self.extract_detailed_info(row)
                if result:
                    results.append(result)
            
            return results
        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}")
            return []

    def scrape_all_codes(self):
        """Scrape all HTS codes with their duty rates and units"""
        try:
            if not self.ensure_page_loaded(self.search_url):
                raise Exception("Failed to load search page")

            # Get all sections
            sections = self.get_sections()
            
            for section in sections:
                section_id = section['value']
                self.logger.info(f"Processing section {section_id}")
                
                # For each section, get chapters
                chapters = self.get_chapters(section_id)
                
                for chapter in chapters:
                    chapter_id = chapter['value']
                    self.logger.info(f"Processing chapter {chapter_id}")
                    
                    # For each chapter, get headings
                    headings = self.get_headings(section_id, chapter_id)
                    
                    for heading in headings:
                        heading_id = heading['value']
                        self.logger.info(f"Processing heading {heading_id}")
                        
                        # For each heading, get subheadings
                        subheadings = self.get_subheadings(section_id, chapter_id, heading_id)
                        
                        if subheadings:
                            for subheading in subheadings:
                                subheading_id = subheading['value']
                                selection_dict = {
                                    "SectionID": section_id,
                                    "ChapterID": chapter_id,
                                    "HeadingID": heading_id,
                                    "SubHeadingID": subheading_id
                                }
                                
                                results = self.search_and_get_results(selection_dict)
                                self.data.extend(results)
                                
                                # Save progress periodically
                                if len(self.data) % 100 == 0:
                                    self.save_progress()
                                    
                        else:
                            # If no subheadings, search with heading
                            selection_dict = {
                                "SectionID": section_id,
                                "ChapterID": chapter_id,
                                "HeadingID": heading_id
                            }
                            results = self.search_and_get_results(selection_dict)
                            self.data.extend(results)
                
                # Save progress after each section
                self.save_progress()
                
        except Exception as e:
            self.logger.error(f"Error in scrape_all_codes: {str(e)}")
            self.save_progress()  # Save whatever we have
            raise
        finally:
            self.close()

    def get_sections(self):
        """Get all available sections from the dropdown"""
        max_attempts = 3
        delay = 2
        
        for attempt in range(max_attempts):
            try:
                self.logger.info(f"Attempt {attempt + 1} to get sections")
                
                # Wait for dropdown to be both present and visible
                section_dropdown = self.wait.until(
                    EC.presence_of_element_located((By.ID, "SectionID"))
                )
                self.wait.until(
                    EC.visibility_of_element_located((By.ID, "SectionID"))
                )
                
                # Wait a bit for any dynamic content to load
                time.sleep(2)
                
                # Get options
                options = section_dropdown.find_elements(By.TAG_NAME, "option")
                
                if not options:
                    self.logger.warning("No options found in section dropdown")
                    if attempt < max_attempts - 1:
                        # Try refreshing the page
                        self.logger.info("Refreshing page...")
                        self.driver.refresh()
                        time.sleep(delay * (attempt + 1))
                        continue
                    else:
                        return []
                
                sections = []
                for option in options[1:]:  # Skip the first empty option
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    
                    if value and text:  # Only add if both value and text are non-empty
                        sections.append({
                            'value': value,
                            'text': text
                        })
                
                if sections:
                    self.logger.info(f"Successfully found {len(sections)} sections")
                    return sections
                else:
                    self.logger.warning("No valid sections found")
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
                        continue
                    
            except Exception as e:
                self.logger.error(f"Error getting sections (attempt {attempt + 1}): {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(delay * (attempt + 1))
                    continue
        
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

    def close(self):
        """Close the browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()