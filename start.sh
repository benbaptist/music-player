#!/bin/bash

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv

    # Install dependencies
    pip3 install -r requirements.txt
fi

# Activate virtual environment
source .venv/bin/activate

# Run the application
python3 run.py