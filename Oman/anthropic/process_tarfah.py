import os
import json
import time
import base64
import concurrent.futures
from typing import Dict, List, Any
import logging
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from pdf2image import convert_from_path
from PIL import Image
import io
import random
import dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv.load_dotenv('/home/computeruse/test_data/Oman/anthropic/.env')

# Get API key from environment
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
PDF_PATH = '/home/computeruse/test_data/Oman/tarfah.pdf'
OUTPUT_DIR = '/home/computeruse/test_data/Oman/anthropic'
MAX_WORKERS = 5  # Limit concurrency to prevent rate limiting
MODEL = 'claude-3-7-sonnet-20250219'

def encode_image_to_base64(img):
    """Convert PIL Image to base64 encoded string"""
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def process_page(page_num: int, image) -> Dict[str, Any]:
    """Process a single page with the Claude API"""
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Encode the image
        base64_image = encode_image_to_base64(image)
        
        # Prepare the prompt for Claude
        prompt = f"""
        This image shows a page from a tariff schedule. Extract the data into a JSON array of objects with the following properties:
        "HS_CODE", "DESCRIPTION", "DUTY_RATE", "EFTA", "SG", "USA"
        
        Notes:
        - Extract all rows visible in this tariff table.
        - HS_CODE is usually formatted as numbers with dots (e.g., 01.01, 0101.21.00)
        - DESCRIPTION contains product descriptions
        - DUTY_RATE is usually a percentage
        - EFTA, SG, and USA columns contain preferential rates or exemption codes
        - If a field is empty or not applicable, use an empty string ""
        - Make sure to return a valid JSON array of objects
        
        ONLY RESPOND WITH THE JSON AND NO OTHER TEXT!!!
        """
        
        # Make the API call
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_image}}
                    ]
                }
            ]
        )
        
        # Get the response text
        response_text = response.content[0].text.strip()
        
        # If the response starts with ``` and ends with ```, strip those out
        if response_text.startswith('```') and response_text.endswith('```'):
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            else:
                response_text = response_text[3:-3].strip()
                
        try:
            # Try to parse the response as JSON
            result = json.loads(response_text)
            logger.info(f"Successfully processed page {page_num}")
            return {"page": page_num, "data": result}
        except json.JSONDecodeError:
            # Try to fix common JSON issues
            # Sometimes the response might have comments or trailing commas
            try:
                # Remove potential trailing commas before closing brackets
                response_text = response_text.replace(',]', ']').replace(',}', '}')
                result = json.loads(response_text)
                logger.info(f"Successfully processed page {page_num} after fixing JSON")
                return {"page": page_num, "data": result}
            except json.JSONDecodeError:
                # If still not valid JSON, return the raw text
                logger.warning(f"Response for page {page_num} was not valid JSON. Raw response: {response_text[:100]}...")
                return {"page": page_num, "error": "Invalid JSON response", "raw_response": response_text}
            
    except Exception as e:
        logger.error(f"Error processing page {page_num}: {str(e)}")
        return {"page": page_num, "error": str(e)}

def process_single_page(pdf_path: str, output_dir: str, page_num: int):
    """Process a single page of the PDF"""
    try:
        # Convert specific page of PDF to image
        images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
        
        if not images:
            logger.error(f"No image generated for page {page_num}")
            return None
        
        # Process the page
        result = process_page(page_num, images[0])
        
        # Save individual page result
        output_file = os.path.join(output_dir, f"page_{page_num}_result.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=4)
        
        logger.info(f"Saved result for page {page_num} to {output_file}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing page {page_num}: {str(e)}")
        return {"page": page_num, "error": str(e)}

def process_pdf(pdf_path: str, output_dir: str, start_page: int = 1, end_page: int = None):
    """Process PDF pages sequentially or with limited parallelism"""
    try:
        # Determine total pages in the PDF
        import PyPDF2
        pdf = PyPDF2.PdfReader(pdf_path)
        total_pages = len(pdf.pages)
        logger.info(f"PDF has {total_pages} pages")
        
        # Set end_page to total_pages if not specified
        if end_page is None or end_page > total_pages:
            end_page = total_pages
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        # Process pages with limited concurrency to avoid memory issues
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit tasks for each page in the range
            future_to_page = {
                executor.submit(process_single_page, pdf_path, output_dir, page_num): page_num
                for page_num in range(start_page, end_page + 1)
            }
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    logger.info(f"Completed processing page {page_num}/{end_page}")
                    
                    # Random backoff to avoid rate limiting
                    time.sleep(random.uniform(2.0, 5.0))
                    
                except Exception as e:
                    logger.error(f"Error with page {page_num}: {str(e)}")
        
        # Combine results for the processed range
        combine_results(output_dir, start_page, end_page)
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return []

def combine_results(output_dir: str, start_page: int, end_page: int):
    """Combine results from multiple pages into a single file"""
    all_data = []
    
    for page_num in range(start_page, end_page + 1):
        result_file = os.path.join(output_dir, f"page_{page_num}_result.json")
        if os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                    
                if "data" in result:
                    if isinstance(result["data"], list):
                        all_data.extend(result["data"])
                    elif isinstance(result["data"], dict) and "rows" in result["data"]:
                        all_data.extend(result["data"]["rows"])
            except Exception as e:
                logger.error(f"Error processing result file for page {page_num}: {str(e)}")
    
    # Save the combined result
    output_file = os.path.join(output_dir, f"tarfah_ocr_result_{start_page}_to_{end_page}.json")
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4)
    
    logger.info(f"Combined results saved to {output_file}")
    return all_data

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Process pages in ranges to handle large PDFs efficiently
    # Start with first 50 pages as a sample
    process_pdf(PDF_PATH, OUTPUT_DIR, start_page=1, end_page=50)