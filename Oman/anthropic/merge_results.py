import os
import json
import glob
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
OUTPUT_DIR = '/home/computeruse/test_data/Oman/anthropic'
FINAL_OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'final_tarfah_ocr_result.json')

def merge_all_results():
    """Merge all batch results into a single final output"""
    all_data = []
    
    # Find all batch result files
    batch_files = glob.glob(os.path.join(OUTPUT_DIR, 'tarfah_ocr_result_*.json'))
    logger.info(f"Found {len(batch_files)} batch result files")
    
    # Process each batch file
    for batch_file in sorted(batch_files):
        try:
            with open(batch_file, 'r') as f:
                batch_data = json.load(f)
                
            if isinstance(batch_data, list):
                all_data.extend(batch_data)
                logger.info(f"Added {len(batch_data)} entries from {os.path.basename(batch_file)}")
        except Exception as e:
            logger.error(f"Error processing batch file {batch_file}: {str(e)}")
    
    # Save the final combined result
    with open(FINAL_OUTPUT_FILE, "w") as f:
        json.dump(all_data, f, indent=4)
    
    logger.info(f"All results combined into {FINAL_OUTPUT_FILE}")
    logger.info(f"Total number of entries: {len(all_data)}")
    
    return all_data

if __name__ == "__main__":
    merge_all_results()