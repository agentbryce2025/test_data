#!/usr/bin/env python3
"""
Test script to process a few pages of the Oman Customs Tariff PDF.
This is intended as a quick test of the multimodal processing pipeline.
"""

import os
import sys
from process_tariff_multimodal import process_pdf, OUTPUT_DIR, PDF_PATH
import json

# Process just a few pages for testing
TEST_PAGES = (1, 3)  # Process only the first 3 pages

def main():
    pdf_path = os.path.join(os.path.dirname(__file__), PDF_PATH)
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)
    
    print(f"Testing PDF processing on pages {TEST_PAGES[0]}-{TEST_PAGES[1]}...")
    results = process_pdf(pdf_path, TEST_PAGES)
    
    # Save test results
    output_path = os.path.join(os.path.dirname(__file__), "test_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Test complete. Processed {len(results)} pages.")
    print(f"Results saved to {output_path}")
    
    # Print a summary
    print("\nSummary of processed pages:")
    for page_data in results:
        page_num = page_data.get("page_number", "unknown")
        
        # Check for entries
        if "entries" in page_data and isinstance(page_data["entries"], list):
            entry_count = len(page_data["entries"])
            print(f"Page {page_num}: {entry_count} entries extracted")
        elif "raw_content" in page_data:
            content_len = len(page_data["raw_content"])
            print(f"Page {page_num}: Raw content extracted ({content_len} characters)")
        else:
            print(f"Page {page_num}: No structured data extracted")

if __name__ == "__main__":
    main()