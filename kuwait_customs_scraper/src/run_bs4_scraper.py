from bs4_scraper import KuwaitCustomsBS4Scraper
import logging

def main():
    try:
        # Initialize the scraper
        scraper = KuwaitCustomsBS4Scraper()
        
        # Start the scraping process
        scraper.scrape_all_codes()
        
    except Exception as e:
        logging.error(f"Main script error: {str(e)}")
        raise

if __name__ == "__main__":
    main()