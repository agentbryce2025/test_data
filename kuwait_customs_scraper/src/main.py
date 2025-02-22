import json
import time
import pandas as pd
from scraper import KuwaitCustomsScraper

def main():
    scraper = KuwaitCustomsScraper(headless=True)
    try:
        # Start the scraping session
        scraper.start_session()
        
        # Get all sections
        sections = scraper.get_sections()
        
        all_data = []
        
        # Iterate through sections
        for section in sections:
            section_id = section['value']
            print(f"Processing section: {section['text']}")
            
            # Get chapters for this section
            chapters = scraper.get_chapters(section_id)
            
            for chapter in chapters:
                chapter_id = chapter['value']
                print(f"Processing chapter: {chapter['text']}")
                
                # Get the data for this chapter
                results = scraper.search_and_get_results(section_id, chapter_id)
                
                # Add section and chapter info to results
                for result in results:
                    result['section'] = section['text']
                    result['chapter'] = chapter['text']
                
                all_data.extend(results)
                
                # Respect the website by waiting between requests
                time.sleep(2)
        
        # Save the data
        # Save as JSON
        with open('../data/kuwait_customs_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        # Save as CSV
        df = pd.DataFrame(all_data)
        df.to_csv('../data/kuwait_customs_data.csv', index=False, encoding='utf-8')
        
        print("Scraping completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()