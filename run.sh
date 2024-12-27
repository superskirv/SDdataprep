#!/bin/bash

# Create a new virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies from requirements.txt file
pip install -r requirements.txt

# Run the python script
python3 dataprep.py
