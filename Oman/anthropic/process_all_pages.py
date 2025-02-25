import os
import json
import logging
from process_tarfah import process_pdf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PDF_PATH = '/home/computeruse/test_data/Oman/tarfah.pdf'
OUTPUT_DIR = '/home/computeruse/test_data/Oman/anthropic'
BATCH_SIZE = 20  # Process in batches of 20 pages

def process_in_batches(pdf_path, output_dir, total_pages):
    """Process the PDF in batches"""
    # Calculate number of batches
    num_batches = (total_pages + BATCH_SIZE - 1) // BATCH_SIZE
    
    logger.info(f"Processing {total_pages} pages in {num_batches} batches of {BATCH_SIZE} pages each")
    
    # Process each batch
    for batch in range(num_batches):
        start_page = batch * BATCH_SIZE + 1
        end_page = min((batch + 1) * BATCH_SIZE, total_pages)
        
        logger.info(f"Processing batch {batch+1}/{num_batches}: pages {start_page} to {end_page}")
        process_pdf(pdf_path, output_dir, start_page, end_page)
    
    # Combine all individual page results into a final output
    combine_results(output_dir, total_pages)

def combine_results(output_dir, total_pages):
    """Combine all individual page results into a single JSON file"""
    all_data = []
    
    for page_num in range(1, total_pages + 1):
        result_file = os.path.join(output_dir, f"page_{page_num}_result.json")
        if os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                    
                if "data" in result and isinstance(result["data"], list):
                    all_data.extend(result["data"])
                elif "data" in result and isinstance(result["data"], dict):
                    # Handle case where data is a dict with rows
                    if "rows" in result["data"]:
                        all_data.extend(result["data"]["rows"])
            except Exception as e:
                logger.error(f"Error processing result file for page {page_num}: {str(e)}")
    
    # Save the combined result
    final_output_file = os.path.join(output_dir, "final_tarfah_ocr_result.json")
    with open(final_output_file, "w") as f:
        json.dump(all_data, f, indent=4)
    
    logger.info(f"All results combined into {final_output_file}")
    logger.info(f"Total number of entries: {len(all_data)}")

if __name__ == "__main__":
    # Get total number of pages from the PDF
    import PyPDF2
    pdf = PyPDF2.PdfReader(PDF_PATH)
    total_pages = len(pdf.pages)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    process_in_batches(PDF_PATH, OUTPUT_DIR, total_pages)