# Oman Tariff Data Extraction Results

## Summary
This document provides an overview of the extraction results from the Oman Customs Tariff PDF document using our multimodal AI extraction pipeline.

## Extraction Overview
- **Source document**: `tarfah.pdf` (Oman Customs Tariff)
- **Pages processed**: 6 pages (1-5, 10)
- **Entries extracted**: 46 tariff entries
- **Unique HS codes**: 45
- **Data quality**: All entries have duty rates and proper structure

## Output Files
- **Raw extraction**: `oman_tariff_data_multimodal.json`
- **Cleaned data**: `oman_tariff_data_multimodal_cleaned.json`
- **Final dataset**: `oman_tariff_final_extraction.json`

## Data Format
Each entry in the dataset includes:
- **H.S. Code**: The harmonized system tariff code
- **Description in English**: Product description in English
- **Description in Arabic**: Product description in Arabic
- **Duty Rate**: The applicable tariff rate (e.g., "0%", "5%", "PROHIBITED")
- **SFTA**, **SG**, **URA**: Special indicator columns
- **page_number**: The page number in the original document

## Sample Entries

```json
{
  "H.S. Code": "01 01",
  "Description in English": "Live horses, asses, mules and hinnies.",
  "Description in Arabic": "خيول وحمير وبغال ونغال حية.",
  "Duty Rate": "0%",
  "SFTA": null,
  "SG": null,
  "URA": null,
  "page_number": 1
}
```

```json
{
  "H.S. Code": "01 06 31 00 00 01",
  "Description in English": "Falcon",
  "Description in Arabic": "الصقر",
  "Duty Rate": "0%",
  "SFTA": "A",
  "SG": "+",
  "URA": "B",
  "page_number": 3
}
```

## Extraction Methodology
1. Each page of the PDF was converted to an image
2. The image was processed using GPT-4o's multimodal capabilities
3. Data was extracted into a structured JSON format
4. Post-processing was applied to clean and normalize the data
5. All page results were combined into a single dataset

## Next Steps
To process the entire document (all 309 pages), run:
```bash
python run_tariff_extraction.py
```

This will extract data from all pages and produce a comprehensive dataset of the entire Oman Customs Tariff.