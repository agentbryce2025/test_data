#!/usr/bin/env python3
"""
Multimodal processing of Oman's Customs Tariff PDF (tarfah.pdf)
This script processes the PDF page by page, extracts table data using OpenAI's vision model,
and converts the extracted data to JSON format.
"""

import os
import json
import base64
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import shutil

import openai
from pdf2image import convert_from_path
from PIL import Image
import io
from tqdm import tqdm

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
OUTPUT_JSON = "oman_tariff_data_multimodal.json"
PAGES_TO_PROCESS = None  # Set to None to process all pages, or specify a range like (1, 5)
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def encode_image_to_base64(image_path: str) -> str:
    """Convert an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def convert_pil_to_base64(pil_image):
    """Convert a PIL Image to base64 string."""
    buffered = io.BytesIO()
    pil_image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extract_table_data_from_image(image_base64: str) -> Dict[str, Any]:
    """
    Extract table data from an image using OpenAI's vision model.
    
    Args:
        image_base64: Base64 encoded image
        
    Returns:
        Extracted table data as a dictionary
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are a data extraction specialist. Your task is to extract structured data from 
                        Oman's Customs Tariff tables. The table contains information about tariff codes, 
                        descriptions, duty rates, and other data.
                        
                        For each entry in the table, extract:
                        - H.S. Code (the tariff code)
                        - Description (in English)
                        - Duty Rate (percentage)
                        - Any additional codes or identifiers present
                        
                        Return the data in a structured JSON format. Do not include explanatory text, only the JSON.
                        If a page doesn't contain tariff table data, return an empty object with a message.
                        """
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all tariff data from this page of Oman's Customs Tariff document. Return the results as a JSON array of entries. Each entry should include the tariff code, description, duty rate, and any additional codes present."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
            
            # Extract content from API response
            content = response.choices[0].message.content
            
            # Find JSON data in the response
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            if json_start != -1 and json_end != -1:
                json_str = content[json_start:json_end + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # If the response isn't valid JSON, try to extract JSON array
                    array_start = content.find('[')
                    array_end = content.rfind(']')
                    if array_start != -1 and array_end != -1:
                        json_str = content[array_start:array_end + 1]
                        try:
                            return {"entries": json.loads(json_str)}
                        except json.JSONDecodeError:
                            pass
            
            # If no valid JSON found, return the raw content
            return {"raw_content": content}
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Error: {e}. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Failed after {MAX_RETRIES} attempts: {e}")
                return {"error": str(e)}

def save_image(image, page_num):
    """Save an image to disk."""
    image_path = os.path.join(OUTPUT_DIR, f"page_{page_num}.png")
    image.save(image_path)
    return image_path

def process_pdf(pdf_path: str, page_range: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Process PDF page by page, extract table data using the vision model.
    
    Args:
        pdf_path: Path to the PDF file
        page_range: Optional tuple (start_page, end_page) to process specific pages
        
    Returns:
        List of dictionaries containing extracted data from each page
    """
    print(f"Converting PDF to images...")
    try:
        # Convert PDF to list of PIL images
        images = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF: {e}")
        # Try with lower DPI
        try:
            print("Retrying with lower DPI...")
            images = convert_from_path(pdf_path, dpi=100)
        except Exception as e2:
            print(f"Failed to convert PDF: {e2}")
            return []
    
    total_pages = len(images)
    print(f"Total pages in PDF: {total_pages}")
    
    # Determine which pages to process
    start_page, end_page = 1, total_pages
    if page_range:
        start_page, end_page = page_range
        start_page = max(1, start_page)
        end_page = min(total_pages, end_page)
    
    all_data = []
    
    # Process each page
    for i in tqdm(range(start_page-1, end_page), desc="Processing pages", unit="page"):
        page_num = i + 1
        print(f"\nProcessing page {page_num}/{end_page}...")
        
        # Save the image temporarily
        image_path = save_image(images[i], page_num)
        
        # Convert image to base64
        image_base64 = encode_image_to_base64(image_path)
        
        # Extract data
        page_data = extract_table_data_from_image(image_base64)
        
        # Add page number to the data
        page_data["page_number"] = page_num
        
        # Save to the list
        all_data.append(page_data)
        
        # To avoid rate limiting
        time.sleep(0.5)
    
    return all_data

def main():
    """Main function to process the PDF and save results."""
    pdf_path = os.path.join(os.path.dirname(__file__), PDF_PATH)
    
    # Process the PDF
    print(f"Processing {pdf_path}...")
    results = process_pdf(pdf_path, PAGES_TO_PROCESS)
    
    # Save the results
    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_JSON)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Processing complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()