#!/usr/bin/env python3
"""
Multimodal Oman Tariff Data Processor

This script processes the Oman Customs Tariff PDF (tarfah.pdf) page by page, 
extracting data from tables using OpenAI's multimodal capabilities and 
converting it to structured JSON format.
"""

import os
import sys
import json
import base64
import time
import argparse
import re
from pathlib import Path

import openai
from pdf2image import convert_from_path
from PIL import Image

# Constants
PDF_PATH = "tarfah.pdf"
OUTPUT_DIR = "tarfah_page_images"
RESULTS_DIR = "processed_pages"
FINAL_OUTPUT = "oman_tariff_data_multimodal.json"

# Create output directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Import API key from separate file (not included in git)
try:
    from openai_api_key import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Either set OPENAI_API_KEY environment variable or create an openai_api_key.py file.")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

def encode_image_to_base64(image_path: str) -> str:
    """Convert an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def save_image(image, page_num):
    """Save an image to disk."""
    image_path = os.path.join(OUTPUT_DIR, f"page_{page_num}.png")
    image.save(image_path)
    return image_path

def extract_table_data_from_image(image_base64: str, page_num: int):
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
                                "text": f"Extract ALL columns of tariff data from page {page_num} of Oman's Customs Tariff document. Return the results as a JSON object with an 'entries' array. Each entry should include the H.S. Code, English description, Arabic description, duty rate, and the SFTA, SG, and URA indicators."
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
                time.sleep(RETRY_DELAY)
            else:
                print(f"Failed after {MAX_RETRIES} attempts: {e}")
                return {"error": str(e)}

def process_page(pdf_path: str, page_num: int) -> dict:
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
        page_data = extract_table_data_from_image(image_base64, page_num)
        
        # Add page number to the data
        page_data["page_number"] = page_num
        
        # Save the result to a JSON file
        output_file = os.path.join(RESULTS_DIR, f"page_{page_num}_result.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to {output_file}")
        return page_data
    
    except Exception as e:
        print(f"Error processing page {page_num}: {e}")
        return {"error": str(e)}

def count_pdf_pages(pdf_path: str) -> int:
    """Count the number of pages in the PDF."""
    try:
        from PyPDF2 import PdfReader
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)
    except Exception as e:
        print(f"Error counting PDF pages: {e}")
        # Fallback method using pdf2image
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, dpi=72, first_page=1, last_page=None)
        return len(images)

def merge_results(results_dir: str, output_file: str):
    """Merge all page results into a single JSON file."""
    print(f"Merging results from {results_dir}...")
    
    all_data = {
        "document_name": "Oman Customs Tariff",
        "source": "https://www.customs.gov.om/media/idwfzthg/tarfah.pdf",
        "entries": [],
        "metadata": []
    }
    
    # Get all result files
    result_files = sorted([f for f in os.listdir(results_dir) if f.startswith("page_") and f.endswith("_result.json")], 
                         key=lambda x: int(x.split("_")[1]))
    
    # Merge data
    for result_file in result_files:
        page_num = int(result_file.split("_")[1])
        file_path = os.path.join(results_dir, result_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
                
            # Add page entries to all_data with page number
            if "entries" in page_data and isinstance(page_data["entries"], list):
                for entry in page_data["entries"]:
                    entry["page_number"] = page_num
                    all_data["entries"].append(entry)
            
            # Add metadata
            if "metadata" in page_data and isinstance(page_data["metadata"], list):
                for meta in page_data["metadata"]:
                    all_data["metadata"].append({
                        "content": meta,
                        "page_number": page_num
                    })
                    
        except Exception as e:
            print(f"Error processing {result_file}: {e}")
    
    # Save merged data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"Merged data saved to {output_file}")
    return all_data

def process_range(pdf_path: str, start_page: int, end_page: int):
    """Process a range of pages from the PDF."""
    for page_num in range(start_page, end_page + 1):
        process_page(pdf_path, page_num)
        # Add a delay to avoid rate limiting
        time.sleep(1)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process Oman Customs Tariff PDF")
    parser.add_argument("--page", type=int, help="Process a specific page only")
    parser.add_argument("--start", type=int, default=1, help="Starting page number")
    parser.add_argument("--end", type=int, help="Ending page number")
    parser.add_argument("--merge-only", action="store_true", help="Only merge existing results")
    args = parser.parse_args()
    
    pdf_path = os.path.join(os.path.dirname(__file__), PDF_PATH)
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)
    
    # Count pages if end page not specified
    if args.end is None and not args.page and not args.merge_only:
        args.end = count_pdf_pages(pdf_path)
        print(f"PDF has {args.end} pages")
    
    # Process pages
    if args.merge_only:
        print("Skipping processing, merging existing results only")
    elif args.page:
        process_page(pdf_path, args.page)
    else:
        process_range(pdf_path, args.start, args.end)
    
    # Merge results
    merge_results(RESULTS_DIR, FINAL_OUTPUT)

if __name__ == "__main__":
    main()