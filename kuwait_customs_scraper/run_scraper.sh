#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if required packages are installed
pip install -r requirements.txt

# Run the scraper
python src/improved_scraper.py

# Check if scraping was successful
if [ -f "data/kuwait_hts_data.json" ]; then
    echo "Scraping completed successfully. Data saved in data/kuwait_hts_data.json"
else
    echo "Error: Scraping failed. Check scraper.log for details."
fi