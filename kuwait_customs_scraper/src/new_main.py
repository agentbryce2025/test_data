import json
import time
import pandas as pd
from undetectable_scraper import UndetectableKuwaitCustomsScraper
from datetime import datetime

def main():
    scraper = UndetectableKuwaitCustomsScraper(headless=True)
    all_data = []
    error_log = []
    
    try:
        # Start the scraping session
        scraper.start_session()
        
        # Get all sections
        sections = scraper.get_sections()
        total_sections = len(sections)
        
        print(f"Found {total_sections} sections to process")
        
        # Iterate through sections
        for section_idx, section in enumerate(sections, 1):
            section_id = section['value']
            print(f"Processing section {section_idx}/{total_sections}: {section['text']}")
            
            try:
                # Get chapters for this section
                chapters = scraper.get_chapters(section_id)
                total_chapters = len(chapters)
                
                for chapter_idx, chapter in enumerate(chapters, 1):
                    chapter_id = chapter['value']
                    print(f"  Processing chapter {chapter_idx}/{total_chapters}: {chapter['text']}")
                    
                    try:
                        # Get headings for this chapter
                        headings = scraper.get_headings(section_id, chapter_id)
                        
                        if not headings:
                            # If no headings, try to get results directly for the chapter
                            results = scraper.search_and_get_results(section_id, chapter_id)
                            for result in results:
                                formatted_result = {
                                    'hts_code': result['hts_code'],
                                    'duty_rate': result['duty_rate'],
                                    'unit': result['unit'],
                                    'raw_duty_text': result['raw_duty_text'],
                                    'description': result['description'],
                                    'section_id': section_id,
                                    'section_text': section['text'],
                                    'chapter_id': chapter_id,
                                    'chapter_text': chapter['text'],
                                    'heading_id': '',
                                    'heading_text': '',
                                    'subheading_id': '',
                                    'subheading_text': ''
                                }
                                all_data.append(formatted_result)
                        else:
                            total_headings = len(headings)
                            for heading_idx, heading in enumerate(headings, 1):
                                heading_id = heading['value']
                                print(f"    Processing heading {heading_idx}/{total_headings}")
                                
                                try:
                                    # Get subheadings for this heading
                                    subheadings = scraper.get_subheadings(section_id, chapter_id, heading_id)
                                    
                                    if not subheadings:
                                        # If no subheadings, get results for the heading
                                        results = scraper.search_and_get_results(section_id, chapter_id, heading_id)
                                        for result in results:
                                            formatted_result = {
                                                'hts_code': result['hts_code'],
                                                'duty_rate': result['duty_rate'],
                                                'unit': result['unit'],
                                                'raw_duty_text': result['raw_duty_text'],
                                                'description': result['description'],
                                                'section_id': section_id,
                                                'section_text': section['text'],
                                                'chapter_id': chapter_id,
                                                'chapter_text': chapter['text'],
                                                'heading_id': heading_id,
                                                'heading_text': heading['text'],
                                                'subheading_id': '',
                                                'subheading_text': ''
                                            }
                                            all_data.append(formatted_result)
                                    else:
                                        total_subheadings = len(subheadings)
                                        for subheading_idx, subheading in enumerate(subheadings, 1):
                                            subheading_id = subheading['value']
                                            print(f"      Processing subheading {subheading_idx}/{total_subheadings}")
                                            
                                            try:
                                                results = scraper.search_and_get_results(
                                                    section_id, chapter_id, heading_id, subheading_id
                                                )
                                                
                                                for result in results:
                                                    formatted_result = {
                                                        'hts_code': result['hts_code'],
                                                        'duty_rate': result['duty_rate'],
                                                        'unit': result['unit'],
                                                        'raw_duty_text': result['raw_duty_text'],
                                                        'description': result['description'],
                                                        'section_id': section_id,
                                                        'section_text': section['text'],
                                                        'chapter_id': chapter_id,
                                                        'chapter_text': chapter['text'],
                                                        'heading_id': heading_id,
                                                        'heading_text': heading['text'],
                                                        'subheading_id': subheading_id,
                                                        'subheading_text': subheading['text']
                                                    }
                                                    all_data.append(formatted_result)
                                                    
                                            except Exception as e:
                                                error_msg = f"Error processing subheading {subheading_id}: {str(e)}"
                                                print(error_msg)
                                                error_log.append(error_msg)
                                                continue
                                            
                                            time.sleep(1)  # Delay between subheadings
                                            
                                except Exception as e:
                                    error_msg = f"Error processing heading {heading_id}: {str(e)}"
                                    print(error_msg)
                                    error_log.append(error_msg)
                                    continue
                                
                                time.sleep(1)  # Delay between headings
                                
                    except Exception as e:
                        error_msg = f"Error processing chapter {chapter_id}: {str(e)}"
                        print(error_msg)
                        error_log.append(error_msg)
                        continue
                    
                    time.sleep(1)  # Delay between chapters
                    
            except Exception as e:
                error_msg = f"Error processing section {section_id}: {str(e)}"
                print(error_msg)
                error_log.append(error_msg)
                continue
            
            # Intermediate save after each section
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f'../data/kuwait_customs_data_section_{section_idx}_{timestamp}.json', 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            time.sleep(2)  # Longer delay between sections
        
        # Final save
        print("\nSaving final results...")
        
        # Save complete dataset
        with open('../data/kuwait_customs_data_complete.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        # Save as CSV
        df = pd.DataFrame(all_data)
        df.to_csv('../data/kuwait_customs_data_complete.csv', index=False, encoding='utf-8')
        
        # Save error log
        if error_log:
            with open('../data/error_log.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(error_log))
        
        print(f"\nScraping completed successfully!")
        print(f"Total records collected: {len(all_data)}")
        print(f"Total errors encountered: {len(error_log)}")
        
    except Exception as e:
        print(f"A critical error occurred: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()