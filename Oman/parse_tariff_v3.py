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

def parse_hs_code_line(line):
    """Parse a line containing HS code information."""
    # Clean and normalize the line
    line = clean_text(line)
    
    # Pattern for HS codes with description and duty rate
    pattern = r'(\d{8})[,\s]+(\d{2})[,\s]+(\d{2}).*?(\d+(?:\.\d+)?%?)'
    match = re.search(pattern, line)
    
    if match:
        hs_code, subcode1, subcode2, duty_rate = match.groups()
        # Get description (everything between the codes and duty rate)
        desc_start = line.find(match.group(0)) + len(match.group(0))
        desc_end = line.rfind(duty_rate)
        description = line[desc_start:desc_end].strip()
        
        return {
            "hs_code": hs_code,
            "subcode": f"{subcode1}{subcode2}",
            "description": description,
            "duty_rate": duty_rate
        }
    return None

def parse_chapter_heading(line):
    """Parse chapter headings from the text."""
    line = clean_text(line)
    # Look for chapter numbers in both English and Arabic text
    chapter_match = re.search(r'Chapter\s+(\d+)|الفصل\s+(\d+)', line, re.IGNORECASE)
    if chapter_match:
        return chapter_match.group(1) or chapter_match.group(2)
    return None

def parse_section_heading(line):
    """Parse section headings from the text."""
    line = clean_text(line)
    section_match = re.search(r'Section\s+([IVX]+)|القسم\s+(\d+)', line, re.IGNORECASE)
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
            if re.search(r'\d{8}', line):
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
    output_base = "oman_tariff_data_v3"
    
    # Parse and save the data
    tariff_data = parse_tariff_file(input_file)
    save_data(tariff_data, output_base)

if __name__ == "__main__":
    main()