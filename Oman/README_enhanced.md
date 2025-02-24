# Enhanced Oman Tariff Data Multimodal Processing

This project processes the Oman Customs Tariff PDF (tarfah.pdf) using OpenAI's GPT-4o model with multimodal capabilities to extract all columns of the table data and convert it to structured JSON format.

## Overview

The Oman Customs Tariff document contains tariff codes, product descriptions in both English and Arabic, duty rates, and other indicators (SFTA, SG, URA) in tabular format. This enhanced script processes the PDF page by page, uses AI vision capabilities to extract all columns of the tabular data, and compiles it into a structured JSON file.

## Features

- Extracts all data columns from the tariff document:
  - H.S. Code (tariff code)
  - English Description
  - Arabic Description
  - Duty Rate
  - SFTA, SG, and URA indicators
- Processes pages in batches to handle large PDFs efficiently
- Includes error handling and retry logic
- Post-processes the data to standardize and clean it
- Exports to both JSON and CSV formats for easy integration with other tools

## Requirements

- Python 3.8+
- OpenAI API key
- Required Python packages:
  - openai
  - pdf2image
  - pillow
  - tqdm
  - pandas (for post-processing)
- Poppler (for pdf2image)

## Installation

1. Install Python dependencies:
```bash
pip install openai pdf2image pillow tqdm pandas
```

2. Install Poppler (required for pdf2image):

   - On Ubuntu/Debian:
   ```bash
   sudo apt-get install poppler-utils
   ```

   - On macOS:
   ```bash
   brew install poppler
   ```

   - On Windows, download the binaries from: https://github.com/oschwartz10612/poppler-windows/releases

3. Place your OpenAI API key in one of the following:
   - Create a file named `openai_api_key.py` with the content:
     ```python
     OPENAI_API_KEY = 'your-api-key-here'
     ```
   - Set an environment variable:
     ```bash
     export OPENAI_API_KEY='your-api-key-here'
     ```

4. Ensure the tarfah.pdf file is in the same directory as the script.

## Usage

### Full Processing

Run the main processing script:

```bash
python process_tariff_multimodal_enhanced.py
```

By default, the script processes all pages of the PDF. To process specific pages, modify the `PAGES_TO_PROCESS` variable in the script:

```python
PAGES_TO_PROCESS = (1, 10)  # Process only pages 1-10
```

### Testing on a Single Page

To test the extraction on a single page before running it on the entire document:

```bash
python process_single_page_enhanced.py 5  # Process page 5
```

### Post-Processing

After running the main extraction script, you can clean and standardize the data:

```bash
python post_process_tariff_data.py
```

## Output

The scripts produce:

1. Page images in the `tarfah_page_images` directory
2. Raw extracted JSON in `oman_tariff_data_multimodal_enhanced.json`
3. Cleaned JSON in `oman_tariff_final_cleaned.json`
4. CSV export in `oman_tariff_final_cleaned.csv`

## Data Structure

The output JSON file contains an array of objects, where each object represents a tariff entry with:

- `hs_code`: The Harmonized System code
- `description_en`: The product description in English
- `description_ar`: The product description in Arabic
- `duty_rate`: The applicable duty rate
- `sfta`: The SFTA indicator
- `sg`: The SG indicator
- `ura`: The URA indicator
- `page_number`: The page number in the PDF

## Notes

- The script handles rate limiting by adding delays between API calls
- Retry logic is included to handle temporary API failures
- For best results, ensure the PDF is high quality and tables are clearly visible
- The post-processing script helps standardize field names and clean the data