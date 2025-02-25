import os
import logging
from process_tarfah import process_single_page

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PDF_PATH = '/home/computeruse/test_data/Oman/tarfah.pdf'
OUTPUT_DIR = '/home/computeruse/test_data/Oman/anthropic'

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Process just a single page as a test to check memory usage
    process_single_page(PDF_PATH, OUTPUT_DIR, page_num=10)