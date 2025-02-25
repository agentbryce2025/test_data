import os
import logging
import argparse
from process_tarfah import process_pdf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PDF_PATH = '/home/computeruse/test_data/Oman/tarfah.pdf'
OUTPUT_DIR = '/home/computeruse/test_data/Oman/anthropic'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a batch of pages from the PDF')
    parser.add_argument('--start', type=int, required=True, help='Starting page number')
    parser.add_argument('--end', type=int, required=True, help='Ending page number')
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    process_pdf(PDF_PATH, OUTPUT_DIR, start_page=args.start, end_page=args.end)