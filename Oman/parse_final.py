import re
import pandas as pd
import json

class TariffParser:
    def __init__(self):
        self.data = []
        self.current_chapter = None
        self.current_heading = None
        self.current_description_en = []
        self.current_description_ar = []
        self.current_rates = {'duty': '5%', 'efta': None, 'sg': None, 'usa': None}
        self.last_hs_code = None

    def clean_text(self, text):
        text = re.sub(r'[\u200e\u200f\u202a\u202b\u202c\u202d\u202e]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def is_arabic(self, text):
        return any(ord(c) > 1500 for c in text)

    def is_hs_code(self, text):
        return bool(re.match(r'^\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}', text))

    def parse_line(self, line):
        line = self.clean_text(line)
        if not line:
            return

        # Check for chapter
        chapter_match = re.search(r'Chapter\s+(\d+)', line)
        if chapter_match:
            self.current_chapter = chapter_match.group(1)
            return True

        # Check for heading
        heading_match = re.search(r'(\d{2}\.\d{2})', line)
        if heading_match:
            self.current_heading = heading_match.group(1)
            self.current_description_en = []
            self.current_description_ar = []
            return True

        # Check for rates
        rate_match = re.search(r'(\d+(?:\.\d+)?%)', line)
        if rate_match:
            rate = rate_match.group(1)
            if 'DUTY RATE' in line or 'duty rate' in line.lower():
                self.current_rates['duty'] = rate
            elif 'EFTA' in line:
                self.current_rates['efta'] = rate
            elif 'SG' in line:
                self.current_rates['sg'] = rate
            elif 'USA' in line:
                self.current_rates['usa'] = rate
            return True

        # Check for HS code line
        if self.is_hs_code(line):
            # Get HS code parts
            parts = line.split()[:6]
            hs_code = ''.join(parts)
            code_format = '.'.join(parts)
            
            # Get description from remainder
            desc = ' '.join(line.split()[6:]).strip()
            
            # Store entry
            entry = {
                'chapter': self.current_chapter,
                'heading': self.current_heading,
                'hs_code': hs_code,
                'code_format': code_format,
                'description_en': ' '.join(self.current_description_en),
                'description_ar': ' '.join(self.current_description_ar),
                'duty_rate': self.current_rates['duty'],
                'efta': self.current_rates['efta'],
                'sg': self.current_rates['sg'],
                'usa': self.current_rates['usa']
            }
            
            self.data.append(entry)
            self.last_hs_code = hs_code
            
            # Add remainder as description if any
            if desc:
                if self.is_arabic(desc):
                    self.current_description_ar.append(desc)
                else:
                    self.current_description_en.append(desc)
            
            return True

        # If not any of the above, might be description
        if not any(x in line for x in ['HEADING', 'H.S CODE', 'DESCRIPTION', 'Chapter']):
            if self.is_arabic(line):
                self.current_description_ar.append(line)
            else:
                self.current_description_en.append(line)
            return True

        return False

    def parse_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            current_section = []
            
            for line in f:
                self.parse_line(line)
        
        return self.data

def save_data(data, base_filename):
    # Save as JSON
    json_file = f"{base_filename}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save as CSV
    df = pd.DataFrame(data)
    csv_file = f"{base_filename}.csv"
    df.to_csv(csv_file, index=False)
    
    print(f"Processed {len(data)} entries")
    print(f"Output saved to {json_file} and {csv_file}")
    
    # Print sample entries
    print("\nSample entries:")
    samples = [entry for entry in data[:50] if entry['description_en'] or entry['description_ar']]
    for entry in samples[:3]:
        print("\nHS Code:", entry['hs_code'])
        print("Description (EN):", entry['description_en'][:100])
        print("Description (AR):", entry['description_ar'][:100])
        print("Duty Rate:", entry['duty_rate'])
        print("EFTA:", entry['efta'])
        print("SG:", entry['sg'])
        print("USA:", entry['usa'])

def main():
    parser = TariffParser()
    data = parser.parse_file("tarfah.txt")
    save_data(data, "oman_tariff_final3")

if __name__ == "__main__":
    main()