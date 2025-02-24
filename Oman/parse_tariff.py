import re
import pandas as pd
import json
from pathlib import Path

def parse_tariff_line(line):
    """Parse a line containing tariff information."""
    # Extract HS code, description, and duty rate
    pattern = r"(\d{2}(?:\s\d{2})*(?:\s\d{2}\s\d{2})?)\s+(.*?)\s+(\d+(?:\.\d+)?%?|\-)\s*$"
    match = re.search(pattern, line)
    if match:
        hs_code = match.group(1).replace(" ", "")
        description = match.group(2).strip()
        duty_rate = match.group(3).strip()
        return {
            "hs_code": hs_code,
            "description": description,
            "duty_rate": duty_rate
        }
    return None

def parse_tariff_file(file_path):
    """Parse the entire tariff file and extract relevant information."""
    tariff_data = []
    current_chapter = None
    current_heading = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for chapter headers
            chapter_match = re.search(r"Chapter\s+(\d+)", line)
            if chapter_match:
                current_chapter = chapter_match.group(1)
                continue
                
            # Parse tariff lines
            entry = parse_tariff_line(line)
            if entry:
                entry['chapter'] = current_chapter
                tariff_data.append(entry)
    
    return tariff_data

def main():
    # Parse the tariff text file
    input_file = "tarfah.txt"
    output_file = "oman_tariff_data.json"
    
    tariff_data = parse_tariff_file(input_file)
    
    # Save as JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tariff_data, f, indent=2, ensure_ascii=False)
    
    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(tariff_data)
    df.to_csv("oman_tariff_data.csv", index=False)
    
    print(f"Processed {len(tariff_data)} tariff entries")
    print(f"Data saved to {output_file} and oman_tariff_data.csv")

if __name__ == "__main__":
    main()