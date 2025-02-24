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

class TariffEntry:
    def __init__(self):
        self.chapter = None
        self.heading = None
        self.hs_code = None
        self.code_format = None
        self.description_en = None
        self.description_ar = None
        self.duty_rate = None
        self.efta = None
        self.sg = None
        self.usa = None

    def to_dict(self):
        return {
            'chapter': self.chapter,
            'heading': self.heading,
            'hs_code': self.hs_code,
            'code_format': self.code_format,
            'description_en': self.description_en,
            'description_ar': self.description_ar,
            'duty_rate': self.duty_rate,
            'efta': self.efta,
            'sg': self.sg,
            'usa': self.usa
        }

class TariffParser:
    def __init__(self):
        self.entries = []
        self.current_entry = None
        self.current_chapter = None
        self.current_heading = None
        self.description_buffer = []
        self.description_mode = None  # 'en' or 'ar'

    def start_new_entry(self):
        if self.current_entry and self.current_entry.hs_code:
            self.entries.append(self.current_entry.to_dict())
        self.current_entry = TariffEntry()
        self.current_entry.chapter = self.current_chapter
        self.current_entry.heading = self.current_heading
        self.description_buffer = []

    def process_description_buffer(self):
        if not self.current_entry:
            return
        
        text = ' '.join(self.description_buffer).strip()
        if not text:
            return
            
        # Check if text contains Arabic characters
        if any(ord(c) > 128 for c in text):
            self.current_entry.description_ar = text
        else:
            self.current_entry.description_en = text
        
        self.description_buffer = []

    def parse_line(self, line):
        line = clean_text(line)
        if not line:
            return

        # Check for chapter
        chapter_match = re.search(r'Chapter\s+(\d+)', line)
        if chapter_match:
            self.current_chapter = chapter_match.group(1)
            return

        # Check for heading
        heading_match = re.search(r'(\d{2}\.\d{2})', line)
        if heading_match:
            self.current_heading = heading_match.group(1)
            return

        # Check for HS code line
        hs_match = re.match(r'^(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})', line)
        if hs_match:
            self.process_description_buffer()
            self.start_new_entry()
            
            code_parts = hs_match.groups()
            self.current_entry.hs_code = ''.join(code_parts)
            self.current_entry.code_format = '.'.join(code_parts)
            
            # Check for rate at the end of the line
            remainder = line[hs_match.end():].strip()
            rate_match = re.search(r'(\d+(?:\.\d+)?%)\s*$', remainder)
            if rate_match:
                self.current_entry.duty_rate = rate_match.group(1)
                remainder = remainder[:rate_match.start()].strip()
            
            if remainder:
                self.description_buffer.append(remainder)
            return

        # Check for rates
        if 'DUTY RATE' in line or 'duty rate' in line.lower():
            rate_match = re.search(r'(\d+(?:\.\d+)?%)', line)
            if rate_match and self.current_entry:
                self.current_entry.duty_rate = rate_match.group(1)
            return

        if 'EFTA' in line:
            rate_match = re.search(r'(\d+(?:\.\d+)?%)', line)
            if rate_match and self.current_entry:
                self.current_entry.efta = rate_match.group(1)
            return

        if 'SG' in line:
            rate_match = re.search(r'(\d+(?:\.\d+)?%)', line)
            if rate_match and self.current_entry:
                self.current_entry.sg = rate_match.group(1)
            return

        if 'USA' in line:
            rate_match = re.search(r'(\d+(?:\.\d+)?%)', line)
            if rate_match and self.current_entry:
                self.current_entry.usa = rate_match.group(1)
            return

        # If it's not any of the above, it might be description text
        if not any(x in line for x in ['HEADING', 'H.S CODE', 'DESCRIPTION']):
            self.description_buffer.append(line)

    def parse_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.parse_line(line)
        
        # Process any remaining description
        self.process_description_buffer()
        # Add the last entry if exists
        if self.current_entry and self.current_entry.hs_code:
            self.entries.append(self.current_entry.to_dict())
        
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
    output_base = "oman_tariff_data_final3"
    
    parser = TariffParser()
    tariff_data = parser.parse_file(input_file)
    save_data(tariff_data, output_base)

if __name__ == "__main__":
    main()