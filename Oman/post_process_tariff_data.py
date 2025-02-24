#!/usr/bin/env python3
"""
Post-process the extracted tariff data from Oman's Customs Tariff PDF.
This script takes the JSON output from the multimodal extraction and:
1. Standardizes the field names
2. Cleans up the data
3. Exports to both JSON and CSV formats
"""

import os
import json
import csv
import re
from typing import Dict, List, Any, Optional
import pandas as pd

# Constants
INPUT_JSON = "oman_tariff_data_multimodal_enhanced.json"
OUTPUT_JSON = "oman_tariff_final_cleaned.json"
OUTPUT_CSV = "oman_tariff_final_cleaned.csv"

def clean_duty_rate(rate_str: Optional[str]) -> Optional[float]:
    """Clean and standardize duty rate values."""
    if not rate_str or rate_str == "null" or rate_str == "None":
        return None
    
    # Extract percentage value
    match = re.search(r'(\d+(?:\.\d+)?)%?', str(rate_str))
    if match:
        return float(match.group(1))
    return None

def clean_hs_code(hs_code: Optional[str]) -> Optional[str]:
    """Clean and standardize HS code values."""
    if not hs_code or hs_code == "null" or hs_code == "None":
        return None
    
    # Remove any non-digit or non-dot characters
    cleaned = re.sub(r'[^\d.]', '', str(hs_code))
    if not cleaned:
        return None
    return cleaned

def standardize_field_names(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Standardize field names in entries."""
    field_mapping = {
        'h.s. code': 'hs_code',
        'h.s code': 'hs_code',
        'hs code': 'hs_code',
        'hscode': 'hs_code',
        'tariff code': 'hs_code',
        'code': 'hs_code',
        
        'description': 'description_en',
        'description in english': 'description_en',
        'english description': 'description_en',
        
        'arabic description': 'description_ar',
        'description in arabic': 'description_ar',
        
        'duty rate': 'duty_rate',
        'duty': 'duty_rate',
        'rate': 'duty_rate',
        
        'sfta': 'sfta',
        'sfta indicator': 'sfta',
        
        'sg': 'sg',
        'sg indicator': 'sg',
        
        'ura': 'ura',
        'ura indicator': 'ura'
    }
    
    standardized = {}
    
    for k, v in entry.items():
        key_lower = k.lower()
        if key_lower in field_mapping:
            standardized[field_mapping[key_lower]] = v
        else:
            standardized[k] = v
    
    # Ensure all standard fields exist
    for std_field in ['hs_code', 'description_en', 'description_ar', 'duty_rate', 'sfta', 'sg', 'ura']:
        if std_field not in standardized:
            standardized[std_field] = None
    
    return standardized

def clean_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean and standardize all entries."""
    cleaned_entries = []
    
    for entry in entries:
        if not entry:
            continue
            
        # Standardize field names
        standardized = standardize_field_names(entry)
        
        # Clean specific fields
        standardized['duty_rate'] = clean_duty_rate(standardized.get('duty_rate'))
        standardized['hs_code'] = clean_hs_code(standardized.get('hs_code'))
        
        cleaned_entries.append(standardized)
    
    return cleaned_entries

def process_json_data(input_path: str, output_json: str, output_csv: str):
    """Process the JSON data and export to both JSON and CSV formats."""
    print(f"Reading input data from {input_path}...")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return
    
    print(f"Processing {len(data)} pages of data...")
    
    all_entries = []
    
    # Extract entries from each page
    for page_data in data:
        page_num = page_data.get('page_number', 'unknown')
        
        entries = page_data.get('entries', [])
        if not entries and 'raw_content' in page_data:
            print(f"Warning: Page {page_num} has raw content but no structured entries.")
            continue
            
        # Clean and standardize entries
        cleaned_entries = clean_entries(entries)
        
        # Add page number to each entry
        for entry in cleaned_entries:
            entry['page_number'] = page_num
            all_entries.append(entry)
    
    print(f"Extracted {len(all_entries)} total entries.")
    
    # Save to JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    print(f"Saved cleaned data to {output_json}")
    
    # Convert to DataFrame and save as CSV
    try:
        df = pd.DataFrame(all_entries)
        df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"Saved data to CSV: {output_csv}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        
        # Fallback to basic CSV export
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                if all_entries:
                    fieldnames = all_entries[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_entries)
                    print(f"Saved data to CSV using fallback method: {output_csv}")
        except Exception as e2:
            print(f"Error with fallback CSV export: {e2}")

def main():
    """Main function."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_JSON)
    output_json_path = os.path.join(script_dir, OUTPUT_JSON)
    output_csv_path = os.path.join(script_dir, OUTPUT_CSV)
    
    process_json_data(input_path, output_json_path, output_csv_path)

if __name__ == "__main__":
    main()