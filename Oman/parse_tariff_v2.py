import re
import pandas as pd
import json
from pathlib import Path

def clean_text(text):
    """Clean text from unwanted characters and normalize spaces."""
    # Remove RTL and LTR marks and other special characters
    text = re.sub(r'[\u200e\u200f\u202a\u202b\u202c\u202d\u202e]', '', text)
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_tariff_line(line):
    """Parse a line containing tariff information."""
    # Clean the line
    line = clean_text(line)
    
    # Different patterns to match tariff lines
    patterns = [
        # Pattern for standard HS code lines with duty rate
        r'^(\d{2}(?:\s?\d{2})*(?:\s?\d{2}\s?\d{2})?)\s+([^0-9]+?)\s+(\d+(?:\.\d+)?%?)$',
        # Pattern for lines with additional codes
        r'^(\d{2}(?:\s?\d{2})*(?:\s?\d{2}\s?\d{2})?)\s+(\d{2}(?:\s?\d{2})*)\s+([^0-9]+?)\s+(\d+(?:\.\d+)?%?)$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                hs_code, description, duty_rate = groups
                return {
                    "hs_code": hs_code.replace(" ", ""),
                    "description": clean_text(description),
                    "duty_rate": clean_text(duty_rate)
                }
            elif len(groups) == 4:
                hs_code, subcode, description, duty_rate = groups
                return {
                    "hs_code": hs_code.replace(" ", ""),
                    "subcode": subcode.replace(" ", ""),
                    "description": clean_text(description),
                    "duty_rate": clean_text(duty_rate)
                }
    return None

def parse_chapter_heading(line):
    """Parse chapter headings from the text."""
    line = clean_text(line)
    chapter_match = re.search(r'Chapter\s+(\d+)', line, re.IGNORECASE)
    if chapter_match:
        return chapter_match.group(1)
    return None

def parse_tariff_file(file_path):
    """Parse the entire tariff file and extract relevant information."""
    tariff_data = []
    current_chapter = None
    current_section = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        for line in lines:
            line = clean_text(line)
            if not line:
                continue
            
            # Look for chapter headers
            chapter = parse_chapter_heading(line)
            if chapter:
                current_chapter = chapter
                continue
            
            # Parse tariff lines
            entry = parse_tariff_line(line)
            if entry:
                entry['chapter'] = current_chapter
                tariff_data.append(entry)
    
    return tariff_data

def save_data(data, base_filename):
    """Save the parsed data in multiple formats."""
    # Save as JSON
    json_file = f"{base_filename}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(data)
    csv_file = f"{base_filename}.csv"
    df.to_csv(csv_file, index=False)
    
    print(f"Processed {len(data)} tariff entries")
    print(f"Data saved to {json_file} and {csv_file}")

def main():
    input_file = "tarfah.txt"
    output_base = "oman_tariff_data_v2"
    
    # Parse and save the data
    tariff_data = parse_tariff_file(input_file)
    save_data(tariff_data, output_base)

if __name__ == "__main__":
    main()