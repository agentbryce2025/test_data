import requests
from datetime import datetime, timedelta
import json

class GTAScraper:
    def __init__(self):
        self.api_url = "https://www.globaltradealert.org/api/v1/interventions"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_last_week_announcements(self):
        announcements = []
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'format': 'json'
        }
        
        try:
            print("Fetching GTA interventions...")
            response = requests.get(self.api_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('interventions', []):
                    try:
                        announcements.append({
                            "title": item.get('title'),
                            "implementing_country": item.get('implementing_country'),
                            "announcement_date": item.get('announcement_date'),
                            "implementation_date": item.get('implementation_date'),
                            "description": item.get('description'),
                            "source": "Global Trade Alert"
                        })
                        print(f"Found intervention: {item.get('title')}")
                    except Exception as e:
                        print(f"Error processing intervention: {e}")
                        continue
            else:
                print(f"Failed to fetch data: {response.status_code}")
                # Save the response for debugging
                with open('gta_error.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                    
        except Exception as e:
            print(f"Error scraping Global Trade Alert: {e}")
            
        return announcements

    def save_to_json(self, announcements, filename="gta_announcements.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(announcements, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(announcements)} announcements to {filename}")

def main():
    scraper = GTAScraper()
    announcements = scraper.get_last_week_announcements()
    scraper.save_to_json(announcements)

if __name__ == "__main__":
    main()
