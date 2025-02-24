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

def parse_hs_code_line(line, current_heading):
    """Parse a line containing HS code information."""
    line = clean_text(line)
    
    # Pattern for HS codes (XX XX XX XX XX XX)
    code_pattern = r'^(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})'
    code_match = re.match(code_pattern, line)
    
    if code_match:
        # Combine the codes
        code_parts = code_match.groups()
        hs_code = ''.join(code_parts)
        
        # Get the remainder of the line after the codes
        remainder = line[code_match.end():].strip()
        
        # Look for any number at the end as the duty rate
        duty_match = re.search(r'(\d+(?:\.\d+)?%?)$', remainder)
        duty_rate = duty_match.group(1) if duty_match else ""
        
        # Everything between the code and duty rate (if any) is the description
        description = remainder
        if duty_match:
            description = remainder[:duty_match.start()].strip()
        
        return {
            "heading": current_heading,
            "hs_code": hs_code,
            "code_format": f"{code_parts[0]}.{code_parts[1]}.{code_parts[2]}.{code_parts[3]}.{code_parts[4]}.{code_parts[5]}",
            "description": description,
            "duty_rate": duty_rate
        }
    return None

def parse_heading(line):
    """Parse a heading line."""
    line = clean_text(line)
    heading_match = re.search(r'(\d{2}\.\d{2})', line)
    if heading_match:
        return heading_match.group(1)
    return None

def parse_tariff_file(file_path):
    """Parse the entire tariff file and extract relevant information."""
    tariff_data = []
    current_heading = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        for line in lines:
            line = clean_text(line)
            if not line:
                continue
            
            # Look for headings
            heading = parse_heading(line)
            if heading:
                current_heading = heading
                continue
            
            # Look for HS code lines
            if is_hs_code_line(line):
                entry = parse_hs_code_line(line, current_heading)
                if entry:
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
    output_base = "oman_tariff_data_final2"
    
    # Parse and save the data
    tariff_data = parse_tariff_file(input_file)
    save_data(tariff_data, output_base)

if __name__ == "__main__":
    main()