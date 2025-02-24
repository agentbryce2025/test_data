import requests
from datetime import datetime, timedelta
import json
import logging
import time
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.reuters.com/'
        }
        
    def get_reuters_articles(self):
        """Get articles from Reuters API"""
        articles = []
        try:
            logger.info("Starting Reuters API scraper...")
            
            # Reuters API endpoints
            endpoints = [
                'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-section-alias',
                'https://www.reuters.com/pf/api/v3/content/fetch/recent-stories'
            ]
            
            params = {
                'query': '{"offset":0,"size":20,"section_alias":"business","website":"reuters"}',
                'filter': 'trade tariffs imports exports'
            }
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying endpoint: {endpoint}")
                    response = requests.get(endpoint, headers=self.headers, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Save response for debugging
                        with open(f'reuters_api_{endpoint.split("/")[-1]}.json', 'w') as f:
                            json.dump(data, f, indent=2)
                            
                        # Extract articles from response
                        items = data.get('result', {}).get('articles', [])
                        for item in items:
                            try:
                                keywords = ['trade', 'tariff', 'import', 'export', 'customs', 'duty']
                                text = f"{item.get('title', '')} {item.get('description', '')}".lower()
                                
                                if any(keyword in text for keyword in keywords):
                                    articles.append({
                                        "title": item.get('title'),
                                        "url": f"https://www.reuters.com{item.get('canonical_url')}",
                                        "date": item.get('published_time'),
                                        "description": item.get('description'),
                                        "source": "Reuters"
                                    })
                                    logger.info(f"Added article: {item.get('title')}")
                                    
                            except Exception as e:
                                logger.error(f"Error processing Reuters article: {e}")
                                continue
                                
                except Exception as e:
                    logger.error(f"Error with Reuters endpoint {endpoint}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in Reuters API scraper: {e}")
            
        return articles
        
    def get_gta_data(self):
        """Get data from GTA API"""
        announcements = []
        try:
            logger.info("Starting GTA API scraper...")
            
            # GTA API endpoints
            endpoints = [
                'https://www.globaltradealert.org/api/interventions',
                'https://www.globaltradealert.org/api/latest'
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying endpoint: {endpoint}")
                    response = requests.get(
                        endpoint,
                        headers=self.headers,
                        params={
                            'since': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            'format': 'json'
                        }
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            # Save response for debugging
                            with open(f'gta_api_{endpoint.split("/")[-1]}.json', 'w') as f:
                                json.dump(data, f, indent=2)
                                
                            # Extract announcements from response
                            items = data.get('interventions', []) or data.get('latest', []) or []
                            for item in items:
                                try:
                                    announcements.append({
                                        "title": item.get('title'),
                                        "date": item.get('announcement_date') or item.get('date'),
                                        "description": item.get('description'),
                                        "implementing_country": item.get('implementing_jurisdiction'),
                                        "source": "Global Trade Alert"
                                    })
                                    logger.info(f"Added announcement: {item.get('title')}")
                                    
                                except Exception as e:
                                    logger.error(f"Error processing GTA announcement: {e}")
                                    continue
                                    
                        except Exception as e:
                            logger.error(f"Error parsing GTA JSON: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error with GTA endpoint {endpoint}: {e}")
                    continue
                    
            # If API fails, try GraphQL endpoint
            if not announcements:
                logger.info("Trying GTA GraphQL endpoint...")
                graphql_url = 'https://www.globaltradealert.org/graphql'
                query = """
                query GetInterventions($since: String!) {
                    interventions(filter: { since: $since }) {
                        items {
                            title
                            description
                            announcementDate
                            implementingJurisdiction
                        }
                    }
                }
                """
                
                variables = {
                    'since': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                }
                
                try:
                    response = requests.post(
                        graphql_url,
                        headers=self.headers,
                        json={
                            'query': query,
                            'variables': variables
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get('data', {}).get('interventions', {}).get('items', [])
                        
                        for item in items:
                            announcements.append({
                                "title": item.get('title'),
                                "date": item.get('announcementDate'),
                                "description": item.get('description'),
                                "implementing_country": item.get('implementingJurisdiction'),
                                "source": "Global Trade Alert"
                            })
                            logger.info(f"Added announcement from GraphQL: {item.get('title')}")
                            
                except Exception as e:
                    logger.error(f"Error with GTA GraphQL endpoint: {e}")
                    
        except Exception as e:
            logger.error(f"Error in GTA API scraper: {e}")
            
        return announcements
        
    def run(self):
        """Run the complete scraping process"""
        try:
            # Get Reuters articles
            reuters_articles = self.get_reuters_articles()
            logger.info(f"Found {len(reuters_articles)} Reuters articles")
            
            # Get GTA announcements
            gta_announcements = self.get_gta_data()
            logger.info(f"Found {len(gta_announcements)} GTA announcements")
            
            # Filter out any items older than a week
            one_week_ago = datetime.now() - timedelta(days=7)
            
            reuters_articles = [
                article for article in reuters_articles
                if datetime.fromisoformat(article['date'].replace('Z', '+00:00')) >= one_week_ago
            ]
            
            gta_announcements = [
                announcement for announcement in gta_announcements
                if datetime.strptime(announcement['date'], '%Y-%m-%d') >= one_week_ago
            ]
            
            # Combine results
            results = {
                "timestamp": datetime.now().isoformat(),
                "reuters_articles": reuters_articles,
                "gta_announcements": gta_announcements
            }
            
            # Save results
            with open('trade_news.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info("Results saved to trade_news.json")
            
        except Exception as e:
            logger.error(f"Error running scraper: {e}")

if __name__ == "__main__":
    scraper = APIScraper()
    scraper.run()
