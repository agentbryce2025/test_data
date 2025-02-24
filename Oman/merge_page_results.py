#!/usr/bin/env python3
"""
Utility script to merge individual page JSON results into a single JSON file.
This is useful when processing large PDFs page by page.
"""

import os
import json
import glob
import argparse
from pathlib import Path

def merge_json_files(input_dir, output_file, pattern="page_*_data.json"):
    """
    Merge multiple JSON files into a single JSON file.
    
    Args:
        input_dir: Directory containing JSON files
        output_file: Path to the output JSON file
        pattern: Glob pattern to match JSON files
    """
    # Get all JSON files matching the pattern
    json_files = sorted(glob.glob(os.path.join(input_dir, pattern)), 
                        key=lambda x: int(x.split('_')[1]))
    
    if not json_files:
        print(f"No JSON files found in {input_dir} matching pattern '{pattern}'")
        return False
    
    # Merge the data
    merged_data = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged_data.append(data)
                print(f"Merged data from {json_file}")
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    # Sort by page number if available
    merged_data.sort(key=lambda x: x.get("page_number", 0))
    
    # Save the merged data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"Merged {len(merged_data)} JSON files into {output_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Merge individual page JSON results into a single file")
    parser.add_argument("--input", default="tarfah_page_images", help="Input directory containing JSON files")
    parser.add_argument("--output", default="oman_tariff_data_merged.json", help="Output JSON file")
    parser.add_argument("--pattern", default="page_*_data.json", help="File pattern to match")
    args = parser.parse_args()
    
    input_dir = args.input
    if not os.path.isabs(input_dir):
        input_dir = os.path.join(os.path.dirname(__file__), input_dir)
    
    output_file = args.output
    if not os.path.isabs(output_file):
        output_file = os.path.join(os.path.dirname(__file__), output_file)
    
    success = merge_json_files(input_dir, output_file, args.pattern)
    
    if success:
        print(f"Successfully merged JSON files from {input_dir} to {output_file}")
    else:
        print(f"Failed to merge JSON files")

if __name__ == "__main__":
    main()