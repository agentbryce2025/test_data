#!/bin/bash

# Script to run the OCR processing as a background task
LOG_FILE="/home/computeruse/test_data/Oman/anthropic/processing.log"

echo "Starting OCR processing at $(date)" > "$LOG_FILE"
cd /home/computeruse/test_data/Oman/anthropic

# Run the processing script, redirecting all output to the log file
nohup python3 run_all.py >> "$LOG_FILE" 2>&1 &

echo "Process started with PID $! - Check $LOG_FILE for progress"