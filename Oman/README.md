# Oman Customs Tariff Data Extraction

This folder contains scripts to parse and extract data from Oman's Customs Tariff PDF document, with both traditional parsing methods and an advanced multimodal AI approach.

## Source Data

The data is sourced from the official Oman Customs website:
https://www.customs.gov.om/media/idwfzthg/tarfah.pdf

## Approaches

### 1. Traditional Parsing (Original Approach)

- `parse_tariff_final2.py`: Python script to parse the tariff PDF and extract structured data
- `tarfah.txt`: Converted text version of the PDF
- `oman_tariff_data_final2.csv`: Parsed data in CSV format
- `oman_tariff_data_final2.json`: Parsed data in JSON format

### 2. Multimodal AI Approach (New)

This new approach uses OpenAI's GPT-4o model to directly extract structured data from PDF images.

- `process_tariff_multimodal.py`: Main script to process the entire PDF
- `process_single_page.py`: Utility to process single pages
- `merge_page_results.py`: Tool to merge results from multiple pages
- `test_processing.py`: Script for testing the extraction on a few pages

## Data Structure

### Traditional Parsing Output
- Heading: The HS code heading (e.g., "01.01")
- HS Code: The full 12-digit HS code
- Code Format: The HS code with dots for better readability
- Description: Product description
- Duty Rate: The applicable duty rate

### Multimodal AI Output
- H.S. Code: The tariff code
- Description: Product description in English
- Duty Rate: The applicable duty rate percentage

## Usage

### Traditional Parser
```bash
pip install pandas
python3 parse_tariff_final2.py
```

### Multimodal AI Approach
```bash
# Install dependencies
pip install openai pdf2image pillow tqdm

# Set up API key in openai_api_key.py or as an environment variable

# Process the entire PDF
python process_tariff_multimodal.py

# Or process a single page
python process_single_page.py 42  # Process page 42

# Merge multiple page results
python merge_page_results.py
```

## Sample Results

Sample extraction results are available in the `tarfah_page_images` directory, showing the page images and extracted JSON data.

## Requirements

- Python 3.8+
- OpenAI API key (for multimodal approach)
- Poppler (for PDF-to-image conversion)
- Required Python packages (see installation instructions above)