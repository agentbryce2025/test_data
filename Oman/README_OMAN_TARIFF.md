# Oman Tariff Data Extraction

This project extracts structured data from the Oman Customs Tariff PDF document using multimodal AI capabilities.

## Overview

The Oman Customs Tariff document (`tarfah.pdf`) contains detailed tables of tariff information in both English and Arabic. This project provides tools to:

1. Process the PDF page by page using OpenAI's multimodal capabilities
2. Extract structured data from the tables
3. Clean and normalize the extracted data
4. Combine results into a comprehensive JSON dataset

## Source Data

- **Original Document**: [Oman Customs Tariff (PDF)](https://www.customs.gov.om/media/idwfzthg/tarfah.pdf)
- **Format**: Bilingual (English/Arabic) tables with tariff codes, descriptions, and duty rates

## Repository Structure

```
Oman/
├── tarfah.pdf                          # Source PDF document
├── multimodal_tariff_processor.py      # Main PDF processing script
├── postprocess_tariff_data.py          # Data cleaning and normalization
├── run_tariff_extraction.py            # End-to-end extraction script
├── processed_pages/                    # Individual page extraction results
├── tarfah_page_images/                 # Converted page images
├── oman_tariff_data_multimodal.json    # Raw combined extraction results
├── oman_tariff_data_multimodal_cleaned.json # Cleaned final dataset
└── README_OMAN_TARIFF.md               # This documentation
```

## Data Structure

The extracted data is structured as follows:

```json
{
  "document_name": "Oman Customs Tariff",
  "source": "https://www.customs.gov.om/media/idwfzthg/tarfah.pdf",
  "entries": [
    {
      "H.S. Code": "01 01 21 00 00",
      "Description in English": "Pure-bred breeding animals:",
      "Description in Arabic": "حيوانات طافرة نقية للتناسل:",
      "Duty Rate": "0%",
      "SFTA": "B",
      "SG": "A",
      "URA": null,
      "page_number": 1
    },
    // Additional entries...
  ],
  "metadata": [
    {
      "content": "Chapter 1: Live animals",
      "page_number": 1
    },
    // Additional metadata...
  ],
  "statistics": {
    "total_entries": 8,
    "entries_with_duty_rate": 5,
    "unique_hs_codes": 8,
    "pages_processed": 1
  }
}
```

## Installation

1. Ensure you have Python 3.8+ installed
2. Install required dependencies:

```bash
pip install openai pdf2image Pillow PyPDF2
```

3. System dependencies:

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils
```

4. Set up your OpenAI API key in `openai_api_key.py`:

```python
OPENAI_API_KEY = 'your-api-key-here'
```

## Usage

### Process the entire document

```bash
python run_tariff_extraction.py
```

### Process a specific range of pages

```bash
python run_tariff_extraction.py --start 10 --end 20
```

### Run a quick demo (pages 1-5 only)

```bash
python run_tariff_extraction.py --demo
```

### Process a single page

```bash
python multimodal_tariff_processor.py --page 15
```

### Only run post-processing on existing data

```bash
python postprocess_tariff_data.py
```

## Processing Pipeline

1. **PDF Conversion**: Each PDF page is converted to an image
2. **Multimodal Analysis**: The image is analyzed using OpenAI's GPT-4o model
3. **Data Extraction**: Structured data is extracted from the tables
4. **Post-processing**: The data is cleaned, normalized and validated
5. **Combination**: All page results are combined into a single dataset

## Error Handling

- The extraction process includes retry logic for API failures
- The post-processing phase includes validation and correction of common extraction errors
- Each page is processed independently to prevent complete failure if a single page fails

## Performance Considerations

- Processing the entire document (~300 pages) will take several hours and consume significant API credits
- The script processes pages in batches to manage memory and API rate limits
- For testing, use the `--demo` flag or process a small range of pages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.