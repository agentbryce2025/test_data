import requests
from datetime import datetime, timedelta
import json
import time
from bs4 import BeautifulSoup

class GTAScraper:
    def __init__(self):
        self.base_url = "https://globaltradealert.org/activity-tracker"
        self.params = {
            'ki': '1',
            'ka': '1',
            'ko': '0',
            'na': '0,999',
            'ast': 'oneplus',
            'nai': 'all',
            'kim': '1',
            'iis': 'oneplus',
            'ni': '1,999',
            'ke': '1',
            'ies': 'oneplus',
            'nei': 'all',
            'ky': '1',
            'kin': '1',
            'krn': '1',
            'kifd': '1',
            'kit': '1',
            'kmc': '1',
            'kil': '1',
            'kef': '1',
            'kt': '1',
            'kcf': '1',
            'kas': '1',
            'apit': 'tree',
            'kap': '1',
            'kid': '1',
            'kr': '1',
            'ij': 'any',
            'ih': 'any',
        }

    def get_last_week_announcements(self):
        announcements = []
        try:
            response = requests.get(self.base_url, params=self.params)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all announcement elements (you'll need to adjust these selectors based on the actual HTML structure)
            items = soup.find_all('div', class_='announcement-item')  # Adjust class name as needed
            
            one_week_ago = datetime.now() - timedelta(days=7)
            
            for item in items:
                try:
                    title = item.find('h3').text.strip()
                    date_str = item.find('time').text.strip()
                    date = datetime.strptime(date_str, "%Y-%m-%d")  # Adjust format as needed
                    
                    if date >= one_week_ago:
                        announcements.append({
                            "title": title,
                            "date": date_str,
                            "source": "Global Trade Alert"
                        })
                except Exception as e:
                    print(f"Error processing announcement: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Global Trade Alert: {e}")
            
        return announcements

    def save_to_json(self, announcements, filename="gta_announcements.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(announcements, f, indent=4, ensure_ascii=False)

def main():
    scraper = GTAScraper()
    announcements = scraper.get_last_week_announcements()
    scraper.save_to_json(announcements)

if __name__ == "__main__":
    main()
