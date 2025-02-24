from playwright.sync_api import sync_playwright
import logging
import time
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_site(url, filename_prefix):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            logger.info(f"Accessing {url}")
            page.goto(url, wait_until='networkidle')
            page.wait_for_timeout(5000)
            
            # Take a screenshot
            page.screenshot(path=f"{filename_prefix}_initial.png")
            logger.info(f"Saved initial screenshot as {filename_prefix}_initial.png")
            
            # Scroll down and take more screenshots
            for i in range(3):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight * {})'.format((i + 1) / 3))
                page.wait_for_timeout(2000)
                page.screenshot(path=f"{filename_prefix}_scroll_{i}.png")
                logger.info(f"Saved scroll screenshot {i}")
            
            # Get page content
            content = page.content()
            with open(f"{filename_prefix}_content.html", "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Saved page content to {filename_prefix}_content.html")
            
            # Print some basic page info
            logger.info(f"Page title: {page.title()}")
            logger.info(f"Current URL: {page.url}")
            
            # Try to find common elements
            for selector in ['article', '.article', '.story', 'div[data-testid]', 'div[class*="story"]', 'div[class*="article"]']:
                elements = page.query_selector_all(selector)
                logger.info(f"Found {len(elements)} elements with selector: {selector}")
                if elements:
                    first_html = elements[0].evaluate('el => el.outerHTML')
                    logger.info(f"First element example:\n{first_html[:500]}...")
            
            # Try to find specific text
            content = page.content().lower()
            keywords = ['tariff', 'trade', 'import', 'export', 'customs']
            for keyword in keywords:
                count = content.count(keyword)
                logger.info(f"Found {count} occurrences of '{keyword}'")
            
        except Exception as e:
            logger.error(f"Error debugging {url}: {e}")
        finally:
            browser.close()

def main():
    # Debug Reuters
    debug_site("https://www.reuters.com/business/trade/", "reuters_trade")
    debug_site("https://www.reuters.com/markets/commodities/", "reuters_commodities")
    
    # Debug GTA
    debug_site("https://www.globaltradealert.org/", "gta_home")
    debug_site("https://www.globaltradealert.org/stats", "gta_stats")

if __name__ == "__main__":
    main()
