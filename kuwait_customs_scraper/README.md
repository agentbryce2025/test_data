# Kuwait Customs HTS Code Scraper

This project scrapes HTS codes, duty rates, and units from the Kuwait Customs website (https://www.customs.gov.kw/HSCode/HsCode).

## Features

- Uses undetectable-chromedriver to bypass anti-bot detection
- Scrapes complete HTS codes hierarchy (sections -> chapters -> headings -> subheadings)
- Extracts duty rates and units with smart parsing
- Saves intermediate results after each section for data safety
- Comprehensive error logging
- Exports data in both JSON and CSV formats
- Built-in retry mechanisms and proper delays
- Support for proxy configuration

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- Required Python packages (see requirements.txt)

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

4. Install Chrome or Chromium browser:
```bash
# For Ubuntu/Debian:
sudo apt-get update
sudo apt-get install chromium-browser

# For CentOS/RHEL:
sudo yum install chromium

# For Windows/Mac:
Download and install Chrome from https://www.google.com/chrome/
```

## Usage

Run the new implementation:
```bash
cd src
python new_main.py
```

The script will:
1. Start an undetectable Chrome browser
2. Navigate through all sections, chapters, headings, and subheadings
3. Extract HTS codes, descriptions, duty rates, and units
4. Save intermediate results after each section
5. Generate final comprehensive dataset

## Data Structure

The scraper extracts:
```json
{
    "hts_code": "string",
    "duty_rate": "string",
    "unit": "string",
    "raw_duty_text": "string",
    "description": "string",
    "section_id": "string",
    "section_text": "string",
    "chapter_id": "string",
    "chapter_text": "string",
    "heading_id": "string",
    "heading_text": "string",
    "subheading_id": "string",
    "subheading_text": "string"
}
```

## Output Files

- `data/kuwait_customs_data_complete.json`: Final complete dataset in JSON format
- `data/kuwait_customs_data_complete.csv`: Final complete dataset in CSV format
- `data/kuwait_customs_data_section_X_TIMESTAMP.json`: Intermediate results per section
- `data/error_log.txt`: Detailed error log if any issues occur

## Error Handling

- Comprehensive error catching and logging
- Automatic retries for common issues
- Intermediate saves prevent data loss
- Detailed error reporting in error_log.txt

## Proxy Configuration

To use residential proxies, modify undetectable_scraper.py:

```python
def setup_driver(self, headless):
    options = uc.ChromeOptions()
    
    # Add proxy configuration
    options.add_argument(f'--proxy-server=http://your_proxy_address:port')
    # or for SOCKS5
    # options.add_argument(f'--proxy-server=socks5://your_proxy_address:port')
    
    # For authenticated proxies
    proxy_extension = self.create_proxy_extension(
        proxy_host="proxy_host",
        proxy_port="proxy_port",
        proxy_username="username",
        proxy_password="password"
    )
    options.add_extension(proxy_extension)
```

## Best Practices

- Uses undetectable-chromedriver to avoid detection
- Implements smart rate and unit parsing
- Saves intermediate results for data safety
- Proper error handling and logging
- Configurable delays between requests
- Support for proxy configuration