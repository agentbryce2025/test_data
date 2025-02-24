#!/usr/bin/env python3
"""
Merge multiple batch JSON files into a single combined file.
"""

import os
import json
import glob
from typing import List, Dict, Any

# Constants
OUTPUT_JSON = "oman_tariff_data_multimodal_enhanced.json"

def merge_batch_files(pattern: str = "oman_tariff_data_pages_*.json") -> List[Dict[str, Any]]:
    """
    Merge multiple batch JSON files into a single list.
    
    Args:
        pattern: Glob pattern to match batch files
        
    Returns:
        Combined list of all page data
    """
    all_data = []
    batch_files = sorted(glob.glob(pattern))
    
    if not batch_files:
        print(f"No files found matching pattern: {pattern}")
        return all_data
    
    print(f"Found {len(batch_files)} batch files to merge.")
    
    for batch_file in batch_files:
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
                all_data.extend(batch_data)
                print(f"Added data from {batch_file}")
        except Exception as e:
            print(f"Error loading {batch_file}: {e}")
    
    return all_data

def main():
    """Main function to merge batch files and save the combined result."""
    combined_data = merge_batch_files()
    
    if not combined_data:
        print("No data to save.")
        return
    
    # Save the combined results
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nMerge complete. {len(combined_data)} pages of data saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()