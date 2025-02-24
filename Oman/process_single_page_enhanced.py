#!/usr/bin/env python3
"""
Process a single page of the Oman Customs Tariff PDF for testing.
This script allows testing the extraction on a specific page before running on the entire document.
"""

import os
import json
import base64
import sys
import re
from pathlib import Path

import openai
from pdf2image import convert_from_path
from PIL import Image

# Define the functions directly to avoid import issues with modifications
def encode_image_to_base64(image_path: str) -> str:
    """Convert an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def save_image(image, page_num):
    """Save an image to disk."""
    image_path = os.path.join(OUTPUT_DIR, f"page_{page_num}.png")
    image.save(image_path)
    return image_path

def extract_table_data_from_image(image_base64: str):
    """Extract table data from an image using OpenAI's vision model."""
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    for attempt in range(MAX_RETRIES):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are a data extraction specialist focusing on Oman's Customs Tariff tables. Your task is to extract ALL columns from the tables with high precision.

                        For each entry in the table, extract these exact fields:
                        - H.S. Code: The tariff code in the rightmost column (e.g., "01.01", "01 01 21 00 10", "25.03")
                        - Description in English: The column with English product descriptions
                        - Description in Arabic: The column with Arabic product descriptions
                        - Duty Rate: The percentage value (e.g., "0%", "5%", "PROHIBITED") - this should ALWAYS go in the Duty Rate field
                        - SFTA: The leftmost indicator column, usually contains A, B, C, etc.
                        - SG: The second indicator column from left
                        - URA: The third indicator column from left (before the duty rate)
                        
                        IMPORTANT RULES:
                        1. Duty Rate should NEVER be placed in the SFTA, SG or URA fields
                        2. The indicator columns (SFTA, SG, URA) should contain only single character values like "A", "B", "+", "-" etc.
                        3. Don't mix up numerical percentages (0%, 5%) with letter indicators (A, B, C)
                        4. Be careful about right-to-left text in the Arabic column
                        5. If a field is empty, use null, not an empty string
                        6. Include ALL lines from the table, including headings and subheadings
                        
                        If a page has section headers, chapter headings, or notes, include those in a separate "metadata" section.
                        
                        Return the data in a structured JSON format with all the fields. Do not include any explanatory text, only the JSON.
                        If a page doesn't contain tariff table data, return an empty entries array with a message.
                        """
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract ALL columns of tariff data from this page of Oman's Customs Tariff document. Return the results as a JSON object with an 'entries' array. Each entry should include the H.S. Code, English description, Arabic description, duty rate, and the SFTA, SG, and URA indicators."
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
            
            # Parse JSON content
            try:
                # First, try to extract JSON from code blocks
                code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
                code_blocks = re.findall(code_block_pattern, content)
                
                if code_blocks:
                    for block in code_blocks:
                        try:
                            return json.loads(block.strip())
                        except json.JSONDecodeError:
                            continue
                
                # Try to find and parse JSON directly
                json_start = content.find('{')
                json_end = content.rfind('}')
                
                if json_start != -1 and json_end != -1:
                    json_str = content[json_start:json_end + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # If the JSON is not valid, try to clean it up
                        cleaned_json = re.sub(r'```json|```', '', json_str).strip()
                        try:
                            return json.loads(cleaned_json)
                        except json.JSONDecodeError:
                            pass
                
                # If all parsing attempts fail, return raw content
                print(f"Content snippet: {content[:200]}...")
                return {"raw_content": content, "parsing_error": "Failed to parse JSON from the response"}
                
            except Exception as e:
                print(f"Error parsing response: {e}")
                return {"raw_content": content, "parsing_error": f"Error parsing response: {str(e)}"}
                
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Error: {e}. Retrying...")
                import time
                time.sleep(RETRY_DELAY)
            else:
                print(f"Failed after {MAX_RETRIES} attempts: {e}")
                return {"error": str(e)}

# Constants
PDF_PATH = "tarfah.pdf"
OUTPUT_DIR = "tarfah_page_images"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Import API key from separate file (not included in git)
try:
    from openai_api_key import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Either set OPENAI_API_KEY environment variable or create an openai_api_key.py file.")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

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