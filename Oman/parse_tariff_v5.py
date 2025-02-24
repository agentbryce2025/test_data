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

class TariffParser:
    def __init__(self):
        self.current_heading = None
        self.current_description = None
        self.current_chapter = None
        self.current_rates = {'duty_rate': None, 'efta': None, 'sg': None, 'usa': None}
        self.entries = []
        self.description_buffer = []

    def is_hs_code(self, line):
        """Check if line contains a valid HS code pattern."""
        return bool(re.match(r'^\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}', line))

    def parse_heading(self, line):
        """Parse heading from line."""
        match = re.search(r'(\d{2}\.\d{2})', line)
        if match:
            self.current_heading = match.group(1)
            return True
        return False

    def parse_chapter(self, line):
        """Parse chapter from line."""
        match = re.search(r'Chapter\s+(\d+)', line)
        if match:
            self.current_chapter = match.group(1)
            return True
        return False

    def parse_rates(self, line):
        """Parse duty rates from line."""
        # Look for percentage rates
        rates = re.findall(r'(\d+(?:\.\d+)?%)', line)
        if rates:
            if 'DUTY RATE' in line or len(rates) == 1:
                self.current_rates['duty_rate'] = rates[0]
            elif 'EFTA' in line and len(rates) >= 1:
                self.current_rates['efta'] = rates[0]
            elif 'SG' in line and len(rates) >= 1:
                self.current_rates['sg'] = rates[0]
            elif 'USA' in line and len(rates) >= 1:
                self.current_rates['usa'] = rates[0]
            return True
        return False

    def parse_description(self, line):
        """Parse description from line."""
        # Skip lines that look like headers or contain special markers
        if any(marker in line for marker in ['DUTY RATE', 'EFTA', 'SG', 'USA', 'H.S CODE', 'HEADING']):
            return False
        
        # Skip lines that are just numbers or empty
        if not line or line.isdigit() or re.match(r'^[\d\s.%]+$', line):
            return False
        
        # Add line to description buffer
        self.description_buffer.append(line)
        return True

    def parse_hs_code_line(self, line):
        """Parse a line containing HS code information."""
        # Pattern for HS codes (XX XX XX XX XX XX)
        match = re.match(r'^(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})', line)
        if match:
            code_parts = match.groups()
            hs_code = ''.join(code_parts)
            code_format = '.'.join(code_parts)
            
            # Create entry with current context
            entry = {
                'chapter': self.current_chapter,
                'heading': self.current_heading,
                'hs_code': hs_code,
                'code_format': code_format,
                'description': ' '.join(self.description_buffer) if self.description_buffer else '',
                'duty_rate': self.current_rates['duty_rate'],
                'efta': self.current_rates['efta'],
                'sg': self.current_rates['sg'],
                'usa': self.current_rates['usa']
            }
            
            # Clear buffers for next entry
            self.description_buffer = []
            return entry
        return None

    def parse_file(self, file_path):
        """Parse the entire tariff file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = clean_text(line)
            if not line:
                continue

            if self.parse_chapter(line):
                continue
            
            if self.parse_heading(line):
                continue
            
            if self.parse_rates(line):
                continue

            if self.is_hs_code(line):
                entry = self.parse_hs_code_line(line)
                if entry:
                    self.entries.append(entry)
            else:
                self.parse_description(line)

        return self.entries

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
    output_base = "oman_tariff_data_v5"
    
    parser = TariffParser()
    tariff_data = parser.parse_file(input_file)
    save_data(tariff_data, output_base)

if __name__ == "__main__":
    main()