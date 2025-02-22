# Kuwait Customs HTS Code Scraper

This project scrapes HTS codes, duty rates, and units from the Kuwait Customs website (https://www.customs.gov.kw/HSCode/HsCode).

## Features

- Multiple scraping methods (BeautifulSoup and Selenium-based)
- Scrapes complete HTS codes hierarchy (sections -> chapters -> headings -> subheadings)
- Extracts duty rates and units with smart parsing
- Saves intermediate results after each section for data safety
- Comprehensive error logging
- Built-in retry mechanisms and proper delays
- Support for both headless and GUI browser operation

## Requirements

- Python 3.8+
- Required Python packages (see requirements.txt)
- For Selenium scraper: Firefox browser and geckodriver

## Installation

1. Clone the repository:
```bash
git clone https://github.com/agentbryce2025/test_data.git
cd test_data/kuwait_customs_scraper
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Install required browsers:
```bash
# For Ubuntu/Debian:
sudo apt-get update
sudo apt-get install firefox-esr chromium-browser

# For Firefox Selenium scraper - Install geckodriver
curl -L https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux-aarch64.tar.gz -o geckodriver.tar.gz
tar xf geckodriver.tar.gz
sudo mv geckodriver /usr/local/bin/
sudo chmod +x /usr/local/bin/geckodriver

# Note: The recommended undetected-chromedriver will automatically handle Chromium/Chrome setup
```

## Usage

There are three different scrapers available:

1. Firefox Selenium Scraper (Recommended):
```bash
python src/run_full_scraper.py
```
- Uses Selenium with Firefox
- Stable and reliable
- Most thoroughly tested

2. Undetected Chrome Scraper (Experimental):
```bash
python src/run_undetected_scraper.py
```
- Uses undetected-chromedriver
- May require additional setup
- Still in development

3. BeautifulSoup Scraper (Limited):
```bash
python src/run_bs4_scraper.py
```
- Uses requests and BeautifulSoup4
- Currently blocked by website security
- For reference only

Both scrapers will:
1. Navigate through sections, chapters, headings, and subheadings
2. Extract HTS codes, descriptions, duty rates, and units
3. Save intermediate results after each section
4. Generate timestamped output files

## Data Structure

The scrapers extract:
```json
{
    "hts_code": "string",
    "description": "string",
    "duty_rate": "string",
    "unit": "string"
}
```

## Output Files

- `data/kuwait_customs_data_TIMESTAMP.json`: Complete dataset in JSON format
- `data/scraper_TIMESTAMP.log`: Detailed log file

## Error Handling

- Comprehensive error catching and logging
- Automatic retries for common issues
- Intermediate saves prevent data loss
- Detailed error reporting in log files

## Best Practices

- Multiple scraping methods for reliability
- Smart rate limiting to avoid server overload
- Regular progress saving
- Detailed logging for debugging
- Configurable parameters for customization

## Development

The project includes two main scraping approaches:

1. `bs4_scraper.py`: Uses requests and BeautifulSoup4 for a lightweight approach
2. `full_scraper.py`: Uses Selenium for browser automation

Both implementations share similar features:
- Progress tracking
- Error handling
- Data validation
- Regular saving