#!/bin/bash

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
else
    # Activate virtual environment
    source .venv/bin/activate
    
    # Update dependencies if needed
    if [ "$1" == "--update" ]; then
        echo "Updating dependencies..."
        pip3 install -r requirements.txt
    fi
fi

# Run the application
echo "Starting music player..."
python3 run.py