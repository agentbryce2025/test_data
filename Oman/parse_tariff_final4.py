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
        self.description_en = []
        self.description_ar = []
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
            'description_en': ' '.join(self.description_en),
            'description_ar': ' '.join(self.description_ar),
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
        self.current_section = None
        self.last_rates = {'duty_rate': None, 'efta': None, 'sg': None, 'usa': None}

    def is_arabic(self, text):
        """Check if text contains Arabic characters."""
        arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
        return bool(arabic_pattern.search(text))

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

        # Check for rates
        rate_match = re.search(r'(\d+(?:\.\d+)?%)', line)
        if rate_match:
            rate = rate_match.group(1)
            if 'DUTY RATE' in line or 'duty rate' in line.lower():
                self.last_rates['duty_rate'] = rate
            elif 'EFTA' in line:
                self.last_rates['efta'] = rate
            elif 'SG' in line:
                self.last_rates['sg'] = rate
            elif 'USA' in line:
                self.last_rates['usa'] = rate
            return

        # Check for HS code line
        hs_match = re.match(r'^(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})', line)
        if hs_match:
            # Start new entry
            if self.current_entry:
                self.entries.append(self.current_entry.to_dict())
            
            self.current_entry = TariffEntry()
            self.current_entry.chapter = self.current_chapter
            self.current_entry.heading = self.current_heading
            
            code_parts = hs_match.groups()
            self.current_entry.hs_code = ''.join(code_parts)
            self.current_entry.code_format = '.'.join(code_parts)
            
            # Apply last known rates
            self.current_entry.duty_rate = self.last_rates['duty_rate']
            self.current_entry.efta = self.last_rates['efta']
            self.current_entry.sg = self.last_rates['sg']
            self.current_entry.usa = self.last_rates['usa']
            
            # Get description from remainder of line
            remainder = line[hs_match.end():].strip()
            if remainder:
                if self.is_arabic(remainder):
                    self.current_entry.description_ar.append(remainder)
                else:
                    self.current_entry.description_en.append(remainder)
            return

        # If we have a current entry and the line doesn't match any other pattern,
        # it might be a description continuation
        if self.current_entry and not any(x in line for x in ['HEADING', 'H.S CODE', 'DESCRIPTION']):
            if self.is_arabic(line):
                self.current_entry.description_ar.append(line)
            else:
                self.current_entry.description_en.append(line)

    def parse_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.parse_line(line)
        
        # Add the last entry if exists
        if self.current_entry:
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
    
    # Print first few entries with their rates
    print("\nSample entries with rates:")
    for entry in data[:5]:
        print(f"\nHS Code: {entry['hs_code']}")
        print(f"Description (EN): {entry['description_en'][:100]}...")
        print(f"Description (AR): {entry['description_ar'][:100]}...")
        print(f"Duty Rate: {entry['duty_rate']}")
        print(f"EFTA: {entry['efta']}")
        print(f"SG: {entry['sg']}")
        print(f"USA: {entry['usa']}")

def main():
    input_file = "tarfah.txt"
    output_base = "oman_tariff_data_final4"
    
    parser = TariffParser()
    tariff_data = parser.parse_file(input_file)
    save_data(tariff_data, output_base)

if __name__ == "__main__":
    main()