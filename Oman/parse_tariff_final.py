import re
import pandas as pd
import json
from pathlib import Path

def clean_text(text):
    """Clean text from unwanted characters and normalize spaces."""
    # Remove RTL and LTR marks and other special characters
    text = re.sub(r'[\u200e\u200f\u202a\u202b\u202c\u202d\u202e]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_hs_code_line(line):
    """Check if line contains an HS code pattern."""
    pattern = r'^\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}'
    return bool(re.match(pattern, line))

def parse_hs_code_line(line):
    """Parse a line containing HS code information."""
    line = clean_text(line)
    
    # Pattern for HS codes (XX XX XX XX XX XX)
    code_pattern = r'(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})'
    code_match = re.match(code_pattern, line)
    
    if code_match:
        # Combine the codes
        hs_code = ''.join(code_match.groups())
        
        # Get the remainder of the line after the codes
        remainder = line[code_match.end():].strip()
        
        # Look for the duty rate at the end
        duty_match = re.search(r'(\d+(?:\.\d+)?%?)$', remainder)
        if duty_match:
            duty_rate = duty_match.group(1)
            # Get description (everything between code and duty rate)
            description = remainder[:duty_match.start()].strip()
            
            return {
                "hs_code": hs_code,
                "description": description,
                "duty_rate": duty_rate
            }
    return None

def parse_chapter_heading(line):
    """Parse chapter headings from the text."""
    line = clean_text(line)
    chapter_match = re.search(r'Chapter\s+(\d+)|الفصل\s+(\d+)', line, re.IGNORECASE)
    if chapter_match:
        return chapter_match.group(1) or chapter_match.group(2)
    return None

def parse_section_heading(line):
    """Parse section headings from the text."""
    line = clean_text(line)
    section_match = re.search(r'Section\s+([IVX]+)|القسم\s+([IVX]+|\d+)', line, re.IGNORECASE)
    if section_match:
        return section_match.group(1) or section_match.group(2)
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
            
            # Look for section headers
            section = parse_section_heading(line)
            if section:
                current_section = section
                continue
            
            # Look for chapter headers
            chapter = parse_chapter_heading(line)
            if chapter:
                current_chapter = chapter
                continue
            
            # Look for HS code lines
            if is_hs_code_line(line):
                entry = parse_hs_code_line(line)
                if entry:
                    entry['chapter'] = current_chapter
                    entry['section'] = current_section
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
    output_base = "oman_tariff_data_final"
    
    # Parse and save the data
    tariff_data = parse_tariff_file(input_file)
    save_data(tariff_data, output_base)

if __name__ == "__main__":
    main()