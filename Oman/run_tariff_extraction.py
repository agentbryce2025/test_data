#!/usr/bin/env python3
"""
Run the complete Oman Tariff extraction process:
1. Process PDF pages with multimodal_tariff_processor.py
2. Post-process and clean data with postprocess_tariff_data.py
"""

import os
import sys
import argparse
import subprocess
import time

def run_command(command):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    """Main function to run the entire process."""
    parser = argparse.ArgumentParser(description="Run complete Oman Tariff extraction")
    parser.add_argument("--start", type=int, default=1, help="Starting page number")
    parser.add_argument("--end", type=int, help="Ending page number (default: process all pages)")
    parser.add_argument("--batch-size", type=int, default=10, help="Number of pages to process in each batch (default: 10)")
    parser.add_argument("--demo", action="store_true", help="Demo mode - only process pages 1-5")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip extraction phase, only run post-processing")
    args = parser.parse_args()

    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    multimodal_script = os.path.join(script_dir, "multimodal_tariff_processor.py")
    postprocess_script = os.path.join(script_dir, "postprocess_tariff_data.py")
    
    # Make scripts executable
    os.chmod(multimodal_script, 0o755)
    os.chmod(postprocess_script, 0o755)

    # Demo mode - just process first 5 pages
    if args.demo:
        args.start = 1
        args.end = 5
        args.batch_size = 5

    # Process PDF pages
    if not args.skip_extraction:
        if args.end:
            # Process pages in batches to manage memory and API rate limits
            for batch_start in range(args.start, args.end + 1, args.batch_size):
                batch_end = min(batch_start + args.batch_size - 1, args.end)
                print(f"\n=== Processing pages {batch_start} to {batch_end} ===")
                
                cmd = [sys.executable, multimodal_script, "--start", str(batch_start), "--end", str(batch_end)]
                output = run_command(cmd)
                
                if output:
                    print("Batch completed successfully")
                else:
                    print("Error processing batch")
                
                # Wait between batches to avoid rate limiting
                if batch_end < args.end:
                    print(f"Waiting 10 seconds before next batch...")
                    time.sleep(10)
        else:
            # Process all pages (let the script determine the total)
            cmd = [sys.executable, multimodal_script]
            output = run_command(cmd)
            
            if not output:
                print("Error processing pages")
                return
    else:
        print("Skipping extraction phase as requested")
    
    # Post-process data
    print("\n=== Post-processing extracted data ===")
    cmd = [sys.executable, postprocess_script]
    output = run_command(cmd)
    
    if output:
        print("Post-processing completed successfully")
    else:
        print("Error during post-processing")

if __name__ == "__main__":
    main()