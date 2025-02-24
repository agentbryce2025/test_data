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

def extract_text_until_percent(text):
    """Extract text until we find a percentage or number with %."""
    match = re.search(r'^(.*?)(\d+(?:\.\d+)?%)', text)
    if match:
        return match.group(1).strip(), match.group(2)
    return text.strip(), None

def parse_hs_code_line(line):
    """Parse a line containing HS code and tariff information."""
    # Clean the line
    line = clean_text(line)
    
    # Pattern for HS codes (XX XX XX XX XX XX)
    code_pattern = r'^(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})'
    
    code_match = re.match(code_pattern, line)
    if not code_match:
        return None
        
    # Get the HS code parts
    code_parts = code_match.groups()
    hs_code = ''.join(code_parts)
    code_format = f"{code_parts[0]}.{code_parts[1]}.{code_parts[2]}.{code_parts[3]}.{code_parts[4]}.{code_parts[5]}"
    
    # Get the rest of the line after the code
    remainder = line[code_match.end():].strip()
    
    # Split the remainder into columns based on multiple spaces or tabs
    cols = re.split(r'\s{2,}|\t+', remainder)
    
    # Initialize default values
    description = ""
    duty_rate = ""
    efta = ""
    sg = ""
    usa = ""
    
    # Process the columns based on their content
    for col in cols:
        col = col.strip()
        if not col:
            continue
            
        # If it ends with %, it's likely a rate
        if col.endswith('%'):
            if not duty_rate:
                duty_rate = col
            elif not efta:
                efta = col
            elif not sg:
                sg = col
            elif not usa:
                usa = col
        else:
            # If it doesn't end with %, it's likely part of the description
            if description:
                description += " " + col
            else:
                description = col
    
    return {
        "hs_code": hs_code,
        "code_format": code_format,
        "description": description,
        "duty_rate": duty_rate,
        "efta": efta,
        "sg": sg,
        "usa": usa
    }

def parse_chapter_heading(line):
    """Parse chapter headings from the text."""
    line = clean_text(line)
    chapter_match = re.search(r'Chapter\s+(\d+)|الفصل\s+(\d+)', line, re.IGNORECASE)
    if chapter_match:
        return chapter_match.group(1) or chapter_match.group(2)
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
    current_chapter = None
    current_heading = None
    description_accumulator = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        for line_num, line in enumerate(lines):
            line = clean_text(line)
            if not line:
                continue
            
            # Look for chapter headers
            chapter = parse_chapter_heading(line)
            if chapter:
                current_chapter = chapter
                continue
            
            # Look for headings
            heading = parse_heading(line)
            if heading:
                current_heading = heading
                continue
            
            # Look for HS code lines
            if re.match(r'^\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}', line):
                entry = parse_hs_code_line(line)
                if entry:
                    entry['chapter'] = current_chapter
                    entry['heading'] = current_heading
                    
                    # Check the next few lines for additional description text
                    for i in range(1, 4):  # Look up to 3 lines ahead
                        if line_num + i < len(lines):
                            next_line = clean_text(lines[line_num + i])
                            if next_line and not re.match(r'^\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}', next_line):
                                if not any(rate in next_line for rate in ['%', 'EFTA', 'SG', 'USA']):
                                    entry['description'] += ' ' + next_line
                    
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
    output_base = "oman_tariff_data_v4"
    
    # Parse and save the data
    tariff_data = parse_tariff_file(input_file)
    save_data(tariff_data, output_base)

if __name__ == "__main__":
    main()