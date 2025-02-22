import time
import json
import logging
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

class KuwaitCustomsBS4Scraper:
    def __init__(self, output_dir="data"):
        self.base_url = "https://www.customs.gov.kw"
        self.search_url = f"{self.base_url}/HSCode/HsCode"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.setup_logging()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Origin': 'https://www.customs.gov.kw',
            'Referer': 'https://www.customs.gov.kw/HSCode/HsCode'
        })
        self.data = []
        
        # Initialize session by visiting the main page
        self.init_session()

    def init_session(self):
        """Initialize session by visiting the main page"""
        try:
            response = self.session.get(self.search_url)
            if response.status_code == 200:
                self.logger.info("Successfully initialized session")
                # Extract any necessary tokens from the response if needed
            else:
                self.logger.error(f"Failed to initialize session. Status code: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error initializing session: {str(e)}")
            raise

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

    def get_sections(self):
        """Get all available sections"""
        try:
            # First try getting the sections from the HTML page
            response = self.session.get(self.search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            section_select = soup.find('select', {'id': 'SectionID'})
            sections = []
            
            if section_select:
                for option in section_select.find_all('option')[1:]:  # Skip first empty option
                    sections.append({
                        'value': option['value'],
                        'text': option.text.strip()
                    })
            
            # If no sections found in HTML, try the API
            if not sections:
                self.logger.info("No sections found in HTML, trying API endpoint")
                url = f"{self.base_url}/HSCode/GetSections"
                response = self.session.get(url)
                sections_data = response.json()
                
                for section in sections_data:
                    sections.append({
                        'value': str(section['SectionID']),
                        'text': section['SectionDesc']
                    })
            
            return sections
        except Exception as e:
            self.logger.error(f"Error getting sections: {str(e)}")
            return []

    def get_chapters(self, section_id):
        """Get chapters for a specific section"""
        try:
            url = f"{self.base_url}/HSCode/GetChapters"
            data = {'sectionId': section_id}
            response = self.session.post(url, data=data)
            chapters = response.json()
            return [{'value': str(ch['ChapterID']), 'text': ch['ChapterDesc']} for ch in chapters]
        except Exception as e:
            self.logger.error(f"Error getting chapters for section {section_id}: {str(e)}")
            return []

    def get_headings(self, chapter_id):
        """Get headings for a specific chapter"""
        try:
            url = f"{self.base_url}/HSCode/GetHeadings"
            data = {'chapterId': chapter_id}
            response = self.session.post(url, data=data)
            headings = response.json()
            return [{'value': str(h['HeadingID']), 'text': h['HeadingDesc']} for h in headings]
        except Exception as e:
            self.logger.error(f"Error getting headings for chapter {chapter_id}: {str(e)}")
            return []

    def get_subheadings(self, heading_id):
        """Get subheadings for a specific heading"""
        try:
            url = f"{self.base_url}/HSCode/GetSubHeadings"
            data = {'headingId': heading_id}
            response = self.session.post(url, data=data)
            subheadings = response.json()
            return [{'value': str(sh['SubHeadingID']), 'text': sh['SubHeadingDesc']} for sh in subheadings]
        except Exception as e:
            self.logger.error(f"Error getting subheadings for heading {heading_id}: {str(e)}")
            return []

    def search_and_get_results(self, section_id, chapter_id=None, heading_id=None, subheading_id=None):
        """Perform search and get results"""
        try:
            url = f"{self.base_url}/HSCode/GetSearchResult"
            data = {
                'sectionId': section_id,
                'chapterId': chapter_id or '',
                'headingId': heading_id or '',
                'subHeadingId': subheading_id or '',
                'hsCodeId': '',
                'searchText': ''
            }
            
            response = self.session.post(url, json=data)
            results_data = response.json()
            
            results = []
            for item in results_data:
                results.append({
                    'hts_code': item.get('HSCode', ''),
                    'description': item.get('Description', ''),
                    'duty_rate': item.get('DutyRate', ''),
                    'unit': item.get('Unit', '')
                })
            return results
        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}")
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
            sections = self.get_sections()
            self.logger.info(f"Found {len(sections)} sections")
            
            for section in sections:
                section_id = section['value']
                self.logger.info(f"Processing section {section_id}")
                
                chapters = self.get_chapters(section_id)
                for chapter in chapters:
                    chapter_id = chapter['value']
                    self.logger.info(f"Processing chapter {chapter_id}")
                    
                    headings = self.get_headings(chapter_id)
                    for heading in headings:
                        heading_id = heading['value']
                        self.logger.info(f"Processing heading {heading_id}")
                        
                        subheadings = self.get_subheadings(heading_id)
                        if subheadings:
                            for subheading in subheadings:
                                subheading_id = subheading['value']
                                results = self.search_and_get_results(
                                    section_id, chapter_id, heading_id, subheading_id
                                )
                                self.data.extend(results)
                                time.sleep(1)  # Be nice to the server
                        else:
                            results = self.search_and_get_results(
                                section_id, chapter_id, heading_id
                            )
                            self.data.extend(results)
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