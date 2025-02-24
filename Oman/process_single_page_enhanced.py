#!/usr/bin/env python3
"""
Process a single page of the Oman Customs Tariff PDF for testing.
This script allows testing the extraction on a specific page before running on the entire document.
"""

import os
import json
import base64
import sys
from pathlib import Path

import openai
from pdf2image import convert_from_path
from PIL import Image

# Import the processing functions from the main script
from process_tariff_multimodal_enhanced import (
    encode_image_to_base64,
    extract_table_data_from_image,
    save_image
)

# Import API key from separate file (not included in git)
try:
    from openai_api_key import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Either set OPENAI_API_KEY environment variable or create an openai_api_key.py file.")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

# Constants
PDF_PATH = "tarfah.pdf"
OUTPUT_DIR = "tarfah_page_images"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_single_page(pdf_path: str, page_num: int) -> dict:
    """Process a single page of the PDF."""
    print(f"Processing page {page_num} of {pdf_path}...")
    
    try:
        # Convert PDF page to image
        images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
        if not images:
            print(f"Error: No image generated for page {page_num}")
            return {"error": "No image generated"}
        
        # Save the image
        image_path = save_image(images[0], page_num)
        print(f"Image saved to {image_path}")
        
        # Convert image to base64
        image_base64 = encode_image_to_base64(image_path)
        
        # Extract data
        page_data = extract_table_data_from_image(image_base64)
        
        # Add page number to the data
        page_data["page_number"] = page_num
        
        # Save the result to a JSON file
        output_file = f"page_{page_num}_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to {output_file}")
        return page_data
    
    except Exception as e:
        print(f"Error processing page {page_num}: {e}")
        return {"error": str(e)}

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python process_single_page_enhanced.py PAGE_NUMBER")
        sys.exit(1)
    
    try:
        page_num = int(sys.argv[1])
    except ValueError:
        print("Error: PAGE_NUMBER must be an integer")
        sys.exit(1)
    
    pdf_path = os.path.join(os.path.dirname(__file__), PDF_PATH)
    process_single_page(pdf_path, page_num)

if __name__ == "__main__":
    main()