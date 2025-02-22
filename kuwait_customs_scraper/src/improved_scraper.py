import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class KuwaitCustomsScraper:
    def __init__(self):
        self.url = "https://www.customs.gov.kw/HSCode/HsCode"
        self.options = uc.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
    def setup_driver(self):
        self.driver = uc.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def close_driver(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            
    def get_hts_data(self):
        try:
            self.setup_driver()
            self.driver.get(self.url)
            
            # Wait for the page to load
            time.sleep(10)
            
            # Get all chapter elements
            chapters = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "chapter"))
            )
            
            all_data = []
            
            # Iterate through chapters
            for chapter in chapters:
                try:
                    # Expand chapter
                    chapter.click()
                    time.sleep(2)
                    
                    # Get headings
                    headings = chapter.find_elements(By.CLASS_NAME, "heading")
                    
                    for heading in headings:
                        try:
                            # Expand heading
                            heading.click()
                            time.sleep(2)
                            
                            # Get subheadings
                            subheadings = heading.find_elements(By.CLASS_NAME, "subheading")
                            
                            for subheading in subheadings:
                                try:
                                    # Expand subheading
                                    subheading.click()
                                    time.sleep(2)
                                    
                                    # Get tariff items
                                    tariffs = subheading.find_elements(By.CLASS_NAME, "tariff")
                                    
                                    for tariff in tariffs:
                                        try:
                                            hts_code = tariff.find_element(By.CLASS_NAME, "hscode").text
                                            duty_rate = tariff.find_element(By.CLASS_NAME, "duty").text
                                            unit = tariff.find_element(By.CLASS_NAME, "unit").text
                                            
                                            data = {
                                                "hts_code": hts_code,
                                                "duty_rate": duty_rate,
                                                "unit": unit
                                            }
                                            all_data.append(data)
                                            
                                        except NoSuchElementException:
                                            continue
                                            
                                except Exception as e:
                                    print(f"Error processing subheading: {str(e)}")
                                    continue
                                    
                        except Exception as e:
                            print(f"Error processing heading: {str(e)}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing chapter: {str(e)}")
                    continue
                    
            return all_data
            
        except Exception as e:
            print(f"Major error: {str(e)}")
            return []
            
        finally:
            self.close_driver()
            
    def save_data(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
def main():
    scraper = KuwaitCustomsScraper()
    data = scraper.get_hts_data()
    scraper.save_data(data, 'kuwait_hts_data.json')

if __name__ == "__main__":
    main()