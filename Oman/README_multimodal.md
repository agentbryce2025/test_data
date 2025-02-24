# Oman Tariff Data Multimodal Processing

This project processes the Oman Customs Tariff PDF (tarfah.pdf) using OpenAI's multimodal vision model to extract structured table data and convert it to JSON format.

## Overview

The Oman Customs Tariff document contains tariff codes, product descriptions, duty rates, and other information in tabular format. This script processes the PDF page by page, uses AI vision capabilities to extract the tabular data, and compiles it into a structured JSON file.

## Requirements

- Python 3.8+
- OpenAI API key
- Required Python packages:
  - openai
  - pdf2image
  - pillow
  - tqdm
- Poppler (for pdf2image)

## Installation

1. Install Python dependencies:
```bash
pip install openai pdf2image pillow tqdm
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

Run the script:

```bash
python process_tariff_multimodal.py
```

By default, the script processes all pages of the PDF. To process specific pages, modify the `PAGES_TO_PROCESS` variable in the script:

```python
PAGES_TO_PROCESS = (1, 10)  # Process only pages 1-10
```

## Output

The script produces:

1. Page images in the `tarfah_page_images` directory
2. A JSON file `oman_tariff_data_multimodal.json` containing the extracted data

## Data Structure

The output JSON file contains an array of objects, with each object representing data from one page. Each page object contains:

- `page_number`: The page number in the PDF
- `entries`: An array of tariff entries, where each entry contains:
  - `hs_code`: The Harmonized System code
  - `description`: The product description
  - `duty_rate`: The applicable duty rate
  - Additional fields as available in the document

## Notes

- The script handles rate limiting by adding delays between API calls
- Retry logic is included to handle temporary API failures
- For best results, ensure the PDF is high quality and tables are clearly visible