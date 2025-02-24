import re
import pandas as pd
import json

def process_file(filename):
    def clean_text(text):
        text = re.sub(r'[\u200e\u200f\u202a\u202b\u202c\u202d\u202e]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def is_arabic(text):
        return any(ord(c) > 1500 for c in text)

    data = []
    current_rates = {'duty': None, 'efta': None, 'sg': None, 'usa': None}
    current_desc_en = []
    current_desc_ar = []
    current_chapter = None
    current_heading = None

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = clean_text(lines[i])
        
        # Skip empty lines
        if not line:
            i += 1
            continue

        # Look for chapter
        chapter_match = re.search(r'Chapter\s+(\d+)', line)
        if chapter_match:
            current_chapter = chapter_match.group(1)
            i += 1
            continue

        # Look for heading
        heading_match = re.search(r'(\d{2}\.\d{2})', line)
        if heading_match:
            current_heading = heading_match.group(1)
            i += 1
            continue

        # Check for rates
        if '%' in line:
            rate = re.search(r'(\d+(?:\.\d+)?%)', line).group(1)
            if 'DUTY RATE' in line:
                current_rates['duty'] = rate
            elif 'EFTA' in line:
                current_rates['efta'] = rate
            elif 'SG' in line:
                current_rates['sg'] = rate
            elif 'USA' in line:
                current_rates['usa'] = rate
            i += 1
            continue

        # Look for HS code lines
        hs_match = re.match(r'^(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})', line)
        if hs_match:
            # Get code parts
            code_parts = hs_match.groups()
            hs_code = ''.join(code_parts)
            code_format = '.'.join(code_parts)
            
            # Get description from remainder of line
            remainder = line[hs_match.end():].strip()
            
            # Look ahead for description lines
            desc_en = []
            desc_ar = []
            
            if remainder:
                if is_arabic(remainder):
                    desc_ar.append(remainder)
                else:
                    desc_en.append(remainder)
            
            # Look ahead for more description lines
            j = i + 1
            while j < len(lines):
                next_line = clean_text(lines[j])
                if not next_line or re.match(r'^\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}', next_line):
                    break
                if is_arabic(next_line):
                    desc_ar.append(next_line)
                else:
                    desc_en.append(next_line)
                j += 1
            
            # Create entry
            entry = {
                'chapter': current_chapter,
                'heading': current_heading,
                'hs_code': hs_code,
                'code_format': code_format,
                'description_en': ' '.join(desc_en),
                'description_ar': ' '.join(desc_ar),
                'duty_rate': current_rates['duty'],
                'efta': current_rates['efta'],
                'sg': current_rates['sg'],
                'usa': current_rates['usa']
            }
            data.append(entry)
            
            i = j  # Skip processed description lines
            continue
        
        i += 1

    return data

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
    for entry in data[:3]:
        print("\nHS Code:", entry['hs_code'])
        print("Description (EN):", entry['description_en'][:100])
        print("Description (AR):", entry['description_ar'][:100])
        print("Duty Rate:", entry['duty_rate'])
        print("EFTA:", entry['efta'])
        print("SG:", entry['sg'])
        print("USA:", entry['usa'])

def main():
    input_file = "tarfah.txt"
    output_base = "oman_tariff_final"
    
    data = process_file(input_file)
    save_data(data, output_base)

if __name__ == "__main__":
    main()