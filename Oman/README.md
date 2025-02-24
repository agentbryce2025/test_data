# Oman Customs Tariff Data Scraper

This folder contains scripts to parse and extract data from Oman's Customs Tariff PDF document.

## Source Data

The data is sourced from the official Oman Customs website:
https://www.customs.gov.om/media/idwfzthg/tarfah.pdf

## Files

- `parse_tariff_final2.py`: Python script to parse the tariff PDF and extract structured data
- `tarfah.pdf`: Original source PDF file
- `tarfah.txt`: Converted text version of the PDF
- `oman_tariff_data_final2.csv`: Parsed data in CSV format
- `oman_tariff_data_final2.json`: Parsed data in JSON format

## Data Structure

The extracted data includes:
- Heading: The HS code heading (e.g., "01.01")
- HS Code: The full 12-digit HS code
- Code Format: The HS code with dots for better readability
- Description: Product description
- Duty Rate: The applicable duty rate

## Usage

1. Ensure you have the required Python packages installed:
```bash
pip install pandas
```

2. Run the script:
```bash
python3 parse_tariff_final2.py
```

The script will generate both CSV and JSON output files containing the structured tariff data.