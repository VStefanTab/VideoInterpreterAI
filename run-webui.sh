#!/bin/bash

# Check if the virtual environment directory exists
if [ ! -d "venv" ]; then
  echo "Error: 'venv' directory not found. Please set up the virtual environment first."
  exit 1
fi

# Activate the virtual environment
source venv/bin/activate

python run.py