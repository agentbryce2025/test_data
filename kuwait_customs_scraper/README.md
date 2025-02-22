# Kuwait Customs HS Code Scraper

This project is a web scraper for the Kuwait Customs HS Code system (https://www.customs.gov.kw/HSCode/HsCode). It extracts HS codes, descriptions, and duty rates from the Kuwait Customs website.

## Features

- Scrapes HS codes hierarchically (Sections → Chapters → Headings → Subheadings)
- Handles both Arabic and English content
- Implements proper delays between requests
- Saves data in both JSON and CSV formats
- Uses Selenium WebDriver for robust web interaction
- Includes logging for debugging and monitoring

## Requirements

- Python 3.8+
- Firefox Browser
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/agentbryce2025/test_data.git
   cd test_data/kuwait_customs_scraper
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script:
```bash
python src/main.py
```

The script will:
1. Start a Firefox browser in headless mode
2. Navigate through all sections and chapters
3. Extract HS codes, descriptions, and duty rates
4. Save the data in both JSON and CSV formats in the data directory

## Data Structure

The scraper extracts the following information:
- Section (2-digit code)
- Chapter (2-digit code)
- HS Code (up to 12 digits)
- Description
- Duty Rate

## Output Files

- `data/kuwait_customs_data.json`: Contains the raw data in JSON format
- `data/kuwait_customs_data.csv`: Contains the data in CSV format

## Notes

- The scraper implements proper delays between requests to avoid overwhelming the server
- It uses the English interface version of the website
- The system is based on the 2022 HS edition and GCC Unified Customs Tariff (January 2025)

## Error Handling

The scraper includes comprehensive error handling and logging:
- All exceptions are caught and logged
- The browser is properly closed even if an error occurs
- Failed requests are logged for debugging

## Best Practices

- Implements proper delays between requests
- Uses headless browser mode for efficiency
- Includes comprehensive logging
- Follows the hierarchical structure of HS codes
- Handles session management