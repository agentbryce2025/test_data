from full_scraper import KuwaitCustomsFullScraper
import logging

def main():
    try:
        # Initialize the scraper
        scraper = KuwaitCustomsFullScraper(headless=False)
        
        # Start the scraping process
        scraper.scrape_all_codes()
        
    except Exception as e:
        logging.error(f"Main script error: {str(e)}")
        raise
    finally:
        # Ensure the scraper is properly closed
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    main()