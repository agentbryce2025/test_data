#!/bin/bash

# Install Python requirements
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Make script executable
chmod +x advanced_scraper.py

echo "Setup complete! Run the scraper with: python advanced_scraper.py"
