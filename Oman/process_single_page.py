#!/usr/bin/env python3
"""
Process a single page of the Oman Customs Tariff PDF using OpenAI's multimodal model.
Useful for testing or when processing very large documents page by page.
"""

import os
import json
import base64
import argparse
from pathlib import Path
import openai
from pdf2image import convert_from_path

# Import API key from separate file (not included in git)
try:
    from openai_api_key import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Either set OPENAI_API_KEY environment variable or create an openai_api_key.py file.")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

def encode_image_to_base64(image_path):
    """Convert an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_data_from_image(image_base64):
    """Extract table data using the OpenAI vision model."""
    response = openai.chat.completions.create(
        model="gpt-4-vision",
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
                        "text": "Extract all tariff data from this page of Oman's Customs Tariff document. Return the results as a JSON array of entries."
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
    
    content = response.choices[0].message.content
    
    # Try to extract JSON content
    json_start = content.find('{')
    json_end = content.rfind('}')
    
    if json_start != -1 and json_end != -1:
        json_str = content[json_start:json_end + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If not valid JSON, try to find array
            array_start = content.find('[')
            array_end = content.rfind(']')
            if array_start != -1 and array_end != -1:
                json_str = content[array_start:array_end + 1]
                try:
                    return {"entries": json.loads(json_str)}
                except json.JSONDecodeError:
                    pass
    
    # Return raw content if no valid JSON found
    return {"raw_content": content}

def process_single_page(pdf_path, page_num, output_dir):
    """Process a single page from the PDF."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert the page to image
    print(f"Converting page {page_num} to image...")
    images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
    
    if not images:
        print(f"Error: Failed to convert page {page_num} to image.")
        return None
    
    # Save the image
    image_path = os.path.join(output_dir, f"page_{page_num}.png")
    images[0].save(image_path)
    print(f"Saved image to {image_path}")
    
    # Convert to base64
    image_base64 = encode_image_to_base64(image_path)
    
    # Extract data
    print(f"Extracting data from page {page_num}...")
    page_data = extract_data_from_image(image_base64)
    
    # Add page number
    page_data["page_number"] = page_num
    
    # Save JSON result
    output_json = os.path.join(output_dir, f"page_{page_num}_data.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, ensure_ascii=False, indent=2)
    
    print(f"Saved data to {output_json}")
    return page_data

def main():
    parser = argparse.ArgumentParser(description="Process a single page from the Oman Tariff PDF")
    parser.add_argument("page_num", type=int, help="Page number to process")
    parser.add_argument("--pdf", default="tarfah.pdf", help="Path to the PDF file")
    parser.add_argument("--output", default="tarfah_page_images", help="Output directory")
    args = parser.parse_args()
    
    pdf_path = os.path.join(os.path.dirname(__file__), args.pdf)
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
    
    process_single_page(pdf_path, args.page_num, args.output)

if __name__ == "__main__":
    main()