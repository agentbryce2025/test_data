import requests
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import time

class ReutersScraper:
    def __init__(self):
        self.url = "https://www.reuters.com/business/tariffs/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_last_week_articles(self):
        articles = []
        try:
            print("Fetching Reuters articles...")
            response = requests.get(self.url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Store the page content for debugging
            with open('reuters_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Find all story elements
            story_elements = soup.find_all('div', {'data-testid': 'story-card'})
            print(f"Found {len(story_elements)} story elements")
            
            one_week_ago = datetime.now() - timedelta(days=7)
            
            for story in story_elements:
                try:
                    # Extract title and link
                    title_element = story.find('a', {'data-testid': 'Heading'})
                    if not title_element:
                        continue
                        
                    title = title_element.text.strip()
                    link = 'https://www.reuters.com' + title_element['href']
                    
                    # Extract date
                    time_element = story.find('time')
                    if time_element and 'datetime' in time_element.attrs:
                        date_str = time_element['datetime']
                        article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        
                        if article_date >= one_week_ago:
                            # Extract description
                            description = ''
                            desc_element = story.find('p', {'data-testid': 'Paragraph'})
                            if desc_element:
                                description = desc_element.text.strip()
                            
                            articles.append({
                                "title": title,
                                "url": link,
                                "date": date_str,
                                "description": description,
                                "source": "Reuters"
                            })
                            print(f"Added article: {title}")
                            
                except Exception as e:
                    print(f"Error processing story: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Reuters: {e}")
            
        return articles

    def save_to_json(self, articles, filename="reuters_articles.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(articles)} articles to {filename}")

def main():
    scraper = ReutersScraper()
    articles = scraper.get_last_week_articles()
    scraper.save_to_json(articles)

if __name__ == "__main__":
    main()
