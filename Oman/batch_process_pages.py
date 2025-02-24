#!/usr/bin/env python3
"""
Process multiple pages of the Oman Customs Tariff PDF in batches.
This script calls the single page processor for specified pages and combines the results.
"""

import os
import json
import sys
import time
import subprocess
from typing import List, Dict, Any

# Constants
PDF_PATH = "tarfah.pdf"
OUTPUT_JSON = "oman_tariff_data_multimodal_enhanced.json"

def process_page_range(start_page: int, end_page: int) -> List[Dict[str, Any]]:
    """Process a range of pages and combine the results."""
    all_results = []
    
    for page_num in range(start_page, end_page + 1):
        print(f"\n===== Processing page {page_num} =====")
        
        # Call the single page processor script
        cmd = f"python process_single_page_enhanced.py {page_num}"
        process = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        
        if process.returncode != 0:
            print(f"Error processing page {page_num}: {process.stderr}")
            continue
            
        # Load the results from the generated JSON file
        result_file = f"page_{page_num}_result.json"
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
                all_results.append(page_data)
                print(f"Page {page_num} processed successfully.")
        except Exception as e:
            print(f"Error loading results for page {page_num}: {e}")
        
        # Wait briefly to avoid rate limiting
        time.sleep(0.5)
    
    return all_results

def main():
    """Main function to process PDF pages in batches and save results."""
    if len(sys.argv) < 3:
        print("Usage: python batch_process_pages.py START_PAGE END_PAGE")
        sys.exit(1)
    
    try:
        start_page = int(sys.argv[1])
        end_page = int(sys.argv[2])
    except ValueError:
        print("Error: Page numbers must be integers")
        sys.exit(1)
    
    if start_page > end_page:
        print("Error: Start page must be less than or equal to end page")
        sys.exit(1)
    
    print(f"Processing pages {start_page} to {end_page}...")
    
    # Process the pages
    results = process_page_range(start_page, end_page)
    
    # Save the results
    output_path = f"oman_tariff_data_pages_{start_page}-{end_page}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nProcessing complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()