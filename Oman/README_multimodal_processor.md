# Oman Customs Tariff Multimodal Processor

This tool extracts data from the Oman Customs Tariff PDF (`tarfah.pdf`) using OpenAI's multimodal capabilities and processes it page by page into structured JSON format.

## Prerequisites

- Python 3.8+
- OpenAI API key
- Required Python packages:
  - openai
  - pdf2image
  - Pillow
  - PyPDF2
  - poppler-utils (system dependency)

## Installation

1. Install system dependencies:
   ```
   sudo apt-get update
   sudo apt-get install -y poppler-utils
   ```

2. Install required Python packages:
   ```
   pip install openai pdf2image Pillow PyPDF2
   ```

3. Set up your OpenAI API key:
   
   Create a file named `openai_api_key.py` with the following content:
   ```python
   OPENAI_API_KEY = 'your-api-key-here'
   ```
   
   Alternatively, you can set it as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

### Process a specific page

To process a single page of the PDF:

```
python multimodal_tariff_processor.py --page 15
```

### Process a range of pages

To process pages 10 through 20:

```
python multimodal_tariff_processor.py --start 10 --end 20
```

### Process the entire document

To process the entire PDF:

```
python multimodal_tariff_processor.py
```

### Only merge existing results

If you've already processed pages and only want to combine the results:

```
python multimodal_tariff_processor.py --merge-only
```

## Output

The script produces:

1. Individual page images saved to `tarfah_page_images/`
2. JSON results for each page saved to `processed_pages/`
3. A combined JSON file with all entries: `oman_tariff_data_multimodal.json`

## JSON Data Structure

The final JSON output has the following structure:

```json
{
  "document_name": "Oman Customs Tariff",
  "source": "https://www.customs.gov.om/media/idwfzthg/tarfah.pdf",
  "entries": [
    {
      "H.S. Code": "01 01 30 00 00",
      "Description in English": "- Asses",
      "Description in Arabic": "- حمير",
      "Duty Rate": "5%",
      "SFTA": "A",
      "SG": "B", 
      "URA": "C",
      "page_number": 12
    },
    // Additional entries...
  ],
  "metadata": [
    {
      "content": "Chapter 1: Live Animals",
      "page_number": 10
    },
    // Additional metadata...
  ]
}
```

## Troubleshooting

- If you encounter rate limiting issues with the OpenAI API, adjust the `time.sleep()` delay in the code.
- For PDF parsing errors, ensure you have poppler-utils installed correctly.
- If JSON parsing fails, check the raw API response saved in the page result files.