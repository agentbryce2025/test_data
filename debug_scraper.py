from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import requests
import json
import time
import platform
import os

def debug_reuters():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    try:
        print("\nDebugging Reuters Scraper...")
        driver = webdriver.Firefox(options=options)
        
        # Try different Reuters URLs
        urls = [
            "https://www.reuters.com/business/tariffs/",
            "https://www.reuters.com/markets/tariffs/",
            "https://www.reuters.com/markets/commodities/"
        ]
        
        for url in urls:
            print(f"\nTrying URL: {url}")
            driver.get(url)
            time.sleep(10)  # Wait longer for content
            
            # Save page source
            with open(f'reuters_debug_{url.split("/")[-2]}.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            # Try different selectors
            selectors = [
                ("article", "tag"),
                (".article", "css"),
                (".story-card", "css"),
                (".media-story-card", "css"),
                ("div[data-testid='story-card']", "css"),
                (".article__content", "css")
            ]
            
            for selector, selector_type in selectors:
                try:
                    if selector_type == "tag":
                        elements = driver.find_elements(By.TAG_NAME, selector)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"Selector '{selector}' found {len(elements)} elements")
                    
                    if elements:
                        print("\nFirst element details:")
                        element = elements[0]
                        print("HTML:", element.get_attribute('outerHTML'))
                        
                        # Try to find title
                        for title_selector in ['h3', 'h4', '.article-heading', '[data-testid="Heading"]']:
                            try:
                                title = element.find_element(By.CSS_SELECTOR, title_selector)
                                print(f"Found title with '{title_selector}': {title.text}")
                            except:
                                continue
                except Exception as e:
                    print(f"Error with selector '{selector}': {e}")
            
            print("\nPage title:", driver.title)
            print("Current URL:", driver.current_url)
            
    except Exception as e:
        print(f"Error in Reuters debug: {e}")
    finally:
        if driver:
            driver.quit()

def debug_gta():
    print("\nDebugging GTA Scraper...")
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    # Try different URLs and approaches
    urls = [
        "https://www.globaltradealert.org/latest/state_acts",
        "https://www.globaltradealert.org/latest/interventions",
        "https://www.globaltradealert.org/data/interventions",
        "https://www.globaltradealert.org/latest"
    ]
    
    for url in urls:
        print(f"\nTrying URL: {url}")
        try:
            response = session.get(url, headers=headers)
            print(f"Status code: {response.status_code}")
            print("Headers:", dict(response.headers))
            
            # Save response
            with open(f'gta_debug_{url.split("/")[-1]}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Try to parse as JSON
            try:
                data = response.json()
                print("Successfully parsed as JSON")
                print("Data structure:", json.dumps(data)[:500] + "...")
            except:
                print("Not JSON response")
                
                # Look for specific HTML elements
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try different selectors
                selectors = [
                    'table.interventions',
                    'div.intervention',
                    'div.state-act',
                    'tr.intervention-row',
                    'div.announcement'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    print(f"\nSelector '{selector}' found {len(elements)} elements")
                    if elements:
                        print("First element HTML:", elements[0])
                
        except Exception as e:
            print(f"Error with URL {url}: {e}")

if __name__ == "__main__":
    debug_reuters()
    debug_gta()
