# Oman Tariff Data Extraction

This project extracts tariff schedule data from the Oman tariff PDF (tarfah.pdf) using Anthropic Claude's OCR capabilities. The extraction process converts the PDF pages into images, sends them to Claude for processing, and combines the results into a structured JSON output.

## Project Structure

- `process_tarfah.py`: Core module for processing PDF pages using Claude API
- `process_batch.py`: Script to process a specific batch of pages
- `process_single_page.py`: Script to process a single page
- `run_all.py`: Main script to orchestrate the entire processing pipeline
- `merge_results.py`: Script to merge all the processed batch results
- `run_process.sh`: Shell script to run the entire process as a background task

## Dependencies

The following Python packages are required:
- anthropic
- pillow
- pdf2image
- PyPDF2
- python-dotenv

## Configuration

The API key is stored in the `.env` file and loaded using python-dotenv. Make sure to add the `.env` file to `.gitignore` to prevent exposing the API key.

## How it Works

1. **PDF Processing**: The PDF is processed in batches to manage memory usage and API rate limits.
2. **OCR with Claude**: Each page is converted to an image and sent to Claude for OCR.
3. **Data Extraction**: Claude extracts the relevant columns: HS_CODE, DESCRIPTION, DUTY_RATE, EFTA, SG, and USA.
4. **Batch Processing**: Results are saved for each batch and then combined into a final output.

## Running the Process

To run the full extraction process:

```bash
./run_process.sh
```

This will start the process in the background and log all output to `processing.log`.

To process a specific batch of pages:

```bash
python3 process_batch.py --start [start_page] --end [end_page]
```

To merge all results after processing:

```bash
python3 merge_results.py
```

## Output Format

The final output is a JSON file containing an array of objects with the following structure:

```json
[
  {
    "HS_CODE": "03 04 59 10 00 00",
    "DESCRIPTION": "- - - Spotted Groupers",
    "DUTY_RATE": "5%",
    "EFTA": "A",
    "SG": "C",
    "USA": "A"
  },
  ...
]
```

## Sample Results

A sample of the extracted data can be found in the `tarfah_ocr_result_10_to_12.json` file. The complete results will be stored in `final_tarfah_ocr_result.json` after processing all pages.

## Notes

- The processing is designed to be memory-efficient and handles rate limiting to avoid API issues.
- Due to the large size of the PDF (309 pages), the full extraction process may take several hours.
- Each page is processed individually to maintain reliable extraction and to recover gracefully from any failures.