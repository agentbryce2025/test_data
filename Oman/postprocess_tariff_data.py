#!/usr/bin/env python3
"""
Post-process Oman Tariff Data

This script performs post-processing on the extracted tariff data to:
1. Clean up H.S. Codes
2. Fix data type issues
3. Normalize duty rates
4. Validate data structure
5. Apply business rules to correct common errors
"""

import os
import sys
import json
import re
from pathlib import Path

# Input/Output file paths
DEFAULT_INPUT = "oman_tariff_data_multimodal.json"
DEFAULT_OUTPUT = "oman_tariff_data_multimodal_cleaned.json"

def clean_hs_code(code):
    """Clean and normalize H.S. Code format."""
    if not code:
        return None
    
    # Remove any non-alphanumeric, dot, or space characters
    code = re.sub(r'[^0-9A-Za-z\. ]', '', code)
    
    # Normalize spaces between digit groups (common format in tariff docs)
    # Example: "01.02" -> "01 02" or "01 02 21 00 00" stays the same
    if '.' in code and ' ' not in code:
        code = code.replace('.', ' ')
    
    # Ensure consistent spacing
    code = re.sub(r'\s+', ' ', code).strip()
    
    return code

def normalize_duty_rate(rate):
    """Normalize duty rate to consistent format."""
    if not rate:
        return None
    
    rate = str(rate).strip()
    
    # Convert common variations
    if rate.lower() in ['free', 'duty free', 'zero', '0', 'nil']:
        return '0%'
    
    # Ensure percentage rates end with %
    if re.match(r'^\d+(\.\d+)?$', rate):
        return f"{rate}%"
    
    # For rates already with % sign, ensure no space between number and %
    rate = re.sub(r'(\d+)\s+%', r'\1%', rate)
    
    return rate

def check_indicator_field(value):
    """Validate and normalize indicator fields (SFTA, SG, URA)."""
    if not value or value in ['-', 'null', 'None', '']:
        return None
    
    # If it's numeric with % symbol, it's likely a misplaced duty rate
    if isinstance(value, str) and (re.match(r'^\d+%$', value) or re.match(r'^\d+(\.\d+)?%$', value)):
        return None
    
    # Normalize common indicators
    value = str(value).strip().upper()
    
    # If value is longer than 3 characters, it's likely not an indicator
    if len(value) > 3:
        return None
        
    return value

def validate_entry(entry):
    """Validate and clean up a single entry."""
    valid_entry = {}
    
    # Clean H.S. Code
    valid_entry["H.S. Code"] = clean_hs_code(entry.get("H.S. Code"))
    
    # Keep descriptions as is, but ensure they're strings
    valid_entry["Description in English"] = str(entry.get("Description in English", "")) if entry.get("Description in English") else None
    valid_entry["Description in Arabic"] = str(entry.get("Description in Arabic", "")) if entry.get("Description in Arabic") else None
    
    # Normalize Duty Rate
    valid_entry["Duty Rate"] = normalize_duty_rate(entry.get("Duty Rate"))
    
    # Validate indicator fields
    valid_entry["SFTA"] = check_indicator_field(entry.get("SFTA"))
    valid_entry["SG"] = check_indicator_field(entry.get("SG"))
    valid_entry["URA"] = check_indicator_field(entry.get("URA"))
    
    # Preserve page number
    valid_entry["page_number"] = entry.get("page_number")
    
    return valid_entry

def fix_common_errors(data):
    """Fix common errors found in the extracted data."""
    if "entries" not in data or not isinstance(data["entries"], list):
        return data
    
    for i, entry in enumerate(data["entries"]):
        # Fix case where duty rate might be in SFTA field due to column misalignment
        if entry.get("SFTA") and isinstance(entry.get("SFTA"), str) and "%" in entry.get("SFTA"):
            if not entry.get("Duty Rate"):
                data["entries"][i]["Duty Rate"] = entry.get("SFTA")
                data["entries"][i]["SFTA"] = None
        
        # Similar checks for other indicator fields
        if entry.get("SG") and isinstance(entry.get("SG"), str) and "%" in entry.get("SG"):
            if not entry.get("Duty Rate"):
                data["entries"][i]["Duty Rate"] = entry.get("SG")
                data["entries"][i]["SG"] = None
                
        if entry.get("URA") and isinstance(entry.get("URA"), str) and "%" in entry.get("URA"):
            if not entry.get("Duty Rate"):
                data["entries"][i]["Duty Rate"] = entry.get("URA")
                data["entries"][i]["URA"] = None
    
    return data

def remove_duplicate_entries(data):
    """Remove duplicate entries based on H.S. Code and descriptions."""
    if "entries" not in data or not isinstance(data["entries"], list):
        return data
    
    unique_entries = []
    seen = set()
    
    for entry in data["entries"]:
        # Create a key from the combination of HS code and English description
        hs_code = entry.get("H.S. Code", "")
        eng_desc = entry.get("Description in English", "")
        key = f"{hs_code}|{eng_desc}"
        
        if key not in seen and hs_code:  # Only keep entry if it has an HS code
            seen.add(key)
            unique_entries.append(entry)
    
    data["entries"] = unique_entries
    return data

def postprocess_data(input_file, output_file):
    """Post-process the JSON data file."""
    try:
        # Load the JSON data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate structure
        if not isinstance(data, dict):
            print(f"Error: Expected dictionary at root level in {input_file}")
            return False
        
        # Process entries
        if "entries" in data and isinstance(data["entries"], list):
            # Apply validation to each entry
            cleaned_entries = [validate_entry(entry) for entry in data["entries"]]
            data["entries"] = cleaned_entries
            
            # Fix common errors
            data = fix_common_errors(data)
            
            # Remove duplicates
            data = remove_duplicate_entries(data)
            
            # Add statistics
            data["statistics"] = {
                "total_entries": len(data["entries"]),
                "entries_with_duty_rate": sum(1 for e in data["entries"] if e.get("Duty Rate")),
                "unique_hs_codes": len(set(e.get("H.S. Code") for e in data["entries"] if e.get("H.S. Code"))),
                "pages_processed": len(set(e.get("page_number") for e in data["entries"] if e.get("page_number"))),
            }
            
            # Save the post-processed data
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Post-processing complete. Cleaned data saved to {output_file}")
            print(f"Statistics: {data['statistics']}")
            return True
            
        else:
            print(f"Error: No 'entries' array found in {input_file}")
            return False
            
    except Exception as e:
        print(f"Error during post-processing: {e}")
        return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Post-process Oman Tariff Data")
    parser.add_argument("-i", "--input", default=DEFAULT_INPUT, help=f"Input JSON file (default: {DEFAULT_INPUT})")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help=f"Output JSON file (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()
    
    # Ensure input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    # Run post-processing
    if postprocess_data(args.input, args.output):
        print("Post-processing completed successfully")
    else:
        print("Post-processing failed")
        sys.exit(1)

if __name__ == "__main__":
    main()