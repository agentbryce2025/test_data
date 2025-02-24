import requests
from datetime import datetime, timedelta
import json

class GTAScraper:
    def __init__(self):
        self.url = "https://www.globaltradealert.org/graphql"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
        }

    def get_last_week_announcements(self):
        announcements = []
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # GraphQL query
        query = """
        query GetInterventions($startDate: String!, $endDate: String!) {
          interventions(
            filter: {
              dateRange: { start: $startDate, end: $endDate }
            }
          ) {
            items {
              id
              title
              implementingCountry
              announcementDate
              implementationDate
              description
              affectedCountries
              tradeFlows
            }
          }
        }
        """
        
        variables = {
            "startDate": start_date.strftime('%Y-%m-%d'),
            "endDate": end_date.strftime('%Y-%m-%d')
        }
        
        try:
            print("Fetching GTA interventions...")
            response = requests.post(
                self.url,
                headers=self.headers,
                json={
                    "query": query,
                    "variables": variables
                }
            )
            
            # Store the response for debugging
            with open('gta_debug.json', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            if response.status_code == 200:
                data = response.json()
                interventions = data.get('data', {}).get('interventions', {}).get('items', [])
                
                for item in interventions:
                    try:
                        announcements.append({
                            "id": item.get('id'),
                            "title": item.get('title'),
                            "implementing_country": item.get('implementingCountry'),
                            "announcement_date": item.get('announcementDate'),
                            "implementation_date": item.get('implementationDate'),
                            "description": item.get('description'),
                            "affected_countries": item.get('affectedCountries'),
                            "trade_flows": item.get('tradeFlows'),
                            "source": "Global Trade Alert"
                        })
                        print(f"Found intervention: {item.get('title')}")
                    except Exception as e:
                        print(f"Error processing intervention: {e}")
                        continue
            else:
                print(f"Failed to fetch data: {response.status_code}")
                print(f"Response: {response.text}")
                    
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
