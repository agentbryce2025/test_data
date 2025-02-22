from undetected_scraper import KuwaitCustomsUndetectedScraper
import logging

def main():
    try:
        # Initialize the scraper (headless=False for debugging)
        scraper = KuwaitCustomsUndetectedScraper(headless=False)
        
        # Start the scraping process
        scraper.scrape_all_codes()
        
    except Exception as e:
        logging.error(f"Main script error: {str(e)}")
        raise
    finally:
        # Make sure the scraper is closed properly
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main()