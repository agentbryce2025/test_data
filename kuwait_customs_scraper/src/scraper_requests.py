import requests
import json
import time
from bs4 import BeautifulSoup

class KuwaitCustomsScraper:
    def __init__(self):
        self.base_url = "https://www.customs.gov.kw"
        self.search_url = f"{self.base_url}/HSCode/HsCode"
        self.session = requests.Session()
        
        # Headers to simulate a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest'
        }

    def get_sections(self):
        response = self.session.get(self.search_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        sections = []
        section_select = soup.find('select', {'id': 'SectionID'})
        if section_select:
            for option in section_select.find_all('option')[1:]:  # Skip first empty option
                sections.append({
                    'code': option['value'],
                    'description': option.text.strip()
                })
        return sections

    def search_by_section(self, section_code):
        data = {
            'SectionID': section_code,
            'ChapterID': '',
            'HeadingID': '',
            'SubHeadingID': ''
        }
        
        response = self.session.post(f"{self.base_url}/HSCode/SearchHsCode", 
                                   headers=self.headers,
                                   data=data)
        
        try:
            results = response.json()
            formatted_results = []
            
            for item in results:
                formatted_result = {
                    'hts_code': item.get('HsCode', ''),
                    'rate': item.get('DutyRate', '').replace('%', '').strip(),
                    'units': '',  # Kuwait customs doesn't explicitly show units
                    'additional_info': f"Description: {item.get('Description', '')}"
                }
                formatted_results.append(formatted_result)
                
            return formatted_results
        except:
            return []

def main():
    scraper = KuwaitCustomsScraper()
    all_data = []
    
    # Get all sections
    sections = scraper.get_sections()
    
    # Process each section
    for section in sections:
        print(f"Processing section: {section['description']}")
        
        # Get data for this section
        results = scraper.search_by_section(section['code'])
        
        # Add section info to results
        for result in results:
            result['additional_info'] = f"Section: {section['description']}, {result['additional_info']}"
            all_data.append(result)
        
        # Respect the website by waiting between requests
        time.sleep(2)
    
    # Save the data
    with open('data/kuwait_customs_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"Scraping completed! Total records: {len(all_data)}")

if __name__ == "__main__":
    main()