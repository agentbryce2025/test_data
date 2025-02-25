import os
import time
import subprocess
import logging
import json
import PyPDF2
from merge_results import merge_all_results

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PDF_PATH = '/home/computeruse/test_data/Oman/tarfah.pdf'
OUTPUT_DIR = '/home/computeruse/test_data/Oman/anthropic'
BATCH_SIZE = 10  # Process in batches of 10 pages

def process_pdf_in_batches():
    """Process the PDF in batches using subprocess to avoid memory issues"""
    # Get total number of pages from the PDF
    pdf = PyPDF2.PdfReader(PDF_PATH)
    total_pages = len(pdf.pages)
    logger.info(f"PDF has {total_pages} pages")
    
    # Calculate number of batches
    num_batches = (total_pages + BATCH_SIZE - 1) // BATCH_SIZE
    logger.info(f"Will process in {num_batches} batches of {BATCH_SIZE} pages each")
    
    # Process each batch
    for batch in range(num_batches):
        start_page = batch * BATCH_SIZE + 1
        end_page = min((batch + 1) * BATCH_SIZE, total_pages)
        
        logger.info(f"Processing batch {batch+1}/{num_batches}: pages {start_page} to {end_page}")
        
        # Use subprocess to run the batch processing
        process = subprocess.Popen([
            'python3', 
            os.path.join(OUTPUT_DIR, 'process_batch.py'),
            '--start', str(start_page),
            '--end', str(end_page)
        ])
        
        # Wait for the process to complete
        process.wait()
        
        if process.returncode != 0:
            logger.error(f"Batch {batch+1} failed with return code {process.returncode}")
        else:
            logger.info(f"Batch {batch+1} completed successfully")
        
        # Sleep a bit to prevent rate limiting
        time.sleep(5)
    
    # Combine all batch results
    logger.info("All batches processed. Merging results...")
    merge_all_results()
    logger.info("Processing complete!")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    process_pdf_in_batches()