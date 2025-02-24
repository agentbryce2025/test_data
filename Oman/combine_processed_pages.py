#!/usr/bin/env python3
"""
Combine all processed page_*_result.json files into a single output file.
"""

import os
import json
import glob
from typing import List, Dict, Any

# Constants
OUTPUT_JSON = "oman_tariff_data_multimodal_enhanced.json"

def combine_page_files(pattern: str = "page_*_result.json") -> List[Dict[str, Any]]:
    """
    Combine multiple page result JSON files into a single list.
    
    Args:
        pattern: Glob pattern to match page files
        
    Returns:
        Combined list of all page data
    """
    all_data = []
    page_files = sorted(glob.glob(pattern))
    
    if not page_files:
        print(f"No files found matching pattern: {pattern}")
        return all_data
    
    print(f"Found {len(page_files)} page files to combine.")
    
    for page_file in page_files:
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
                all_data.append(page_data)
                print(f"Added data from {page_file}")
        except Exception as e:
            print(f"Error loading {page_file}: {e}")
    
    return all_data

def main():
    """Main function to combine page files and save the combined result."""
    combined_data = combine_page_files()
    
    if not combined_data:
        print("No data to save.")
        return
    
    # Save the combined results
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nCombine complete. {len(combined_data)} pages of data saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()